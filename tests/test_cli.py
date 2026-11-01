import json
from pathlib import Path
import shutil

import pytest
from threadpoolctl import threadpool_limits

import market_microstructure.acquisition as acquisition
import market_microstructure.experiment as experiment
from market_microstructure.cli import _data_contract, load_sources, main
from market_microstructure.config import ResearchConfig
from market_microstructure.synthetic import generate_fixture


DATES = tuple(f"2020-{month:02d}-01" for month in range(1, 9))


@pytest.fixture
def sources(tmp_path):
    config = ResearchConfig(dates=DATES, rows_per_date=80)
    raw = tmp_path / "raw"
    manifests = generate_fixture(raw, dates=config.dates, rows_per_date=config.rows_per_date)
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config.to_dict()), encoding="utf-8")
    lock_path = tmp_path / "sources.lock.json"
    lock_path.write_text(json.dumps({
        "schema_version": 1, "data_contract": _data_contract(config), "sources": manifests,
    }), encoding="utf-8")
    return config, raw, manifests, config_path, lock_path


def test_help_explains_offline_demo_and_the_explicit_network_command(capsys):
    with pytest.raises(SystemExit) as stopped:
        main(["--help"])
    assert stopped.value.code == 0
    output = capsys.readouterr().out
    assert "demo offline" in output
    assert "fetch is the only network command" in " ".join(output.split())


def test_missing_configuration_is_a_structured_error_without_network(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(acquisition, "download_many", lambda *args, **kwargs: pytest.fail("Offline failure tried to fetch"))
    status = main(["run", "--config", str(tmp_path / "missing.json")])
    assert status == 2
    error = json.loads(capsys.readouterr().err)
    assert error["status"] == "error"
    assert "missing.json" in error["error"]


def test_ingest_command_verifies_sources_and_creates_auditable_local_artifacts(sources, tmp_path, capsys, monkeypatch):
    config, raw, _, config_path, lock = sources
    monkeypatch.setattr(acquisition, "download_many", lambda *args, **kwargs: pytest.fail("Ingest command performed network acquisition"))
    output = tmp_path / "normalized"
    status = main([
        "ingest", "--config", str(config_path), "--raw-dir", str(raw),
        "--source-lock", str(lock), "--output", str(output),
    ])
    assert status == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "ingested"
    assert result["retained_states"] == len(config.dates) * 80
    assert (output / "normalized-states.csv.gz").is_file()
    quality = json.loads((output / "quality.json").read_text(encoding="utf-8"))
    assert quality["retained_rows"] == result["retained_states"]
    assert quality["excluded_rows"] == 0


def test_corrupted_source_fails_checksum_before_any_output(sources, tmp_path, capsys):
    _, raw, manifests, config_path, lock = sources
    path = raw / manifests[0]["path"]
    path.write_bytes(path.read_bytes() + b"\n")
    output = tmp_path / "must-not-exist"
    status = main([
        "ingest", "--config", str(config_path), "--raw-dir", str(raw),
        "--source-lock", str(lock), "--output", str(output),
    ])
    assert status == 2
    assert "checksum" in json.loads(capsys.readouterr().err)["error"].lower()
    assert not output.exists()


def test_manifest_paths_cannot_escape_the_raw_directory(sources):
    config, raw, manifests, _, _ = sources
    manifests[0]["path"] = "../outside.csv"
    (raw / "manifest.json").write_text(json.dumps(manifests), encoding="utf-8")
    with pytest.raises(ValueError, match="safe relative"):
        load_sources(raw, config, source_lock=None)


def test_changed_acquisition_contract_does_not_start_a_fetch(sources, capsys, monkeypatch):
    _, raw, _, config_path, lock = sources
    saved = json.loads(lock.read_text(encoding="utf-8"))
    saved["data_contract"]["rows_per_date"] = 999
    lock.write_text(json.dumps(saved), encoding="utf-8")
    monkeypatch.setattr(acquisition, "download_many", lambda *args, **kwargs: pytest.fail("Mismatched frozen contract reached acquisition"))
    status = main([
        "fetch", "--config", str(config_path), "--raw-dir", str(raw), "--source-lock", str(lock),
    ])
    assert status == 2
    assert "different acquisition" in json.loads(capsys.readouterr().err)["error"]


def test_report_command_refuses_to_overwrite_existing_evidence(tmp_path, capsys):
    reference = tmp_path / "reference.json"
    reference.write_text("{}", encoding="utf-8")
    output = tmp_path / "report"
    output.mkdir()
    original = output / "keep.txt"
    original.write_text("existing user evidence", encoding="utf-8")
    status = main(["report", "--reference", str(reference), "--output", str(output)])
    assert status == 2
    assert "avoid overwriting" in json.loads(capsys.readouterr().err)["error"]
    assert original.read_text(encoding="utf-8") == "existing user evidence"


def test_offline_demo_fits_real_estimators_and_produces_explicitly_synthetic_reports(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(acquisition, "download_many", lambda *args, **kwargs: pytest.fail("Demo used the network"))
    project = tmp_path / "isolated-project"
    original_root = Path(__file__).resolve().parents[1]
    shutil.copytree(original_root / "src", project / "src", ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("pyproject.toml", "uv.lock", ".python-version"):
        shutil.copy2(original_root / name, project / name)
    actual_runner = experiment.run_experiment

    def isolated_runner(*args, **kwargs):
        return actual_runner(*args, project_root=project, **kwargs)

    monkeypatch.setattr(experiment, "run_experiment", isolated_runner)
    output = tmp_path / "demo"
    with threadpool_limits(limits=1):
        status = main(["demo", "--rows-per-date", "80", "--output", str(output)])
    assert status == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "synthetic-demo-complete"
    report_path = Path(result["report"])
    assert report_path.is_file()
    artifact = json.loads(report_path.with_name("experiment.json").read_text(encoding="utf-8"))
    assert artifact["kind"] == "synthetic_fixture"
    assert artifact["sample_count"] > 0
    assert set(artifact["holdout"]["models"]) == {"majority", "logistic", "boosted"}
    assert "synthetic" in report_path.read_text(encoding="utf-8").lower()
