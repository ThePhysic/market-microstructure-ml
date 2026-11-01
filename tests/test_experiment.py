from copy import deepcopy
from dataclasses import replace
import importlib.metadata
import json
import os
from pathlib import Path
import shutil

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"

import numpy as np
import pytest
from threadpoolctl import threadpool_limits

from market_microstructure.config import ResearchConfig
from market_microstructure.data import ingest_files
import market_microstructure.experiment as experiment
from market_microstructure.synthetic import generate_fixture


DATES = tuple(f"2020-{month:02d}-01" for month in range(1, 9))
PRIVATE_ROW_MARKER = "UNTRUSTED_ROW_PAYLOAD_MUST_NOT_BE_REPORTED"


@pytest.fixture(scope="module", autouse=True)
def deterministic_test_threads():
    with threadpool_limits(limits=1):
        yield


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    base = tmp_path_factory.mktemp("experiment-integration")
    raw = base / "raw"
    manifests = generate_fixture(raw, dates=DATES, rows_per_date=120, seed=42)
    states, quality = ingest_files([raw / entry["path"] for entry in manifests], manifests=manifests)
    assert len(states) == 960
    quality["records"] = [{"private": PRIVATE_ROW_MARKER}]
    quality["nested_example"] = {"rows": [{"private": PRIVATE_ROW_MARKER}], "counts": {"visible": 1}}
    # Freeze a real source-code snapshot so another parallel implementation task
    # cannot legitimately alter experiment identity halfway through this test.
    project = base / "frozen-project"
    shutil.copytree(
        Path(__file__).resolve().parents[1] / "src", project / "src",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    for name in ("pyproject.toml", "uv.lock", ".python-version"):
        shutil.copy2(Path(__file__).resolve().parents[1] / name, project / name)
    return {
        "base": base, "states": states, "quality": quality, "manifests": manifests,
        "config": ResearchConfig(dates=DATES, rows_per_date=120), "project": project,
    }


def run(dataset, name, **changes):
    arguments = {
        "config": dataset["config"], "source_manifests": dataset["manifests"],
        "ingestion_quality": dataset["quality"],
        "output_dir": dataset["base"] / "runs" / name,
        "project_root": dataset["project"],
    }
    states = changes.pop("states", dataset["states"])
    arguments.update(changes)
    return experiment.run_experiment(states, **arguments)


@pytest.fixture(scope="module")
def completed(dataset):
    result = run(dataset, "baseline")
    assert result["kind"] == "synthetic_fixture"
    assert result["sample_count"] > 0
    return result


def projection(result):
    return {
        "fingerprints": result["fingerprints"],
        "primary": [fold["models"] for fold in result["development"]["folds"]],
        "summary": result["development"]["summary"],
        "robustness": {
            name: [fold["models"] for fold in section["folds"]]
            for name, section in result["robustness"].items()
        },
        "holdout": result["holdout"]["models"],
        "by_date": result["holdout"]["by_date"],
        "conclusion": result["conclusion"],
    }


def test_frozen_experiment_reproduces_actual_metrics_in_a_fresh_directory(dataset, completed):
    repeated = run(dataset, "fresh-reproduction", force_reproduction=True)
    assert repeated["experiment_id"] == completed["experiment_id"]
    assert projection(repeated) == projection(completed)
    assert repeated["holdout_usage"]["execution_count"] == completed["holdout_usage"]["execution_count"] + 1


def test_completed_result_is_reused_without_refitting_or_overwriting(dataset, completed, monkeypatch):
    artifact = dataset["base"] / "runs" / "baseline" / completed["experiment_id"] / "experiment.json"
    original = artifact.read_bytes()
    monkeypatch.setattr(experiment, "_fit_fold", lambda *args, **kwargs: pytest.fail("Cache rerun tried to fit a model"))
    cached = run(dataset, "baseline")
    assert projection(cached) == projection(completed)
    assert artifact.read_bytes() == original
    with pytest.raises(ValueError, match="fresh directory"):
        run(dataset, "baseline", force_reproduction=True)


def test_synthetic_conclusion_cannot_be_mistaken_for_an_empirical_market_finding(dataset, completed):
    conclusion = completed["conclusion"]
    assert conclusion["title"] == "Synthetic software demonstration — no market conclusion"
    assert "project-generated toy data" in conclusion["text"]
    assert "establish no finding" in conclusion["text"]
    artifact_dir = dataset["base"] / "runs" / "baseline" / completed["experiment_id"]
    persisted = json.loads((artifact_dir / "experiment.json").read_text(encoding="utf-8"))
    assert persisted["conclusion"] == conclusion
    assert "no market conclusion" in (artifact_dir / "report.html").read_text(encoding="utf-8")


def test_incomplete_readable_report_cache_is_rejected_without_refitting(dataset, completed, monkeypatch):
    artifact_dir = dataset["base"] / "runs" / "baseline" / completed["experiment_id"]
    persisted = (artifact_dir / "experiment.json").read_bytes()
    monkeypatch.setattr(
        experiment, "_fit_fold",
        lambda *args, **kwargs: pytest.fail("Incomplete report cache silently refitted the study"),
    )
    for filename in ("report.html", "report.md"):
        path = artifact_dir / filename
        original = path.read_bytes()
        path.unlink()
        try:
            with pytest.raises(ValueError, match="missing readable reports"):
                run(dataset, "baseline")
            assert (artifact_dir / "experiment.json").read_bytes() == persisted
        finally:
            path.write_bytes(original)


@pytest.mark.parametrize("bad_kind", ["missing_flag", "mixed_flags", "unverified_real_source"])
def test_source_kind_is_explicit_and_bad_provenance_fails_before_fitting(dataset, monkeypatch, bad_kind):
    manifests = deepcopy(dataset["manifests"])
    if bad_kind == "missing_flag":
        manifests[0].pop("synthetic")
    elif bad_kind == "mixed_flags":
        manifests[0]["synthetic"] = False
    else:
        for manifest in manifests:
            manifest["synthetic"] = False
            manifest["provider"] = "unverified vendor"
            manifest["retrieval_url"] = "https://example.invalid/not-market-data"
    monkeypatch.setattr(experiment, "_development", lambda *args, **kwargs: pytest.fail("Invalid provenance reached model fitting"))
    with pytest.raises(ValueError, match="Sources|provenance"):
        run(dataset, bad_kind, source_manifests=manifests)


def test_empty_and_one_class_training_cannot_be_reported_as_a_success(dataset):
    with pytest.raises(ValueError):
        run(dataset, "empty", states=dataset["states"].iloc[:0])
    constant = dataset["states"].copy(deep=True)
    for level in range(1, 6):
        constant[f"bid_price_{level}"] = 10_000.0 - (level - 1) * 0.5
        constant[f"ask_price_{level}"] = 10_001.0 + (level - 1) * 0.5
    with pytest.raises(ValueError, match="fewer than two classes"):
        run(dataset, "one-class", states=constant)


def test_final_holdout_is_absent_from_all_development_and_robustness_fits(completed):
    held_out = set(completed["holdout"]["test_dates"])
    assert held_out == {"2020-07-01", "2020-08-01"}
    for section in [completed["development"], *completed["robustness"].values()]:
        for fold in section["folds"]:
            assert held_out.isdisjoint(fold["train_dates"])
            assert held_out.isdisjoint(fold["test_dates"])
    assert completed["split_audit"]["final_holdout_excluded_from_development"]
    assert set(completed["holdout"]["train_dates"]) == set(DATES) - held_out


def test_counterfactual_holdout_distribution_cannot_change_development_fits(dataset, completed):
    changed = dataset["states"].copy(deep=True)
    final = changed["session_date"].isin(completed["holdout"]["test_dates"])
    ramp = np.arange(int(final.sum())) * 10.0
    for side in ("bid", "ask"):
        for level in range(1, 6):
            changed.loc[final, f"{side}_size_{level}"] *= 1000
            changed.loc[final, f"{side}_price_{level}"] += 100_000 + ramp
    perturbed = run(dataset, "holdout-counterfactual", states=changed)
    for clean_fold, changed_fold in zip(completed["development"]["folds"], perturbed["development"]["folds"]):
        assert clean_fold["models"] == changed_fold["models"]
        assert clean_fold["fit_transformations"] == changed_fold["fit_transformations"]
    for name in completed["robustness"]:
        assert [fold["models"] for fold in completed["robustness"][name]["folds"]] == [
            fold["models"] for fold in perturbed["robustness"][name]["folds"]
        ]
    assert completed["holdout"]["models"] != perturbed["holdout"]["models"]
    missing_class_warnings = [
        warning for warning in perturbed["holdout"]["models"]["majority"]["warnings"]
        if warning.startswith("True classes absent:")
    ]
    assert missing_class_warnings
    for warning in missing_class_warnings:
        assert any("final_holdout" in message and warning in message for message in perturbed["warnings"])


def test_report_payload_discloses_synthetic_scope_and_excludes_rows_and_model_weights(completed):
    payload = json.dumps(completed, allow_nan=False)
    assert "SYNTHETIC FIXTURE" in payload
    assert PRIVATE_ROW_MARKER not in payload
    forbidden = {"coef_", "intercept_", "estimators_", "trees_", "predictions", "x_train", "y_train", "records", "exclusion_rows"}

    def inspect(value):
        if isinstance(value, dict):
            assert forbidden.isdisjoint(value)
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)

    inspect(completed)
    assert completed["quality"]["features"]["exclusions"] == {
        "insufficient_history": 160, "future_unavailable": 80,
    }
    assert completed["quality"]["ingestion"]["nested_example"]["counts"] == {"visible": 1}


def test_same_holdout_rejects_changed_settings_before_final_prediction(dataset, completed, monkeypatch):
    actual = experiment._fit_fold
    final_calls = []

    def guard(samples, features, fold, config):
        if fold.name == "final_holdout":
            final_calls.append(fold.name)
            pytest.fail("A changed contract reached final-holdout fitting")
        return actual(samples, features, fold, config)

    monkeypatch.setattr(experiment, "_fit_fold", guard)
    with pytest.raises(ValueError, match="already bound"):
        run(dataset, "changed-seed", config=replace(dataset["config"], seed=43))
    assert final_calls == []


def test_renaming_identical_sources_cannot_bypass_same_holdout_contract_guard(dataset, completed, monkeypatch):
    renamed = deepcopy(dataset["manifests"])
    for manifest in renamed:
        manifest["path"] = "renamed-" + manifest["path"]
    actual = experiment._fit_fold

    def guard(samples, features, fold, config):
        if fold.name == "final_holdout":
            pytest.fail("Renaming the same source bypassed the holdout contract")
        return actual(samples, features, fold, config)

    monkeypatch.setattr(experiment, "_fit_fold", guard)
    with pytest.raises(ValueError, match="already bound"):
        run(
            dataset, "renamed-same-bytes", source_manifests=renamed,
            config=replace(dataset["config"], seed=43),
        )


def test_changing_output_parent_cannot_bypass_the_project_holdout_registry(dataset, completed, monkeypatch):
    actual = experiment._fit_fold

    def guard(samples, features, fold, config):
        if fold.name == "final_holdout":
            pytest.fail("Changing output parent bypassed the project holdout registry")
        return actual(samples, features, fold, config)

    monkeypatch.setattr(experiment, "_fit_fold", guard)
    with pytest.raises(ValueError, match="already bound"):
        run(
            dataset, "unused", config=replace(dataset["config"], seed=43),
            output_dir=dataset["base"] / "unrelated-parent" / "new-runs",
        )


def test_changed_scientific_source_requires_a_new_reviewed_holdout_contract(dataset, completed, monkeypatch):
    path = dataset["project"] / "src" / "market_microstructure" / "features.py"
    original = path.read_bytes()
    actual = experiment._fit_fold

    def guard(samples, features, fold, config):
        if fold.name == "final_holdout":
            pytest.fail("Changed scientific source reached the reserved holdout")
        return actual(samples, features, fold, config)

    monkeypatch.setattr(experiment, "_fit_fold", guard)
    try:
        path.write_bytes(original + b"\n# Counterfactual scientific-source identity change for the guard test.\n")
        with pytest.raises(ValueError):
            run(dataset, "changed-scientific-source")
    finally:
        path.write_bytes(original)


def test_cached_result_is_not_reused_under_a_changed_package_environment(dataset, completed, monkeypatch):
    actual_version = importlib.metadata.version
    monkeypatch.setattr(
        importlib.metadata, "version",
        lambda name: actual_version(name) + "+counterfactual" if name == "numpy" else actual_version(name),
    )
    monkeypatch.setattr(
        experiment, "_development",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("Cache invalidated by environment change")),
    )
    with pytest.raises((ValueError, RuntimeError)):
        run(dataset, "baseline")


def test_cached_result_is_not_reused_after_build_lock_changes(dataset, completed, monkeypatch):
    path = dataset["project"] / "uv.lock"
    original = path.read_bytes()
    monkeypatch.setattr(
        experiment, "_development",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("Cache invalidated by lock change")),
    )
    try:
        path.write_bytes(original + b"\n# Counterfactual reviewed-build lock identity.\n")
        with pytest.raises((ValueError, RuntimeError)):
            run(dataset, "baseline")
    finally:
        path.write_bytes(original)


def test_losing_reserved_primary_dates_is_rejected_before_any_fit(dataset, monkeypatch):
    held_out = set(DATES[-2:])
    source = dataset["states"]
    retain = ~source["session_date"].isin(held_out) | source["source_row_position"].le(20)
    shortened = source.loc[retain].copy()
    assert set(shortened["session_date"]) == set(DATES)
    fit_calls = []

    def reject_fit(*args, **kwargs):
        fit_calls.append(True)
        pytest.fail("Missing eligible primary dates reached a model fit")

    monkeypatch.setattr(experiment, "_fit_fold", reject_fit)
    with pytest.raises(ValueError) as stopped:
        run(dataset, "lost-primary-holdout-dates", states=shortened)
    assert all(day in str(stopped.value) for day in held_out)
    assert "date" in str(stopped.value).lower()
    assert fit_calls == []


def test_alternate_horizon_cannot_silently_move_the_reserved_holdout(dataset, monkeypatch):
    source = dataset["states"].copy()
    held_out = source["session_date"].isin(DATES[-2:])
    # Thirty-five-state segments yield primary H10 samples after a20-state
    # warmup, but yield no alternate H20 samples. The reserved dates must remain
    # fixed instead of becoming the last two surviving development dates.
    for row_index in source.index[held_out]:
        row = source.loc[row_index]
        source.at[row_index, "segment_id"] = (
            str(row["session_date"]) + ":short:" + str((int(row["source_row_position"]) - 1) // 35)
        )
    fit_calls = []

    def reject_fit(*args, **kwargs):
        fit_calls.append(True)
        pytest.fail("Missing alternate-horizon holdout dates reached model fitting")

    monkeypatch.setattr(experiment, "_fit_fold", reject_fit)
    with pytest.raises(ValueError) as stopped:
        run(dataset, "lost-alternate-holdout-dates", states=source)
    assert all(day in str(stopped.value) for day in DATES[-2:])
    assert "date" in str(stopped.value).lower()
    assert fit_calls == []
