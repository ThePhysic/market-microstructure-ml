"""Frozen model comparisons, date-aware uncertainty and holdout accounting."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Callable
import warnings

import numpy as np
import pandas as pd

from .config import ResearchConfig
from .evaluation import evaluate_predictions, paired_session_bootstrap, summarize_session_scores
from .features import build_samples
from .manifests import code_provenance, digest, environment_provenance, frame_digest, jsonable, write_json
from .models import model_factories, model_specifications
from .splits import Fold, audit_fold, walk_forward

FEATURE_ALLOWLIST = {
    "spread_ticks", "level1_imbalance", "depth5_imbalance", "bid_depth5", "ask_depth5",
    "mid_change_1_ticks", "mid_change_window_ticks", "mid_volatility_ticks",
    "spread_change_1_ticks", "imbalance_change_1",
}
Progress = Callable[[str], None]


def _quality_summary(value: Any) -> Any:
    """Never include excluded row records or historical row-level payloads in reports."""
    if isinstance(value, dict):
        return {
            str(key): _quality_summary(item) for key, item in value.items()
            if key not in {"exclusion_rows", "records", "rows", "examples"}
            and (key != "exclusions" or isinstance(item, dict))
        }
    if isinstance(value, (list, tuple)):
        return [_quality_summary(item) for item in value]
    return jsonable(value)


def _fit_fold(
    samples: pd.DataFrame, features: list[str], fold: Fold, config: ResearchConfig,
) -> dict[str, Any]:
    boundary_proof = audit_fold(samples, fold)
    train = samples.iloc[fold.train_indices]
    test = samples.iloc[fold.test_indices]
    if train["target"].nunique() < 2:
        raise ValueError(f"{fold.name}: training has fewer than two classes")
    x_train, x_test = train[features], test[features]
    if x_train.isna().all().any():
        raise ValueError(f"{fold.name}: an input has no observed training values")
    y_train, y_test = train["target"].to_numpy(), test["target"].to_numpy()
    result: dict[str, Any] = {
        "name": fold.name, "train_dates": list(fold.train_dates),
        "test_dates": list(fold.test_dates), "train_count": len(train), "test_count": len(test),
        "purged_count": fold.purged_count, "audit": boundary_proof,
        "models": {}, "by_date": {}, "fit_transformations": {}, "runtime_seconds": {},
        "warnings": [],
    }
    for model_name, factory in model_factories(config.seed).items():
        estimator = factory()
        started = time.perf_counter()
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            estimator.fit(x_train, y_train)
            predicted = estimator.predict(x_test)
        result["runtime_seconds"][model_name] = time.perf_counter() - started
        result["models"][model_name] = evaluate_predictions(y_test, predicted)
        for warning in captured:
            result["warnings"].append(f"{model_name}: {warning.category.__name__}: {warning.message}")
        transforms: dict[str, Any] = {"fit_rows": len(train), "fit_scope": "training partition only"}
        for step_name, step in estimator.steps[:-1]:
            state: dict[str, Any] = {"class": type(step).__name__}
            for attribute in ("statistics_", "mean_", "scale_", "n_samples_seen_"):
                if hasattr(step, attribute):
                    state[attribute + "_sha256"] = digest(jsonable(getattr(step, attribute)))
            transforms[step_name] = state
        result["fit_transformations"][model_name] = transforms
        for date in fold.test_dates:
            mask = test["session_date"].to_numpy() == date
            if not mask.any():
                raise ValueError(f"{fold.name}: no test rows for declared date {date}")
            result["by_date"].setdefault(date, {})[model_name] = evaluate_predictions(
                y_test[mask], predicted[mask]
            )
        # The fitted model and per-row predictions remain in memory only.
    return result


def _development(
    samples: pd.DataFrame, features: list[str], folds: list[Fold],
    config: ResearchConfig, progress: Progress, prefix: str,
) -> dict[str, Any]:
    reports = []
    for fold in folds:
        progress(f"{prefix}: {fold.name}, testing {', '.join(fold.test_dates)}")
        reports.append(_fit_fold(samples, features, fold, config))
    summary: dict[str, Any] = {}
    scores: dict[str, dict[str, float]] = {}
    for name in ("majority", "logistic", "boosted"):
        scores[name] = {
            date: metrics[name]["macro_f1"]
            for fold in reports for date, metrics in fold["by_date"].items()
        }
        f1 = summarize_session_scores(scores[name])
        balanced = summarize_session_scores({
            date: metrics[name]["balanced_accuracy"]
            for fold in reports for date, metrics in fold["by_date"].items()
        })
        summary[name] = {
            "macro_f1_mean": f1["mean"], "macro_f1_std": f1["std"],
            "balanced_accuracy_mean": balanced["mean"], "macro_f1_by_date": scores[name],
            "dispersion": f1, "warnings": f1["warnings"],
        }
    comparisons = {
        f"boosted_vs_{baseline}": paired_session_bootstrap(
            scores["boosted"], scores[baseline], seed=config.seed,
        )
        for baseline in ("logistic", "majority")
    }
    return {"folds": reports, "summary": summary, "paired_comparisons": comparisons}


def _conclusion(development: dict[str, Any], holdout: dict[str, Any]) -> dict[str, str]:
    summary = development["summary"]
    delta = summary["boosted"]["macro_f1_mean"] - summary["logistic"]["macro_f1_mean"]
    majority_delta = summary["boosted"]["macro_f1_mean"] - summary["majority"]["macro_f1_mean"]
    test_delta = holdout["models"]["boosted"]["macro_f1"] - holdout["models"]["logistic"]["macro_f1"]
    test_majority = holdout["models"]["boosted"]["macro_f1"] - holdout["models"]["majority"]["macro_f1"]
    lower = development["paired_comparisons"]["boosted_vs_logistic"].get("ci_lower")
    absent = any(
        any(row["support"] == 0 for row in model["per_class"])
        for fold in development["folds"] + [holdout] for model in fold["models"].values()
    )
    if not absent and lower is not None and lower > 0 and majority_delta > 0 and test_delta > 0 and test_majority > 0:
        title = "Promising exploratory improvement on these limited excerpts"
        text = (
            "Under the frozen contract, boosted trees exceeded both baseline comparisons in "
            "development and the final aggregate holdout. The small date sample and narrow "
            "opening windows prevent a broad claim of market generalization."
        )
    elif not absent and delta <= 0 and test_delta <= 0:
        title = "No evidence of added value beyond the linear comparison"
        text = (
            "The boosted model did not improve macro F1 beyond logistic regression in either "
            "the development date mean or aggregate final holdout. This does not establish that "
            "all order-book information is uninformative."
        )
    else:
        title = "Inconclusive evidence of improvement beyond the linear comparison"
        text = (
            "The frozen comparisons do not jointly support a repeatable improvement beyond "
            "logistic regression. Any observed advantage is limited by variation across dates, "
            "a small independent sample, or missing-class coverage."
        )
    return {
        "title": title, "text": text,
        "next_test": "Predeclare a new set of broader intraday dates and a new untouched holdout before further model selection.",
    }


def _raw_identity(manifests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "date": item["date"], "sha256": item["sha256"], "path": item["path"],
        "synthetic": item.get("synthetic"), "exchange": item.get("exchange"),
        "symbol": item.get("symbol"),
    } for item in sorted(manifests, key=lambda item: item["date"])]


def _checked_splits(samples: pd.DataFrame, config: ResearchConfig, name: str):
    actual_dates = sorted(samples["session_date"].unique().tolist())
    if actual_dates != list(config.dates):
        missing = sorted(set(config.dates) - set(actual_dates))
        extra = sorted(set(actual_dates) - set(config.dates))
        raise ValueError(f"{name}: eligible sample date coverage mismatch; missing={missing}, extra={extra}")
    folds, holdout, audit = walk_forward(
        samples, min_train_dates=config.min_train_dates, holdout_dates=config.holdout_dates,
    )
    expected_final = list(config.dates[-config.holdout_dates:])
    expected_development = list(config.dates[config.min_train_dates:-config.holdout_dates])
    if list(holdout.test_dates) != expected_final:
        raise ValueError(f"{name}: reserved final dates changed from {expected_final}")
    if [date for fold in folds for date in fold.test_dates] != expected_development:
        raise ValueError(f"{name}: development evaluation dates changed")
    return folds, holdout, audit


def _contextual_warnings(section_name: str, folds: list[dict[str, Any]]) -> list[str]:
    messages = []
    for fold in folds:
        prefix = f"{section_name}/{fold['name']}"
        messages.extend(f"{prefix}: {message}" for message in fold["warnings"])
        for model, metrics in fold["models"].items():
            messages.extend(f"{prefix}/{model}: {message}" for message in metrics["warnings"])
        for date, models in fold["by_date"].items():
            for model, metrics in models.items():
                messages.extend(
                    f"{prefix}/{date}/{model}: {message}" for message in metrics["warnings"]
                )
    return messages


def _holdout_registry(
    path: Path, key: str, contract: str, code_hash: str,
) -> dict[str, Any]:
    registry = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if key in registry and registry[key]["contract_hash"] != contract:
        raise ValueError(
            "This holdout was already bound to different research settings. "
            "A new reviewed contract and untouched holdout are required."
        )
    previous = registry.get(key, {})
    registry[key] = {
        "contract_hash": contract, "first_registered_at": previous.get(
            "first_registered_at", datetime.now(timezone.utc).isoformat()
        ), "execution_count": previous.get("execution_count", 0) + 1,
        "code_hashes": sorted(set(previous.get("code_hashes", []) + [code_hash])),
        "policy": "Repeat execution is for frozen reproduction, never holdout-driven selection.",
    }
    write_json(path, registry)
    return registry[key]


def run_experiment(
    states: pd.DataFrame, *, config: ResearchConfig,
    source_manifests: list[dict[str, Any]], ingestion_quality: dict[str, Any],
    output_dir: str | Path, project_root: str | Path | None = None,
    progress: Progress | None = None, force_reproduction: bool = False,
) -> dict[str, Any]:
    """Run the frozen study. All robustness fitting precedes final-holdout scoring."""
    progress = progress or (lambda message: None)
    root = Path(project_root or Path(__file__).resolve().parents[2])
    output = Path(output_dir)
    if sorted(states["session_date"].unique().tolist()) != list(config.dates):
        raise ValueError("Observed dates must exactly match the frozen research configuration")
    if [item["date"] for item in sorted(source_manifests, key=lambda item: item["date"])] != list(config.dates):
        raise ValueError("Source manifests must cover exactly the frozen research dates")
    synthetic_flags = [item.get("synthetic") for item in source_manifests]
    if all(flag is True for flag in synthetic_flags):
        kind = "synthetic_fixture"
    elif all(flag is False for flag in synthetic_flags):
        if not all(
            item.get("provider") == "Tardis.dev"
            and item.get("retrieval_url", "").startswith("https://datasets.tardis.dev/v1/deribit/book_snapshot_5/")
            for item in source_manifests
        ):
            raise ValueError("Real-data provenance is not the frozen Tardis source")
        kind = "real_historical"
    else:
        raise ValueError("Sources must explicitly and consistently identify synthetic or real data")
    samples, features, feature_quality = build_samples(
        states, horizon_events=config.horizon_events, threshold_ticks=config.threshold_ticks,
        tick_size=config.tick_size, trailing_window=config.trailing_window,
    )
    if set(features) != FEATURE_ALLOWLIST:
        raise ValueError("Feature list differs from the predeclared causal input contract")
    folds, holdout, split_audit = _checked_splits(samples, config, "Primary")
    # Validate every predeclared partition before any fitting, so exclusions
    # can never silently change the reserved dates or robustness comparisons.
    alt_samples, alt_features, alt_quality = build_samples(
        states, horizon_events=dict(config.robustness)["alternate_horizon_events"],
        threshold_ticks=config.threshold_ticks, tick_size=config.tick_size,
        trailing_window=config.trailing_window,
    )
    alt_folds, _, alt_audit = _checked_splits(alt_samples, config, "Alternate horizon")
    code = code_provenance(root)
    environment = environment_provenance()
    fingerprints = {
        "config": digest(config.to_dict()), "raw_sources": digest(_raw_identity(source_manifests)),
        "normalized_states": frame_digest(states), "samples": frame_digest(samples),
        "feature_columns": digest(features),
        "split_assignments": digest({"development": [fold.audit for fold in folds], "holdout": holdout.audit}),
        "environment": digest(environment), "build": code["build_sha256"],
    }
    experiment_id = "exp-" + digest({
        "fingerprints": fingerprints, "code": code["source_sha256"], "kind": kind,
    })[:16]
    destination = output / experiment_id
    existing = destination / "experiment.json"
    if existing.exists() and not force_reproduction:
        cached = json.loads(existing.read_text(encoding="utf-8"))
        if cached.get("fingerprints") != fingerprints or cached.get("experiment_id") != experiment_id:
            raise ValueError("Existing result does not match this experiment; refusing overwrite")
        if not all((destination / name).is_file() for name in ("report.html", "report.md")):
            raise ValueError(
                "Cached result is missing readable reports. Use report --reference with a fresh output directory."
            )
        progress(f"Reusing completed immutable result {experiment_id}")
        cached["output_paths"] = {
            "html": str(destination / "report.html"), "markdown": str(destination / "report.md"),
            "json": str(existing),
        }
        return cached
    if destination.exists() and force_reproduction:
        raise ValueError("Reproduction output must use a fresh directory")
    development = _development(samples, features, folds, config, progress, "Primary development")
    without_imbalance = [name for name in features if "imbalance" not in name]
    robustness = {
        "remove_imbalance": _development(
            samples, without_imbalance, folds, config, progress, "Predeclared imbalance ablation"
        )
    }
    if {date for fold in alt_folds for date in fold.test_dates} & set(holdout.test_dates):
        raise ValueError("Robustness attempted to inspect the final holdout")
    robustness["horizon_20"] = _development(
        alt_samples, alt_features, alt_folds, config, progress, "Predeclared 20-state horizon"
    )
    robustness["horizon_20"]["feature_quality"] = _quality_summary(alt_quality)
    robustness["horizon_20"]["split_audit"] = alt_audit
    contract_hash = digest({
        "config": config.to_dict(), "features": features, "models": model_specifications(config.seed),
        "scientific_code": code["scientific_sha256"], "environment": digest(environment),
        "build": code["build_sha256"],
    })
    holdout_sources = [
        item for item in _raw_identity(source_manifests) if item["date"] in holdout.test_dates
    ]
    holdout_content_identity = [
        {key: item[key] for key in ("date", "sha256", "exchange", "symbol", "synthetic")}
        for item in holdout_sources
    ]
    usage = _holdout_registry(
        root / "artifacts" / "holdout-registry.json", digest(holdout_content_identity), contract_hash,
        code["source_sha256"],
    )
    progress("Frozen final holdout: fitting on development dates, then evaluating reserved dates")
    final = _fit_fold(samples, features, holdout, config)
    messages = [
        "Only noncontiguous monthly opening excerpts are observed; these are not full trading days.",
        "Millions of correlated rows are not millions of independent experimental observations.",
        "Date bootstrap intervals are exploratory; overlapping training windows and few dates limit inference.",
        "Vendor snapshots were reconstructed and may have crossed levels removed upstream.",
        "CSV disconnect events are unavailable; a 30-second gap rule is only a discontinuity heuristic.",
        "Order sizes are vendor-native USD notional for this inverse instrument, not BTC quantities.",
        "Prediction scores do not establish executable, fee-adjusted trading profitability.",
        "No fitted models, row-level predictions or historical records are redistributed.",
    ]
    if kind == "synthetic_fixture":
        messages.insert(0, "SYNTHETIC FIXTURE: all model outputs here are software tests, not empirical market findings.")
    for section_name, section in {"primary": development, **robustness}.items():
        for comparison in section["paired_comparisons"].values():
            messages.extend(comparison.get("warnings", []))
        messages.extend(_contextual_warnings(section_name, section["folds"]))
    messages.extend(_contextual_warnings("final_holdout", [final]))
    conclusion = _conclusion(development, final)
    if kind == "synthetic_fixture":
        conclusion = {
            "title": "Synthetic software demonstration — no market conclusion",
            "text": (
                "Actual estimators were trained and evaluated on project-generated toy data. "
                "These scores exercise the software workflow only and establish no finding "
                "about historical markets or the value of order-book features."
            ),
            "next_test": "Use the frozen real-data contract and verified source files for empirical research.",
        }
    result = {
        "schema_version": 1, "kind": kind, "experiment_id": experiment_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "config": config.to_dict(), "feature_columns": features, "primary_model": "boosted",
        "model_specifications": model_specifications(config.seed),
        "sample_count": len(samples), "observed_dates": list(config.dates),
        "source_manifest": source_manifests, "code": code, "fingerprints": fingerprints,
        "environment": environment,
        "quality": {"ingestion": _quality_summary(ingestion_quality), "features": _quality_summary(feature_quality)},
        "development": development, "holdout": final, "robustness": robustness,
        "split_audit": split_audit, "holdout_usage": usage,
        "research_contract_hash": contract_hash,
        "warnings": list(dict.fromkeys(messages)),
        "conclusion": conclusion,
        "reproduction_commands": (
            ["uv run microstructure demo --output artifacts/demo"] if kind == "synthetic_fixture"
            else [
                "uv sync --frozen --extra dev",
                "uv run microstructure fetch --config configs/research.json --raw-dir data/raw --source-lock data/sources.lock.json",
                "uv run microstructure run --config configs/research.json --raw-dir data/raw --output reports/runs",
                "uv run microstructure reproduce --reference reports/reference/experiment.json --raw-dir data/raw --output artifacts/reproduction",
            ]
        ),
    }
    from .reporting import write_reports
    destination.mkdir(parents=True, exist_ok=False)
    paths = write_reports(jsonable(result), destination)
    progress(f"Reports written to {destination}")
    result["output_paths"] = paths
    return jsonable(result)
