"""Synthetic aggregate evidence verifies report behavior, never market findings."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re

import pytest

from market_microstructure.evaluation import evaluate_predictions
from market_microstructure.reporting import write_reports


class _Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = set()
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if attributes.get("id"):
            assert attributes["id"] not in self.ids
            self.ids.add(attributes["id"])
        if tag == "a":
            self.anchors.append(attributes.get("href", ""))


def _result():
    metric = evaluate_predictions([-1, -1, 0, 0, 1, 1], [-1, 0, 0, 1, 1, 1])
    models = {"majority": metric, "logistic": metric, "boosted": metric}
    fold = {
        "name": "fold_01",
        "train_dates": ["2020-01-01", "2020-02-01", "2020-03-01"],
        "test_dates": ["2020-04-01"],
        "train_count": 24, "test_count": 6, "purged_count": 2, "models": models,
    }
    development = {
        "folds": [fold],
        "summary": {
            name: {
                "macro_f1_mean": metric["macro_f1"], "macro_f1_std": 0.0,
                "balanced_accuracy_mean": metric["balanced_accuracy"],
            }
            for name in models
        },
        "paired_comparisons": {
            "boosted_vs_logistic": {
                "n_units": 1, "mean_difference": 0.0, "ci_lower": None,
                "ci_upper": None, "status": "insufficient_units",
                "warnings": ["No confidence interval with one date."],
            }
        },
    }
    return {
        "schema_version": 1, "kind": "synthetic_fixture", "experiment_id": "fixture-report",
        "created_at": "2026-11-01T00:00:00+00:00",
        "config": {"horizon_events": 10, "seed": 42},
        "feature_columns": ["spread_ticks", "imbalance_l1"], "sample_count": 36,
        "observed_dates": [f"2020-{month:02d}-01" for month in range(1, 7)],
        "source_manifest": [{
            "date": "2020-01-01", "retrieval_url": "https://example.org/historical.csv.gz",
            "retained_rows": 100, "bytes_received": 1024, "excerpt_bytes": 4096,
            "excerpt_sha256": "a" * 64, "compressed_sha256": "b" * 64,
        }],
        "code": {"revision": "abc123", "dirty": False},
        "fingerprints": {"config_sha256": "c" * 64},
        "quality": {
            "ingestion": {
                "total_rows": 50, "retained_rows": 48, "excluded_rows": 2,
                "exclusion_counts": {"crossed_or_locked_book": 2},
                "exclusions": [{"private_row_marker": "DO_NOT_DISPLAY_ROW_DIAGNOSTIC"}],
            },
            "features": {"input_rows": 48, "usable_samples": 36},
        },
        "development": development,
        "holdout": {
            "name": "final_holdout",
            "train_dates": ["2020-01-01", "2020-02-01", "2020-03-01", "2020-04-01"],
            "test_dates": ["2020-05-01", "2020-06-01"],
            "train_count": 24, "test_count": 12, "purged_count": 0,
            "models": models, "by_date": {},
        },
        "robustness": {"remove_imbalance": development},
        "split_audit": {"passed": True, "folds_checked": 2},
        "warnings": ["Only six synthetic dates."],
        "conclusion": {
            "title": "Synthetic software check", "text": "These fixture scores support no market claim.",
            "next_test": "Supply approved historical excerpts.",
        },
        "reproduction_commands": ["uv run microstructure demo --output artifacts/demo"],
    }


def test_writes_portable_report_triplet_with_matching_json(tmp_path):
    result = _result()
    paths = write_reports(result, tmp_path / "report")
    assert set(paths) == {"html", "markdown", "json"}
    assert all(Path(value).is_file() for value in paths.values())
    assert json.loads(Path(paths["json"]).read_text(encoding="utf-8")) == result
    rendered_html = Path(paths["html"]).read_text(encoding="utf-8")
    markdown = Path(paths["markdown"]).read_text(encoding="utf-8")
    assert "SYNTHETIC FIXTURE — DEMONSTRATION ONLY" in rendered_html
    assert "NO EMPIRICAL MARKET FINDINGS" in markdown
    assert "higher is better" in rendered_html and "higher is better" in markdown
    assert "not complete trading days" in rendered_html
    assert "6 observed dates and 1 development evaluation dates" in rendered_html
    assert "uv run microstructure demo --output artifacts/demo" in rendered_html
    assert "DO_NOT_DISPLAY_ROW_DIAGNOSTIC" not in rendered_html
    assert "DO_NOT_DISPLAY_ROW_DIAGNOSTIC" not in markdown
    assert "https://example.org/historical.csv.gz" in rendered_html
    assert "a" * 64 in rendered_html and "b" * 64 in markdown


def test_html_uses_existing_section_anchors_and_real_sibling_evidence_links(tmp_path):
    paths = write_reports(_result(), tmp_path)
    document = _Document()
    document.feed(Path(paths["html"]).read_text(encoding="utf-8"))
    expected = {"overview", "models", "validation", "quality", "research-note", "provenance"}
    assert expected.issubset(document.ids)
    for href in document.anchors:
        if href.startswith("#"):
            assert href[1:] in document.ids
        elif href in {"experiment.json", "report.md"}:
            assert (tmp_path / href).is_file()
    assert "experiment.json" in document.anchors and "report.md" in document.anchors
    tables = [
        attrs for tag, attrs in document.tags
        if tag == "div" and attrs.get("class") == "table-wrap"
    ]
    assert tables
    assert all(item["tabindex"] == "0" and item["role"] == "region" for item in tables)


def test_report_has_no_active_script_or_automatic_external_resources(tmp_path):
    rendered_html = Path(write_reports(_result(), tmp_path)["html"]).read_text(encoding="utf-8")
    document = _Document()
    document.feed(rendered_html)
    forbidden = {"script", "iframe", "img", "video", "audio", "object", "embed"}
    assert not any(tag in forbidden for tag, _ in document.tags)
    assert not any(tag == "link" and attrs.get("href") for tag, attrs in document.tags)
    assert not re.search(r"@import|url\s*\(", rendered_html, re.IGNORECASE)
    assert "onclick=" not in rendered_html
    assert "font-size:14px" in rendered_html and "overflow-x:auto" in rendered_html


def test_dynamic_titles_paths_metadata_and_source_links_cannot_inject_html(tmp_path):
    result = _result()
    payload = '</h2><script>alert("bad")</script><img src=x onerror=alert(1)>'
    result["experiment_id"] = payload
    result["conclusion"]["title"] = payload
    result["conclusion"]["text"] = payload
    result["feature_columns"] = [payload]
    result["source_manifest"][0]["retrieval_url"] = 'javascript:alert("bad")'
    result["source_manifest"][0]["excerpt_sha256"] = payload
    paths = write_reports(result, tmp_path)
    rendered_html = Path(paths["html"]).read_text(encoding="utf-8")
    document = _Document()
    document.feed(rendered_html)
    assert not any(tag in {"script", "img"} for tag, _ in document.tags)
    assert not any(href.startswith("javascript:") for href in document.anchors)
    assert "&lt;script&gt;" in rendered_html
    assert "&lt;script&gt;" in Path(paths["markdown"]).read_text(encoding="utf-8")


def test_missing_optional_sections_are_explicit_and_not_fabricated(tmp_path):
    paths = write_reports({"kind": "synthetic_fixture", "experiment_id": "partial"}, tmp_path)
    rendered_html = Path(paths["html"]).read_text(encoding="utf-8")
    assert "No research conclusion was supplied" in rendered_html
    assert "No records were supplied for this section." in rendered_html
    assert "Exact reproduction commands were not recorded" in rendered_html
    assert "Not recorded" in rendered_html and "0.999" not in rendered_html


def test_real_kind_receives_bounded_historical_banner_without_synthetic_findings(tmp_path):
    result = _result()
    result["kind"] = "real_historical"
    rendered_html = Path(write_reports(result, tmp_path)["html"]).read_text(encoding="utf-8")
    assert "REAL HISTORICAL DATA — BOUNDED EXCERPTS" in rendered_html
    assert "classification scores do not establish trading profitability" in rendered_html
    assert "SYNTHETIC FIXTURE — DEMONSTRATION ONLY" not in rendered_html


@pytest.mark.parametrize(
    ("confidence", "label"), [(0.95, "95%"), (0.90, "90%"), (0.955, "95.5%")]
)
def test_interval_confidence_level_is_taken_from_evidence_in_html_and_markdown(
    tmp_path, confidence, label
):
    result = _result()
    interval = result["development"]["paired_comparisons"]["boosted_vs_logistic"]
    interval.update(confidence=confidence, ci_lower=0.01, ci_upper=0.03, status="exploratory")
    paths = write_reports(result, tmp_path)
    rendered_html = Path(paths["html"]).read_text(encoding="utf-8")
    markdown = Path(paths["markdown"]).read_text(encoding="utf-8")
    assert f"{label} [0.010, 0.030]" in rendered_html
    assert f"{label} \\[0.010, 0.030\\]" in markdown
    assert json.loads(Path(paths["json"]).read_text(encoding="utf-8")) == result


def test_missing_interval_confidence_is_not_silently_assumed_to_be_95_percent(tmp_path):
    result = _result()
    result["development"]["paired_comparisons"]["boosted_vs_logistic"].update(
        ci_lower=0.01, ci_upper=0.03
    )
    paths = write_reports(result, tmp_path)
    for name in ("html", "markdown"):
        assert "Confidence level not recorded" in Path(paths[name]).read_text(encoding="utf-8")


def test_long_warning_prefixes_have_narrow_screen_wrapping_without_altering_text(tmp_path):
    result = _result()
    warning = "remove_imbalance/walk_forward_01/majority:" + "x" * 200
    result["warnings"] = [warning]
    rendered_html = Path(write_reports(result, tmp_path)["html"]).read_text(encoding="utf-8")
    assert warning in rendered_html
    assert re.search(r"\.warning-list\{[^}]*overflow-wrap:anywhere", rendered_html)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), object()])
def test_nonjson_or_nonfinite_evidence_fails_before_output_is_written(tmp_path, value):
    result = _result()
    result["bad_value"] = value
    output = tmp_path / "not-created"
    with pytest.raises((ValueError, TypeError)):
        write_reports(result, output)
    assert not output.exists()
