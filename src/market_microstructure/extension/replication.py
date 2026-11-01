"""Development-only methodological adaptation of Gould and Bonart (2015).

This is not a reproduction of their equity-market numerical results. It tests
the published queue-imbalance idea on the separately declared crypto excerpts,
with chronological splits and proper out-of-sample probability scores.
"""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Real
from typing import Any
import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, log_loss, roc_auc_score

from market_microstructure.features import _validate_states
from market_microstructure.models import model_factories, model_specifications
from .study import exact_midpoint_units, make_date_fold, validate_research_config, validate_state_coverage

PAPER_URL = "https://arxiv.org/abs/1512.03492"
ADAPTATION_MODELS = ("queue_logistic", "empirical_prior", "paper_constant_half")


def build_next_move_samples(states: pd.DataFrame, *, tick_size: float = 0.01) -> tuple[pd.DataFrame, dict[str, Any]]:
    """One causal decision at the start of each constant-midpoint run.

    The first observation of a run is identifiable on arrival. The label ends
    at the next observed nonzero midpoint change inside the same segment/date/
    file; the last run is unlabelled and excluded. There is no future-conditioned
    random choice of a decision time.
    """
    if isinstance(tick_size, bool) or not isinstance(tick_size, Real) or not np.isfinite(tick_size) or tick_size <= 0:
        raise ValueError("tick_size must be finite and positive")
    normalized = _validate_states(states)
    midpoints = exact_midpoint_units(normalized, tick_size)
    pieces = []
    quality = {"input_rows": len(normalized), "segments": 0, "samples": 0,
               "terminal_runs_without_next_move": 0, "zero_queue_denominator_decisions": 0}
    for _, group in normalized.groupby(["session_date", "segment_id", "source_file"], sort=False):
        group = group.reset_index(drop=True)
        # Exact half-tick midpoint units prevent false moves from float addition.
        mid_units = midpoints.loc[group["source_order"].to_numpy()].to_numpy(dtype=np.int64)
        starts = np.flatnonzero(np.r_[True, np.diff(mid_units) != 0])
        quality["segments"] += 1
        quality["terminal_runs_without_next_move"] += 1
        if len(starts) < 2:
            continue
        decision, end = starts[:-1], starts[1:]
        chosen = group.iloc[decision].copy()
        bid = chosen["bid_size_1"].to_numpy(dtype=float)
        ask = chosen["ask_size_1"].to_numpy(dtype=float)
        denominator = bid + ask
        chosen["queue_imbalance"] = np.divide(
            bid - ask, denominator, out=np.zeros_like(denominator), where=denominator != 0,
        )
        quality["zero_queue_denominator_decisions"] += int(np.sum(denominator == 0))
        chosen["target"] = (mid_units[end] > mid_units[decision]).astype(np.int8)
        chosen["feature_cutoff_time"] = group["receive_time_us"].to_numpy(dtype=np.int64)[decision]
        chosen["label_end_time"] = group["receive_time_us"].to_numpy(dtype=np.int64)[end]
        chosen["feature_order"] = group["source_order"].to_numpy(dtype=np.int64)[decision]
        chosen["label_end_order"] = group["source_order"].to_numpy(dtype=np.int64)[end]
        for label_column, input_column in (
            ("label_segment_id", "segment_id"), ("label_session_date", "session_date"),
            ("label_source_file", "source_file"),
        ):
            chosen[label_column] = group[input_column].to_numpy()[end]
        pieces.append(chosen)
    if not pieces:
        raise ValueError("No next-midpoint-change targets are available inside the supplied segments")
    samples = pd.concat(pieces, ignore_index=True)
    quality["samples"] = len(samples)
    quality["decision_sampling"] = "first observation of each constant-midpoint run, excluding the terminal run"
    quality["target"] = "binary direction of next observed nonzero midpoint change inside the same segment"
    quality["midpoint_representation"] = "integer half-tick units on the declared price grid"
    quality["tick_size"] = float(tick_size)
    return samples, quality


def binary_probability_metrics(y_true: Any, p_up: Any) -> dict[str, Any]:
    truth, probability = np.asarray(y_true), np.asarray(p_up, dtype=float)
    if truth.ndim != 1 or not len(truth) or truth.shape != probability.shape:
        raise ValueError("Probability metrics require nonempty paired one-dimensional arrays")
    if not np.isin(truth, [0, 1]).all() or not np.isfinite(probability).all() or np.any((probability < 0) | (probability > 1)):
        raise ValueError("Targets must be binary and probabilities finite in [0,1]")
    truth = truth.astype(np.int64)
    predicted = (probability > 0.5).astype(np.int64)
    matrix = confusion_matrix(truth, predicted, labels=[0, 1])
    both = len(np.unique(truth)) == 2
    warnings = [] if both else ["Only one true binary class is present; ROC AUC is undefined."]
    return {
        "class_order": [0, 1], "class_names": ["down", "up"], "support": len(truth),
        "class_support": matrix.sum(axis=1).astype(int).tolist(),
        "confusion_matrix": matrix.astype(int).tolist(),
        "brier_score": float(np.mean((probability - truth) ** 2)),
        "log_loss": float(log_loss(truth, np.column_stack([1 - probability, probability]), labels=[0, 1])),
        "roc_auc": float(roc_auc_score(truth, probability)) if both else None,
        "accuracy": float(np.mean(truth == predicted)),
        "probability_threshold": 0.5, "threshold_tie_policy": "down",
        "log_loss_endpoint_policy": "sklearn machine-epsilon clipping for probabilities exactly zero or one",
        "warnings": warnings,
    }


def adapt_queue_imbalance(states: pd.DataFrame, config: Mapping[str, Any]) -> dict[str, Any]:
    """Return aggregate development evidence only; never use reserved labels."""
    config = validate_research_config(config)
    normalized = validate_state_coverage(states, config)
    permitted_dates = [day for day in config["dates"] if day not in set(config["final_dates"])]
    permitted = normalized.loc[normalized["session_date"].isin(permitted_dates)]
    samples, quality = build_next_move_samples(permitted, tick_size=config["tick_size"])
    if list(samples["session_date"].drop_duplicates()) != permitted_dates:
        raise ValueError("Every development/train date must have a next-move sample before any fit")
    folds = [
        make_date_fold(samples, f"queue_development_{index:02d}",
                       [date for date in permitted_dates if date < day], day)
        for index, day in enumerate(config["development_dates"], 1)
    ]
    for fold in folds:
        if samples.iloc[fold.train_indices]["target"].nunique() < 2:
            raise ValueError(f"{fold.name}: binary logistic training needs both classes before any fit")
    records, by_date = [], {}
    for fold in folds:
        train, test = samples.iloc[fold.train_indices], samples.iloc[fold.test_indices]
        model = model_factories(config["seed"])["logistic"]()
        with warnings.catch_warnings(record=True) as fit_messages:
            warnings.simplefilter("always")
            model.fit(train[["queue_imbalance"]], train["target"])
        class_index = int(np.flatnonzero(model.classes_ == 1)[0])
        predictions = {
            "queue_logistic": model.predict_proba(test[["queue_imbalance"]])[:, class_index],
            "empirical_prior": np.full(len(test), float(train["target"].mean())),
            "paper_constant_half": np.full(len(test), 0.5),
        }
        metrics = {key: binary_probability_metrics(test["target"], probability)
                   for key, probability in predictions.items()}
        metrics["queue_logistic"]["fit_warnings"] = [
            f"{message.category.__name__}: {message.message}" for message in fit_messages
        ]
        day = fold.test_dates[0]
        by_date[day] = metrics
        records.append({
            "name": fold.name, "train_dates": list(fold.train_dates), "test_dates": [day],
            "train_count": len(train), "test_count": len(test),
            "purged_count": fold.purged_count, "audit": fold.audit,
            "empirical_training_up_probability": float(train["target"].mean()),
            "models": metrics,
        })
    summary = {}
    for model_id in ADAPTATION_MODELS:
        values = [day[model_id] for day in by_date.values()]
        summary[model_id] = {
            "date_count": len(values), "support": sum(value["support"] for value in values),
            "brier_score_mean": float(np.mean([value["brier_score"] for value in values])),
            "log_loss_mean": float(np.mean([value["log_loss"] for value in values])),
            "accuracy_mean": float(np.mean([value["accuracy"] for value in values])),
            "roc_auc_mean": float(np.mean([value["roc_auc"] for value in values if value["roc_auc"] is not None]))
            if any(value["roc_auc"] is not None for value in values) else None,
        }
    result = {
        "schema_version": 1, "scope": "development_only_methodological_adaptation",
        "numerical_reproduction": False, "paper": {
            "title": "Queue Imbalance as a One-Tick-Ahead Price Predictor in a Limit Order Book",
            "authors": ["Martin D. Gould", "Julius Bonart"], "arxiv": "1512.03492",
            "version": "v1 (2015-12)", "url": PAPER_URL,
            "idea": "Predict the binary next nonzero midpoint move using opposing top-queue imbalance.",
            "original_market": "10 Nasdaq stocks during 2014 using LOBSTER data",
            "original_global_logistic": "unpenalized maximum likelihood",
            "original_null": "constant up probability 0.5; Brier score 0.25",
        },
        "differences_from_paper": [
            "Bitstamp BTCUSD spot on newly selected fixed date/window excerpts, rather than the paper's equity data.",
            "One causal decision at each constant-midpoint run start instead of random within-run clock-time sampling.",
            "Expanding earlier-date development fits instead of a randomized train/test partition.",
            "Fixed C=1 regularized logistic with train-only scaling instead of unpenalized global logistic fitting.",
            "No local-logistic variant, paper sample-size matching or claimed match to published numerical tables.",
        ],
        "model_specification": model_specifications(config["seed"])["logistic"],
        "feature_columns": ["queue_imbalance"], "quality": quality,
        "labelled_dates": permitted_dates, "reserved_dates_not_labelled": config["final_dates"],
        "folds": records, "by_date": by_date, "summary": summary,
        "warnings": [
            "This is a methodological adaptation, not an exact numerical reproduction or independent final test.",
            "Empirical prior uses only each fold's training labels; paper constant-half null is also retained.",
            "Probability metrics are descriptive date means; no IID-row interval or profitability claim is made.",
        ],
    }
    for fold in records:
        result["warnings"].extend(
            f"{fold['name']}/queue_logistic: {message}"
            for message in fold["models"]["queue_logistic"]["fit_warnings"]
        )
    return result
