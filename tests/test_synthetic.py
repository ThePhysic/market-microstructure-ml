import csv
import hashlib
import json

import numpy as np
import pandas as pd
import pytest

from market_microstructure.acquisition import HEADER_FIELDS
from market_microstructure.data import ingest_files
from market_microstructure.features import build_samples
from market_microstructure.synthetic import PROVIDER, generate_fixture


DATES = ["2020-01-01", "2020-02-01", "2020-03-01"]


def test_same_seed_reproduces_csv_and_manifest_bytes_across_directories(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    a = generate_fixture(first, dates=DATES, seed=42)
    b = generate_fixture(second, dates=list(reversed(DATES)), seed=42)
    assert a == b
    for name in [entry.name for entry in first.iterdir()]:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    before = {entry.name: entry.read_bytes() for entry in first.iterdir()}
    assert generate_fixture(first, dates=DATES, seed=42) == a
    assert before == {entry.name: entry.read_bytes() for entry in first.iterdir()}


def test_different_seed_changes_fixture_without_claiming_market_data(tmp_path):
    first = generate_fixture(tmp_path / "a", dates=DATES, seed=1)
    second = generate_fixture(tmp_path / "b", dates=DATES, seed=2)
    assert first[0]["sha256"] != second[0]["sha256"]
    for manifest in first:
        assert manifest["synthetic"] is True
        assert manifest["provider"] == PROVIDER
        assert manifest["market_evidence"] is False
        assert "retrieval_url" not in manifest
        assert "response_url" not in manifest


def test_tardis_schema_timestamps_units_prices_and_hashes_are_explicit(tmp_path):
    manifests = generate_fixture(tmp_path, dates=[DATES[0]], rows_per_date=50)
    manifest = manifests[0]
    path = tmp_path / manifest["path"]
    payload = path.read_bytes()
    assert hashlib.sha256(payload).hexdigest() == manifest["sha256"] == manifest["excerpt_sha256"]
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == HEADER_FIELDS
        rows = list(reader)
    assert len(rows) == 50
    receives = [int(row["local_timestamp"]) for row in rows]
    assert receives == sorted(receives)
    assert len(set(receives)) < len(receives)
    assert all(pd.Timestamp(value, unit="us", tz="UTC").date().isoformat() == DATES[0] for value in receives)
    for row in rows:
        bids = [float(row[f"bids[{level}].price"]) for level in range(5)]
        asks = [float(row[f"asks[{level}].price"]) for level in range(5)]
        assert bids[0] < asks[0]
        assert all(bids[i] > bids[i+1] for i in range(4))
        assert all(asks[i] < asks[i+1] for i in range(4))
        assert all(price > 0 and price * 2 == int(price * 2) for price in bids + asks)
        assert all(float(row[f"{side}[{level}].amount"]) > 0 for side in ("asks", "bids") for level in range(5))


def test_fixture_passes_ingestion_and_causal_sample_pipeline(tmp_path):
    manifests = generate_fixture(tmp_path, dates=DATES)
    paths = [tmp_path / entry["path"] for entry in manifests]
    normalized, quality = ingest_files(paths, manifests=manifests)
    assert len(normalized) == 900
    assert quality["excluded_rows"] == 0
    assert quality["segments"] == 3
    samples, columns, feature_quality = build_samples(normalized)
    assert len(samples) == 810
    assert set(samples["target"].unique()) == {-1, 0, 1}
    assert np.isfinite(samples[columns]).all().all()
    assert feature_quality["excluded_samples"] == 90
    assert samples["label_session_date"].eq(samples["session_date"]).all()


def test_companion_manifests_are_usable_without_explicit_manifest_argument(tmp_path):
    manifests = generate_fixture(tmp_path, dates=[DATES[0]])
    normalized, quality = ingest_files([tmp_path / manifests[0]["path"]])
    assert len(normalized) == 300
    assert quality["per_file"][0]["manifest_verified"] is True
    aggregate = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert aggregate == manifests


@pytest.mark.parametrize("arguments", [
    {"dates": []}, {"dates": "2020-01-01"}, {"dates": [DATES[0], DATES[0]]},
    {"dates": ["2020-1-1"]}, {"dates": ["not-a-date"]}, {"dates": ["1999-12-31"]},
    {"dates": DATES, "rows_per_date": 0}, {"dates": DATES, "rows_per_date": True},
    {"dates": DATES, "rows_per_date": 3.5}, {"dates": DATES, "rows_per_date": 20_001},
    {"dates": DATES, "seed": -1}, {"dates": DATES, "seed": True},
    {"dates": DATES, "seed": 2**32},
])
def test_invalid_arguments_fail_before_creating_output(tmp_path, arguments):
    output = tmp_path / "uncreated"
    with pytest.raises(ValueError):
        generate_fixture(output, **arguments)
    assert not output.exists()


def test_existing_real_or_unverifiable_manifest_is_never_overwritten(tmp_path):
    original = '[{"provider": "Tardis.dev", "synthetic": false}]'
    (tmp_path / "manifest.json").write_text(original, encoding="utf-8")
    with pytest.raises(ValueError, match="non-synthetic"):
        generate_fixture(tmp_path, dates=DATES)
    assert (tmp_path / "manifest.json").read_text(encoding="utf-8") == original
    assert not list(tmp_path.glob("*.csv"))


def test_existing_modified_fixture_is_not_silently_repaired(tmp_path):
    manifests = generate_fixture(tmp_path, dates=DATES)
    path = tmp_path / manifests[0]["path"]
    path.write_bytes(path.read_bytes() + b"corrupted")
    with pytest.raises(ValueError, match="differs"):
        generate_fixture(tmp_path, dates=DATES)
    assert path.read_bytes().endswith(b"corrupted")
