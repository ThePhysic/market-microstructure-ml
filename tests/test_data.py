"""Synthetic source rows cover attribution, integrity and segment boundaries."""
import csv
from datetime import datetime, timezone

import numpy as np
import pytest

from market_microstructure.acquisition import HEADER_FIELDS, sha256_file
from market_microstructure.data import DataIntegrityError, ingest_files


BASE = 1577836800000000


def row(index=0, *, timestamp=None, size=10):
    record = {
        "exchange": "deribit", "symbol": "BTC-PERPETUAL",
        "timestamp": str(BASE+index*1000 if timestamp is None else timestamp),
        "local_timestamp": str(BASE+index*1000 if timestamp is None else timestamp),
    }
    for level in range(5):
        record[f"asks[{level}].price"] = str(100.5+level*.5)
        record[f"bids[{level}].price"] = str(100-level*.5)
        record[f"asks[{level}].amount"] = str(size+index)
        record[f"bids[{level}].amount"] = str(size+index+1)
    return record


def write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_normalization_provenance_ties_and_dtypes(tmp_path):
    a, b = row(0), row(1)
    b["local_timestamp"] = a["local_timestamp"]
    path = write(tmp_path/"2020-01-01.csv", [a,b])
    manifest = {"path":path.name, "date":"2020-01-01", "sha256":sha256_file(path)}
    states, quality = ingest_files([path], manifests=[manifest])
    assert states.source_row_position.tolist() == [1,2]
    assert states.source_order.tolist() == [1,2]
    assert states.receive_time_us.dtype == np.dtype("int64")
    assert states.bid_price_1.dtype == np.dtype("float64")
    assert states.provenance_key.tolist() == [f"{manifest['sha256']}:1", f"{manifest['sha256']}:2"]
    assert quality["counts"]["tied_receive_timestamps"] == 1
    assert quality["retained_rows"] == 2
    assert quality["per_file"][0]["manifest_verified"] is True


@pytest.mark.parametrize("field,value,reason", [
    ("timestamp", "1577836800000", "timestamp_unit_or_range"),
    ("bids[0].price", "0", "nonpositive_price"),
    ("asks[0].price", "100", "crossed_or_locked_book"),
    ("bids[1].price", "100", "unsorted_or_duplicate_price_levels"),
    ("asks[4].amount", "", "depth_insufficiency_or_missing_value"),
    ("bids[3].amount", "-1", "negative_amount"),
    ("asks[2].price", "NaN", "nonfinite_book_value"),
    ("bids[2].price", "not-a-number", "unparsable_book_value"),
    ("symbol", "WRONG", "market_mismatch"),
])
def test_invalid_rows_are_attributed_and_break_segments(tmp_path, field, value, reason):
    bad = row(1)
    bad[field] = value
    path = write(tmp_path/"2020-01-01.csv", [row(0),bad,row(2)])
    states, quality = ingest_files([path])
    assert states.source_row_position.tolist() == [1,3]
    assert states.segment_id.iloc[0] != states.segment_id.iloc[1]
    assert quality["total_rows"] == 3
    assert quality["excluded_rows"] == 1
    assert quality["exclusion_counts"][reason] == 1
    assert quality["exclusions"][0]["source_row_position"] == 2


def test_receive_regression_high_watermark_is_not_sorted_away(tmp_path):
    rows = [row(0,timestamp=BASE+x) for x in (0,20000,10000,15000,25000)]
    path = write(tmp_path/"2020-01-01.csv", rows)
    states, quality = ingest_files([path])
    assert states.source_row_position.tolist() == [1,2,5]
    assert states.receive_time_us.is_monotonic_increasing
    assert quality["exclusion_counts"]["receive_time_before_high_watermark"] == 2
    assert states.segment_id.iloc[-1] != states.segment_id.iloc[0]


def test_duplicate_rows_excluded_but_new_timestamps_retained(tmp_path):
    first, later = row(), row(1)
    for name in HEADER_FIELDS[4:]:
        later[name] = first[name]
    path = write(tmp_path/"2020-01-01.csv", [first,dict(first),later])
    states, quality = ingest_files([path])
    assert states.source_row_position.tolist() == [1,3]
    assert quality["counts"]["duplicate_rows"] == 1
    assert quality["counts"]["repeated_book_payloads"] == 1
    assert states.segment_id.nunique() == 2


def test_gap_date_and_file_boundaries_are_explicit(tmp_path):
    path = write(tmp_path/"2020-01-01.csv", [row(),row(1,timestamp=BASE+31_000_000)])
    later_base = int(datetime(2020,2,1,tzinfo=timezone.utc).timestamp()*1_000_000)
    later = write(tmp_path/"2020-02-01.csv", [row(1,timestamp=later_base)])
    states, quality = ingest_files([later,path], gap_seconds=30)
    assert states.session_date.tolist() == ["2020-01-01","2020-01-01","2020-02-01"]
    assert states.segment_id.nunique() == 3
    assert quality["counts"]["gaps"] == 1


def test_zero_size_recorded_and_checksum_corruption_rejected(tmp_path):
    zero = row()
    for name in HEADER_FIELDS:
        if name.endswith(".amount"):
            zero[name] = "0"
    path = write(tmp_path/"2020-01-01.csv", [zero])
    states, quality = ingest_files([path])
    assert len(states) == 1
    assert quality["counts"]["zero_amount_cells"] == 10
    with pytest.raises(DataIntegrityError, match="SHA-256"):
        ingest_files([path], manifests=[{"path":path.name,"sha256":"0"*64}])


def test_wrong_schema_duplicate_paths_bad_csv_and_empty_arguments_fail(tmp_path):
    path = tmp_path/"2020-01-01.csv"
    path.write_text("wrong,schema\n1,2\n")
    with pytest.raises(DataIntegrityError, match="schema"):
        ingest_files([path])
    write(path,[row()])
    with pytest.raises(DataIntegrityError, match="same source path"):
        ingest_files([path,path])
    with pytest.raises(DataIntegrityError, match="At least one"):
        ingest_files([])
    with path.open("a") as handle:
        handle.write('\"unclosed\n')
    with pytest.raises(DataIntegrityError, match="Malformed CSV"):
        ingest_files([path])


def test_all_invalid_rows_produce_typed_empty_frame_and_full_attribution(tmp_path):
    invalid = row()
    invalid["timestamp"] = "wrong"
    states, quality = ingest_files([write(tmp_path/"2020-01-01.csv",[invalid])])
    assert states.empty
    assert states.receive_time_us.dtype == np.dtype("int64")
    assert quality["total_rows"] == quality["excluded_rows"] == 1
