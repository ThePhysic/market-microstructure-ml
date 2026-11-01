import json
from pathlib import Path

import pytest

from market_microstructure.extension.cli import main
from market_microstructure.extension.reporting import write_report


def test_help_distinguishes_explicit_fetch_and_offline_demo(capsys):
    with pytest.raises(SystemExit) as stopped:
        main(["--help"])
    assert stopped.value.code == 0
    assert "only fetch uses the network" in " ".join(capsys.readouterr().out.split())


def test_missing_sources_fail_before_network_or_fitting(tmp_path, capsys, monkeypatch):
    import market_microstructure.extension.acquisition as acquisition
    monkeypatch.setattr(acquisition, "download_days", lambda *a, **k: pytest.fail("Offline command accessed network"))
    config = Path(__file__).resolve().parents[1] / "configs/research-extension.json"
    status = main(["coverage", "--config", str(config), "--source-lock", str(tmp_path/"missing.json")])
    assert status == 2
    assert json.loads(capsys.readouterr().err)["status"] == "error"


def test_report_escapes_dynamic_content_and_has_offline_evidence_links(tmp_path):
    document = {"experiment_id": "<script>bad()</script>", "kind": "synthetic_fixture",
                "research": {"warning": "<img src=x>"}, "limitations": ["<unsafe>"],
                "config": {}, "simulations": {}}
    write_report(document, tmp_path)
    html = (tmp_path/"report.html").read_text(encoding="utf-8")
    assert "<script>" not in html and "<img src=x>" not in html
    assert "SYNTHETIC DEMONSTRATION" in html
    assert 'href="experiment.json"' in html and 'href="report.md"' in html
    assert "No execution results" in html
    assert html.count("Synthetic fixture only.") == 2
    assert "Declared practical improvement" in html and "Precision target" in html
    assert "annualized" in html or "continuous" in html


def test_reference_report_cannot_overwrite_evidence(tmp_path, capsys):
    config = Path(__file__).resolve().parents[1] / "configs/research-extension.json"
    reference = tmp_path/"reference.json"
    reference.write_text("{}", encoding="utf-8")
    target = tmp_path/"report"
    target.mkdir()
    original = target/"keep.txt"
    original.write_text("keep", encoding="utf-8")
    assert main(["report", "--config", str(config), "--reference", str(reference), "--output", str(target)]) == 2
    assert "empty" in json.loads(capsys.readouterr().err)["error"]
    assert original.read_text() == "keep"
