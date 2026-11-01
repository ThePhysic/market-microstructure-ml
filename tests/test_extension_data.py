"""Independent synthetic books only; tests never request historical data."""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from market_microstructure.acquisition import AcquisitionError, HEADER_FIELDS
from market_microstructure.data import DataIntegrityError
from market_microstructure.extension.acquisition import (
    DEFAULT_WINDOWS, download_day, download_days, source_url, validate_selection,
)
from market_microstructure.extension.coverage import summarize_coverage
from market_microstructure.extension.storage import (
    iter_normalized_batches, iter_state_batches, load_states, read_state_store,
    validate_states, write_state_store,
)


def source_bytes(date="2021-01-01", events=None):
    base = int(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp()) * 1_000_000
    if events is None:
        events = [(s + offset, {}) for s in DEFAULT_WINDOWS for offset in range(0, 900, 5)]
        events += [(1800, {}), (900, {}), (86_399, {})]
        events.sort(key=lambda event: event[0])
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(HEADER_FIELDS)
    for second, changes in events:
        row = {"exchange": "bitstamp", "symbol": "BTCUSD", "timestamp": base + int(second * 1_000_000),
               "local_timestamp": base + int(second * 1_000_000)}
        for level in range(5):
            row.update({f"asks[{level}].price": f"{101 + level}.01", f"asks[{level}].amount": "0.01234567",
                        f"bids[{level}].price": f"{100 - level}.01", f"bids[{level}].amount": "0.02345678"})
        row.update(changes)
        writer.writerow([row[key] for key in HEADER_FIELDS])
    return gzip.compress(stream.getvalue().encode(), mtime=0)


class Response(io.BytesIO):
    def __init__(self, data, *, status=206, headers=None, truncate=0):
        super().__init__(data[:len(data) - truncate] if truncate else data)
        self.status = status
        self.headers = {"Content-Range": f"bytes 0-{len(data)-1}/{len(data)}", "Content-Length": str(len(data)),
                        "x-md5": hashlib.md5(data, usedforsecurity=False).hexdigest(), **(headers or {})}

    def geturl(self):
        return "https://storage.example/source?secret=DO_NOT_RECORD"


def opener_for(data, **response_kwargs):
    return lambda *args, **kwargs: Response(data, **response_kwargs)


@pytest.fixture
def acquired(tmp_path):
    manifest = download_day("2021-01-01", tmp_path / "raw", opener=opener_for(source_bytes()))
    return tmp_path / "raw", manifest


def test_complete_source_crc_md5_and_all_intraday_windows(acquired):
    raw, manifest = acquired
    assert manifest["complete_source_gzip"] and manifest["gzip_crc_verified"] and manifest["provider_md5_verified"]
    assert manifest["retained_rows"] == 8 * 180
    assert manifest["source_total_rows"] == 8 * 180 + 3
    assert len(manifest["source_row_ranges"]) == 8
    assert manifest["selection"]["window_starts_utc_seconds"] == list(DEFAULT_WINDOWS)
    assert all(q["retained_rows"] == 180 for q in manifest["window_coverage"])
    assert manifest["response_url_without_query"] == "https://storage.example/source"
    assert "DO_NOT_RECORD" not in json.dumps(manifest)
    assert list(csv.reader((raw / manifest["path"]).read_text().splitlines()))[0] == HEADER_FIELDS


def test_half_open_windows_do_not_include_end_or_intervening_state(tmp_path):
    data = source_bytes(events=[(0, {}), (899.999999, {}), (900, {}), (10799, {}), (10800, {}), (11700, {})])
    m = download_day("2021-01-01", tmp_path, opener=opener_for(data))
    assert m["retained_rows"] == 3
    assert [(r["source_row_start"], r["source_row_end"]) for r in m["source_row_ranges"]] == [(1, 2), (5, 5)]


def test_existing_probe_reused_without_network(tmp_path):
    prior = tmp_path / "probe.gz"
    data = source_bytes()
    prior.write_bytes(data)
    def no_network(*args, **kwargs):
        raise AssertionError("Reused feasibility source must not download again")
    m = download_day("2021-01-01", tmp_path / "raw", existing_gzip=prior,
                     expected_compressed_sha256=hashlib.sha256(data).hexdigest(),
                     expected_source_bytes=len(data), opener=no_network)
    assert m["bytes_received"] == 0 and m["source_compressed_bytes"] == len(data)
    assert m["reused_feasibility_gzip"] and m["gzip_crc_verified"]


def test_probe_reuse_requires_exact_preverified_hash(tmp_path):
    prior = tmp_path / "probe.gz"
    prior.write_bytes(source_bytes())
    with pytest.raises(AcquisitionError, match="previously verified checksum"):
        download_day("2021-01-01", tmp_path / "raw", existing_gzip=prior, expected_compressed_sha256="0" * 64)


@pytest.mark.parametrize("date", ["2020-01-01", "2025-01-01", "2021-01-02", "2021-1-01", "bad"])
def test_only_reviewed_free_spot_dates(date):
    with pytest.raises(AcquisitionError):
        source_url(date)


@pytest.mark.parametrize("windows,duration", [([], 900), ([0, 0], 900), ([3, 0], 1), ([0, 1], 2), ([86399], 2), ([-1], 1), ([0.5], 1), ([0], 0)])
def test_invalid_window_selection(windows, duration):
    with pytest.raises(AcquisitionError):
        validate_selection(windows, duration)


@pytest.mark.parametrize("kwargs", [
    {"headers": {"Content-Range": "bytes 0-99/999999"}},
    {"headers": {"Content-Range": "bytes 5-99/100"}},
    {"headers": {"Content-Encoding": "gzip"}},
    {"headers": {"x-md5": "0" * 32}},
    {"truncate": 8}, {"status": 403},
])
def test_no_partial_or_ambiguous_source_fallback(tmp_path, kwargs):
    with pytest.raises(AcquisitionError):
        download_day("2021-01-01", tmp_path, opener=opener_for(source_bytes(), **kwargs))
    assert not list(tmp_path.glob("*.csv"))
    assert not list(tmp_path.glob("*.part"))


def test_crc_corruption_is_rejected_even_without_md5(tmp_path):
    data = bytearray(source_bytes()); data[-8] ^= 1
    with pytest.raises(AcquisitionError):
        download_day("2021-01-01", tmp_path, opener=opener_for(bytes(data), headers={"x-md5": ""}))
    assert not list(tmp_path.glob("*.manifest.json"))


def test_bounded_decoding_and_transfer(tmp_path):
    data = source_bytes()
    with pytest.raises(AcquisitionError, match="compressed or disk budget"):
        download_day("2021-01-01", tmp_path / "compressed", max_compressed_bytes=10, opener=opener_for(data))
    with pytest.raises(AcquisitionError, match="Decoded source"):
        download_day("2021-01-01", tmp_path / "decoded", max_decompressed_bytes=500, opener=opener_for(data))
    with pytest.raises(AcquisitionError, match="disk budget"):
        download_day("2021-01-01", tmp_path / "disk", max_new_disk_bytes=len(data) + 500, opener=opener_for(data))
    with pytest.raises(AcquisitionError, match="wall-clock"):
        download_day("2021-01-01", tmp_path / "deadline", deadline=time.monotonic() - 1, opener=opener_for(data))


def test_cached_artifacts_validate_contract_and_both_hashes(acquired):
    raw, manifest = acquired
    assert download_day("2021-01-01", raw, opener=lambda *a, **k: pytest.fail("network")) == manifest
    with pytest.raises(AcquisitionError, match="different frozen selection"):
        download_day("2021-01-01", raw, windows=[0])
    (raw / manifest["path"]).write_bytes(b"altered selected source")
    with pytest.raises(AcquisitionError, match="checksum mismatch"):
        download_day("2021-01-01", raw)


def test_aggregate_budget_rejects_before_network(tmp_path):
    with pytest.raises(AcquisitionError, match="aggregate transfer"):
        download_days(["2021-01-01"], tmp_path, max_total_compressed_bytes=100, expected_source_sizes={"2021-01-01": 101})
    with pytest.raises(AcquisitionError, match="unique dates"):
        download_days(["2021-01-01"] * 2, tmp_path)
    with pytest.raises(AcquisitionError, match="exactly all selected"):
        download_days(["2021-01-01"], tmp_path, expected_source_sizes={})


def test_source_catalogue_size_changes_stop_before_source_body(tmp_path):
    with pytest.raises(AcquisitionError, match="size changed"):
        download_day("2021-01-01", tmp_path, expected_source_bytes=1, opener=opener_for(source_bytes()))


def test_multiple_dates_keep_original_row_positions_and_global_order(tmp_path):
    dates = ["2021-02-01", "2021-01-01"]
    def opened(request, **kwargs):
        date = "2021-02-01" if "/02/" in request.full_url else "2021-01-01"
        return Response(source_bytes(date))
    manifests = download_days(dates, tmp_path, opener=opened)
    frame, quality = load_states(manifests, tmp_path)
    assert len(frame) == 2 * 1440 and quality["excluded_rows"] == 0
    assert frame["segment_id"].nunique() == 16
    assert (frame["source_order"].diff().dropna() > 0).all()
    assert frame["source_order"].iloc[180] == 183  # two unselected source events are not renumbered away.
    assert frame["source_order"].iloc[1440] == 1444  # full first source has 1,443 rows.
    assert frame["source_row_position"].iloc[1440] == 1
    assert all(key.startswith(manifests[0]["compressed_sha256"] + ":") for key in frame["provenance_key"].iloc[:1440])


@pytest.mark.parametrize("batch_rows", [1, 37, 180, 181, 10000])
def test_chunked_normalization_matches_unchunked_at_all_boundaries(acquired, batch_rows):
    raw, manifest = acquired
    expected, _ = load_states([manifest], raw)
    batches = list(iter_normalized_batches([manifest], raw, batch_rows=batch_rows))
    pd.testing.assert_frame_equal(pd.concat([f for f, _ in batches], ignore_index=True), expected)
    assert sum(q is not None for _, q in batches) == 1
    assert all(len(f) <= batch_rows for f, _ in batches)


def test_tied_times_keep_source_order_and_invalid_state_breaks_segment(tmp_path):
    events = [(0, {}), (1, {}), (1, {"asks[0].amount": "0.1"}),
              (2, {"bids[0].price": "999"}), (3, {}), (4, {}), (5, {})]
    m = download_day("2021-01-01", tmp_path, opener=opener_for(source_bytes(events=events)))
    frame, quality = load_states([m], tmp_path)
    assert frame["source_row_position"].tolist() == [1, 2, 3, 5, 6, 7]
    assert frame["receive_time_us"].iloc[1] == frame["receive_time_us"].iloc[2]
    assert frame["segment_id"].iloc[2] != frame["segment_id"].iloc[3]
    assert quality["exclusions"][0]["source_row_position"] == 4
    assert quality["exclusion_counts"]["crossed_or_locked_book"] == 1


def test_source_row_mapping_tampering_and_gzip_corruption_fail(acquired):
    raw, manifest = acquired
    bad = json.loads(json.dumps(manifest)); bad["source_row_ranges"][1]["selected_row_start"] += 1
    with pytest.raises(DataIntegrityError, match="mapping"):
        load_states([bad], raw)
    (raw / manifest["gzip_path"]).write_bytes(b"corrupt")
    with pytest.raises(DataIntegrityError, match="gzip checksum"):
        load_states([manifest], raw)


def test_objective_coverage_all_dates_windows_and_edge_thresholds(acquired):
    raw, manifest = acquired
    frame, _ = load_states([manifest], raw)
    coverage = summarize_coverage(frame, [manifest])
    assert coverage["eligible"] and coverage["windows"] == 8
    assert all(w["segments_with_at_least_31_states"] == 1 for w in coverage["per_date"][0]["windows"])
    partial = frame.iloc[50:].reset_index(drop=True)
    failed = summarize_coverage(partial, [manifest])
    assert not failed["eligible"]
    assert "window_edge_coverage" in failed["per_date"][0]["windows"][0]["reasons"]
    assert "excluded_fraction" in failed["per_date"][0]["reasons"]


def test_coverage_missing_date_never_redefines_date_set(acquired):
    raw, manifest = acquired
    frame, _ = load_states([manifest], raw)
    other = json.loads(json.dumps(manifest)); other["date"] = "2021-02-01"
    with pytest.raises(DataIntegrityError, match="dates differ"):
        summarize_coverage(frame, [manifest, other])


def test_local_state_store_roundtrip_order_precision_and_corruption(acquired, tmp_path):
    raw, manifest = acquired
    frame, _ = load_states([manifest], raw)
    metadata = write_state_store(frame, tmp_path / "store", batch_rows=137)
    actual = read_state_store(tmp_path / "store")
    pd.testing.assert_frame_equal(actual, frame)
    assert len(metadata["chunks"]) == 11
    first = tmp_path / "store" / metadata["chunks"][0]["path"]
    first.write_bytes(b"altered")
    with pytest.raises(DataIntegrityError, match="checksum"):
        read_state_store(tmp_path / "store")


def test_order_regression_duplicate_provenance_and_precision_loss_rejected(acquired):
    raw, manifest = acquired
    frame, _ = load_states([manifest], raw)
    for key in ["source_order", "receive_time_us", "provenance_key"]:
        changed = frame.copy()
        changed.loc[1, key] = changed.loc[0, key] if key != "receive_time_us" else changed.loc[0, key] - 1
        with pytest.raises(DataIntegrityError):
            validate_states(changed)
    changed = frame.copy(); changed["receive_time_us"] = changed["receive_time_us"].astype(float)
    with pytest.raises(DataIntegrityError, match="integer precision"):
        list(iter_state_batches(changed))


@pytest.mark.parametrize("key,value", [("bid_price_1", 999), ("ask_price_2", 1), ("bid_size_1", -1), ("ask_size_5", float("nan"))])
def test_local_store_refuses_malformed_normalized_books(acquired, tmp_path, key, value):
    raw, manifest = acquired
    frame, _ = load_states([manifest], raw)
    frame.loc[0, key] = value
    with pytest.raises(DataIntegrityError, match="Malformed normalized"):
        write_state_store(frame, tmp_path / "malformed")


def test_local_store_path_traversal_rejected(acquired, tmp_path):
    raw, manifest = acquired
    frame, _ = load_states([manifest], raw)
    write_state_store(frame, tmp_path / "store")
    path = tmp_path / "store" / "manifest.json"
    metadata = json.loads(path.read_text()); metadata["chunks"][0]["path"] = "../outside.npz"
    path.write_text(json.dumps(metadata))
    with pytest.raises(DataIntegrityError, match="basename"):
        read_state_store(tmp_path / "store")
