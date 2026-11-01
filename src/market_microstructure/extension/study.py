"""Frozen chronological research with local causal signals and aggregate results.

Pilot construction excludes the reserved dates before feature/target creation.
Final evaluation is prequential: prior final labels become eligible at the next
scheduled date, with no intermediate score-dependent choices.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from decimal import Decimal, InvalidOperation
from numbers import Integral, Real
import re
from typing import Any
import warnings

import numpy as np
import pandas as pd

from market_microstructure.evaluation import evaluate_predictions
from market_microstructure.features import FEATURE_COLUMNS, _ratio, _validate_states, build_samples
from market_microstructure.models import model_factories, model_specifications
from market_microstructure.splits import Fold, audit_fold
from .statistics import paired_block_bootstrap, pilot_precision_plan, practical_effect_decision

HISTORY_COLUMNS = ["mid_change_1_ticks", "mid_change_window_ticks", "mid_volatility_ticks"]
MODEL_IDS = ("majority", "history_logistic", "book_logistic", "boosted")
CONFIG_KEYS = {
    "schema_version", "stage", "dates", "initial_train_dates", "development_dates",
    "final_dates", "exchange", "symbol", "horizon_events", "threshold_ticks",
    "tick_size", "trailing_window", "seed", "practical_delta", "confidence",
    "block_length_dates", "precision_half_width", "min_final_blocks", "n_resamples",
    "protocol_sha256", "frozen_source_revision", "final_scoring_authorized",
    "precision_gate_status", "target_position", "max_holding_events", "inference_delay_us",
}


def _dates(values: Any, name: str) -> list[str]:
    if not isinstance(values, list) or not values:
        raise ValueError(f"{name} must be a nonempty ordered list of dates")
    try:
        valid = all(isinstance(value, str) and date.fromisoformat(value).isoformat() == value for value in values)
    except ValueError:
        valid = False
    if not valid or sorted(set(values)) != values:
        raise ValueError(f"{name} must contain unique chronological canonical dates")
    return list(values)


def validate_research_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the flat research object, including the outer freeze attestation.

    Binding the attestation to actual repository/protocol bytes is the caller's
    responsibility; this function rejects missing attestations before any fit.
    """
    if not isinstance(config, Mapping):
        raise ValueError("research config must be a mapping")
    unknown, missing = set(config) - CONFIG_KEYS, CONFIG_KEYS - set(config)
    if unknown or missing:
        raise ValueError(f"Research config keys differ: unknown={sorted(unknown)}, missing={sorted(missing)}")
    result = dict(config)
    if result["schema_version"] != 1 or isinstance(result["schema_version"], bool):
        raise ValueError("Unsupported research schema_version")
    if result["stage"] not in ("pilot", "final"):
        raise ValueError("stage must be pilot or final")
    for key in ("initial_train_dates", "horizon_events", "trailing_window",
                "block_length_dates", "min_final_blocks", "n_resamples", "max_holding_events"):
        value = result[key]
        if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
            raise ValueError(f"{key} must be a positive integer")
        result[key] = int(value)
    if result["min_final_blocks"] < 2 or not 100 <= result["n_resamples"] <= 100_000:
        raise ValueError("At least two final blocks and 100..100000 resamples are required")
    if isinstance(result["seed"], bool) or not isinstance(result["seed"], Integral) or not 0 <= result["seed"] < 2**32:
        raise ValueError("seed must be an integer from zero to 2**32-1")
    result["seed"] = int(result["seed"])
    for key in ("tick_size", "practical_delta", "confidence", "precision_half_width"):
        value = result[key]
        if isinstance(value, bool) or not isinstance(value, Real) or not np.isfinite(value) or value <= 0:
            raise ValueError(f"{key} must be finite and positive")
        result[key] = float(value)
    if result["confidence"] >= 1 or result["practical_delta"] >= 1:
        raise ValueError("confidence and practical_delta must be below one")
    threshold = result["threshold_ticks"]
    if isinstance(threshold, bool) or not isinstance(threshold, Real) or not np.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold_ticks must be finite and nonnegative")
    result["threshold_ticks"] = float(threshold)
    for key in ("exchange", "symbol"):
        if not isinstance(result[key], str) or not result[key].strip():
            raise ValueError(f"{key} must be a nonempty string")
    all_dates = _dates(result["dates"], "dates")
    development = _dates(result["development_dates"], "development_dates")
    final = _dates(result["final_dates"], "final_dates")
    initial = all_dates[:result["initial_train_dates"]]
    if len(initial) != result["initial_train_dates"] or initial + development + final != all_dates:
        raise ValueError("Initial, development and final dates must partition the declared dates chronologically")
    if len(final) // result["block_length_dates"] < result["min_final_blocks"]:
        raise ValueError("Declared final coverage has fewer than min_final_blocks")
    if not isinstance(result["protocol_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", result["protocol_sha256"]):
        raise ValueError("A frozen protocol_sha256 is required before fitting")
    if not isinstance(result["frozen_source_revision"], str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", result["frozen_source_revision"]):
        raise ValueError("A frozen source revision is required before fitting")
    if not isinstance(result["final_scoring_authorized"], bool):
        raise ValueError("final_scoring_authorized must be boolean")
    if result["precision_gate_status"] not in ("pending", "adequate", "exploratory_only_acknowledged"):
        raise ValueError("Unknown precision_gate_status")
    if result["stage"] == "pilot" and result["final_scoring_authorized"]:
        raise ValueError("Pilot must not authorize final scoring")
    if result["stage"] == "final" and (
        not result["final_scoring_authorized"] or result["precision_gate_status"] == "pending"
    ):
        raise ValueError("Final scoring needs explicit authorization and a reviewed precision gate")
    delay = result["inference_delay_us"]
    if isinstance(delay, bool) or not isinstance(delay, Integral) or delay != 0:
        raise ValueError("inference_delay_us must be zero; execution latency belongs to the simulator")
    if not isinstance(result["target_position"], str):
        raise ValueError("target_position must be a positive decimal string")
    try:
        quantity = Decimal(result["target_position"])
    except InvalidOperation as error:
        raise ValueError("target_position must be a positive decimal string") from error
    if not quantity.is_finite() or quantity <= 0:
        raise ValueError("target_position must be a positive decimal string")
    return result


def validate_state_coverage(states: pd.DataFrame, config: Mapping[str, Any]) -> pd.DataFrame:
    """Inspect schema/coverage only; do not construct reserved-date targets."""
    normalized = _validate_states(states)
    observed = list(normalized["session_date"].drop_duplicates())
    if observed != config["dates"]:
        missing = sorted(set(config["dates"]) - set(observed))
        extra = sorted(set(observed) - set(config["dates"]))
        raise ValueError(f"State date coverage differs from the frozen selection: missing={missing}, extra={extra}")
    if normalized["exchange"].iloc[0] != config["exchange"] or normalized["symbol"].iloc[0] != config["symbol"]:
        raise ValueError("States disagree with frozen exchange/symbol")
    return normalized


def make_date_fold(samples: pd.DataFrame, name: str, train_dates: list[str], test_date: str) -> Fold:
    """Use the shared audit with explicit purging on both time and source order."""
    candidate = np.flatnonzero(samples["session_date"].isin(train_dates).to_numpy())
    test = np.flatnonzero(samples["session_date"].eq(test_date).to_numpy())
    if not len(candidate) or not len(test):
        raise ValueError(f"{name}: a declared partition has no eligible samples")
    boundary = int(samples.iloc[test]["feature_cutoff_time"].min())
    order_boundary = int(samples.iloc[test]["feature_order"].min())
    keep = (
        (samples.iloc[candidate]["label_end_time"].to_numpy() < boundary)
        & (samples.iloc[candidate]["label_end_order"].to_numpy() < order_boundary)
    )
    train = candidate[keep]
    actual_dates = tuple(samples.iloc[train]["session_date"].drop_duplicates())
    if actual_dates != tuple(train_dates):
        raise ValueError(f"{name}: purging removes all eligible samples from a declared train date")
    fold = Fold(name, train, test, actual_dates, (test_date,), int((~keep).sum()))
    object.__setattr__(fold, "audit", audit_fold(samples, fold))
    return fold


def causal_feature_frame(states: pd.DataFrame, *, tick_size: float, trailing_window: int) -> pd.DataFrame:
    """Current/past-only features for every state after trailing warm-up.

    This frame deliberately has no future target and does not remove the last
    horizon observations. Execution eligibility must not depend on whether a
    later price/segment observation exists.
    """
    if isinstance(tick_size, bool) or not isinstance(tick_size, Real) or not np.isfinite(tick_size) or tick_size <= 0:
        raise ValueError("tick_size must be finite and positive")
    if isinstance(trailing_window, bool) or not isinstance(trailing_window, Integral) or trailing_window < 1:
        raise ValueError("trailing_window must be a positive integer")
    normalized = _validate_states(states)
    pieces = []
    for _, group in normalized.groupby(["session_date", "segment_id", "source_file"], sort=False):
        group = group.reset_index(drop=True)
        bid = group["bid_price_1"].to_numpy(dtype=float)
        ask = group["ask_price_1"].to_numpy(dtype=float)
        mid = (bid + ask) / 2
        spread = (ask - bid) / float(tick_size)
        bid1 = group["bid_size_1"].to_numpy(dtype=float)
        ask1 = group["ask_size_1"].to_numpy(dtype=float)
        bid_depth = group[[f"bid_size_{level}" for level in range(1, 6)]].sum(axis=1).to_numpy(dtype=float)
        ask_depth = group[[f"ask_size_{level}" for level in range(1, 6)]].sum(axis=1).to_numpy(dtype=float)
        imbalance = _ratio(bid_depth - ask_depth, bid_depth + ask_depth)
        changes = pd.Series(mid).diff() / float(tick_size)
        current = group.copy()
        current["spread_ticks"] = spread
        current["level1_imbalance"] = _ratio(bid1 - ask1, bid1 + ask1)
        current["depth5_imbalance"] = imbalance
        current["bid_depth5"] = bid_depth
        current["ask_depth5"] = ask_depth
        current["mid_change_1_ticks"] = changes
        current["mid_change_window_ticks"] = (pd.Series(mid) - pd.Series(mid).shift(trailing_window)) / float(tick_size)
        current["mid_volatility_ticks"] = changes.rolling(trailing_window, min_periods=trailing_window).std(ddof=0)
        current["spread_change_1_ticks"] = pd.Series(spread).diff()
        current["imbalance_change_1"] = pd.Series(imbalance).diff()
        current["feature_cutoff_time"] = current["receive_time_us"].astype(np.int64)
        current["feature_order"] = current["source_order"].astype(np.int64)
        eligible = current.iloc[trailing_window:].copy()
        if len(eligible):
            if not np.isfinite(eligible[FEATURE_COLUMNS].to_numpy(dtype=float)).all():
                raise ValueError("A causal execution feature is nonfinite")
            pieces.append(eligible)
    if not pieces:
        raise ValueError("No causal feature decisions are available after warm-up")
    return pd.concat(pieces, ignore_index=True)


def exact_midpoint_units(states: pd.DataFrame, tick_size: float) -> pd.Series:
    """Exact integer half-tick midpoints keyed by original source order.

    Decimal text conversion preserves the declared normalized quote grid.
    Reject off-grid values rather than rounding an observed price or inventing
    a boundary tolerance. The safe bound also prevents int64 arithmetic overflow.
    """
    try:
        tick = Decimal(str(tick_size))
    except InvalidOperation as error:
        raise ValueError("tick_size must be finite and positive") from error
    if not tick.is_finite() or tick <= 0:
        raise ValueError("tick_size must be finite and positive")
    if states["source_order"].duplicated().any():
        raise ValueError("Exact midpoint mapping needs unique source_order")
    cache: dict[Any, int] = {}
    def integer_ticks(value: Any) -> int:
        if value in cache:
            return cache[value]
        try:
            price = Decimal(str(value))
            ratio = price / tick
        except InvalidOperation as error:
            raise ValueError("Best quotes must be finite prices on the declared tick grid") from error
        if (
            not price.is_finite() or price <= 0 or not ratio.is_finite()
            or ratio != ratio.to_integral_value() or abs(ratio) >= 2**52
        ):
            raise ValueError("Best quotes must lie exactly on the declared safe integer tick grid")
        result = int(ratio)
        cache[value] = result
        return result
    values = np.fromiter(
        (integer_ticks(bid) + integer_ticks(ask)
         for bid, ask in states[["bid_price_1", "ask_price_1"]].itertuples(index=False, name=None)),
        dtype=np.int64, count=len(states),
    )
    return pd.Series(values, index=states["source_order"].to_numpy(), name="midpoint_half_ticks")


def build_research_samples(states: pd.DataFrame, **kwargs: Any) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    """Reuse legacy sample eligibility/features and replace float-boundary labels."""
    samples, columns, quality = build_samples(states, **kwargs)
    midpoint = exact_midpoint_units(states, kwargs.get("tick_size", 0.5))
    threshold = 2 * Decimal(str(kwargs.get("threshold_ticks", 1)))
    if not threshold.is_finite() or threshold < 0:
        raise ValueError("threshold_ticks must be finite and nonnegative")
    if len(samples):
        future = midpoint.loc[samples["label_end_order"].to_numpy()].to_numpy(dtype=np.int64)
        current = midpoint.loc[samples["feature_order"].to_numpy()].to_numpy(dtype=np.int64)
        delta = future - current
        samples["target"] = np.fromiter(
            (1 if int(change) > threshold else -1 if int(change) < -threshold else 0 for change in delta),
            dtype=np.int8, count=len(samples),
        )
    quality.update(
        target_arithmetic="exact Decimal quote-grid integers; midpoint changes in integer half-ticks",
        threshold_half_ticks=str(threshold),
        target_boundary_policy="Exact equality at either threshold is unchanged.",
        target_class_support={str(label): int(samples["target"].eq(label).sum()) for label in (-1, 0, 1)},
    )
    return samples, columns, quality


def _preflight(samples: pd.DataFrame, dates: list[str], folds: list[Fold], columns: list[str]) -> None:
    if list(samples["session_date"].drop_duplicates()) != dates:
        raise ValueError("Feature eligibility must represent every permitted date before any fit")
    if not np.isfinite(samples[columns].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite model features")
    for fold in folds:
        if samples.iloc[fold.train_indices]["target"].nunique() < 2:
            raise ValueError(f"{fold.name}: logistic training needs at least two target classes before any fit")


def _signals(samples: pd.DataFrame, predictions: np.ndarray, model_id: str,
             train_label_end: int, config: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Cap consecutive long target decisions; this is not a fill holding guarantee."""
    records = []
    consecutive = 0
    prior_group = None
    for row, prediction in zip(samples.itertuples(index=False), predictions, strict=True):
        group = (row.session_date, row.segment_id, row.source_file)
        if group != prior_group:
            consecutive = 0
            prior_group = group
        long = int(prediction) == 1 and consecutive < config["max_holding_events"]
        consecutive = consecutive + 1 if long else 0
        available = int(row.receive_time_us)
        if train_label_end >= available or int(row.feature_cutoff_time) != available:
            raise ValueError("Signal training or feature timestamps violate information availability")
        records.append({
            "source_order": int(row.source_order), "available_time_us": available,
            "feature_cutoff_time_us": int(row.feature_cutoff_time),
            "train_label_end_time_us": train_label_end,
            "target_position": config["target_position"] if long else "0",
            "model_id": model_id,
        })
    return records


def _comparisons(by_date: dict[str, Any], config: Mapping[str, Any], *, final: bool) -> dict[str, Any]:
    pairs = (
        ("book_logistic_vs_history_logistic", "book_logistic", "history_logistic"),
        ("boosted_vs_book_logistic", "boosted", "book_logistic"),
    )
    result = {}
    for key, left, right in pairs:
        interval = paired_block_bootstrap(
            {day: metrics[left]["macro_f1"] for day, metrics in by_date.items()},
            {day: metrics[right]["macro_f1"] for day, metrics in by_date.items()},
            block_length=config["block_length_dates"], n_resamples=config["n_resamples"],
            confidence=config["confidence"], seed=config["seed"],
            min_blocks=config["min_final_blocks"] if final else 2,
        )
        interval.update(model_a=left, model_b=right,
                        role="primary" if left == "book_logistic" else "secondary")
        interval["decision"] = practical_effect_decision(interval, config["practical_delta"])
        result[key] = interval
    return result


def _section(samples: pd.DataFrame, decisions: pd.DataFrame, folds: list[Fold], columns: list[str],
             config: Mapping[str, Any], *, final: bool) -> tuple[dict[str, Any], dict[str, list]]:
    factories = model_factories(config["seed"])
    records, by_date = [], {}
    signals = {model: [] for model in MODEL_IDS}
    for fold in folds:
        train, test = samples.iloc[fold.train_indices], samples.iloc[fold.test_indices]
        decision = decisions.loc[decisions["session_date"].eq(fold.test_dates[0])]
        metrics = {}
        for model_id in MODEL_IDS:
            feature_columns = HISTORY_COLUMNS if model_id == "history_logistic" else columns
            factory_id = "logistic" if model_id in ("book_logistic", "history_logistic") else model_id
            model = factories[factory_id]()
            with warnings.catch_warnings(record=True) as fit_messages:
                warnings.simplefilter("always")
                model.fit(train[feature_columns], train["target"])
            prediction = model.predict(test[feature_columns])
            metrics[model_id] = evaluate_predictions(test["target"], prediction)
            metrics[model_id]["fit_warnings"] = [
                f"{message.category.__name__}: {message.message}" for message in fit_messages
            ]
            decision_prediction = model.predict(decision[feature_columns])
            signals[model_id].extend(_signals(
                decision, decision_prediction, model_id, int(train["label_end_time"].max()), config,
            ))
        day = fold.test_dates[0]
        by_date[day] = metrics
        records.append({
            "name": fold.name, "train_dates": list(fold.train_dates), "test_dates": [day],
            "train_count": len(train), "test_count": len(test),
            "execution_decision_count": len(decision),
            "purged_count": fold.purged_count, "audit": fold.audit, "models": metrics,
        })
    summary = {}
    for model_id in MODEL_IDS:
        scores = np.asarray([value[model_id]["macro_f1"] for value in by_date.values()])
        balanced = [value[model_id]["balanced_accuracy"] for value in by_date.values()]
        summary[model_id] = {
            "macro_f1_mean": float(scores.mean()),
            "macro_f1_std": float(scores.std(ddof=1)) if len(scores) > 1 else None,
            "balanced_accuracy_mean": float(np.mean(balanced)), "date_count": len(scores),
            "test_count": sum(value[model_id]["support"] for value in by_date.values()),
        }
    return {
        "schedule": (
            "predeclared prequential evaluation; prior final labels available for later scheduled fits"
            if final else "expanding earlier-date development fits"
        ),
        "folds": records, "by_date": by_date, "summary": summary,
        "comparisons": _comparisons(by_date, config, final=final),
    }, signals


def run_study(states: pd.DataFrame, config: Mapping[str, Any]) -> dict[str, Any]:
    """Return {'aggregate': JSON-safe aggregate study, 'signals': local records}.

    The caller must attest that protocol/source fingerprints are bound to the
    reviewed bytes. This function never writes files or exports fitted models.
    """
    config = validate_research_config(config)
    normalized = validate_state_coverage(states, config)
    permitted_dates = config["dates"] if config["stage"] == "final" else [
        day for day in config["dates"] if day not in set(config["final_dates"])
    ]
    permitted = normalized.loc[normalized["session_date"].isin(permitted_dates)]
    samples, columns, quality = build_research_samples(
        permitted, horizon_events=config["horizon_events"],
        threshold_ticks=config["threshold_ticks"], tick_size=config["tick_size"],
        trailing_window=config["trailing_window"],
    )
    decisions = causal_feature_frame(
        permitted, tick_size=config["tick_size"], trailing_window=config["trailing_window"],
    )
    dev_folds = [
        make_date_fold(samples, f"development_{index:02d}",
                       [date for date in permitted_dates if date < day], day)
        for index, day in enumerate(config["development_dates"], 1)
    ]
    final_folds = [] if config["stage"] == "pilot" else [
        make_date_fold(samples, f"final_{index:02d}",
                       [date for date in permitted_dates if date < day], day)
        for index, day in enumerate(config["final_dates"], 1)
    ]
    # Preflight every scheduled fold before the first fit, including the final schedule.
    _preflight(samples, permitted_dates, dev_folds + final_folds, columns)
    development, signals = _section(samples, decisions, dev_folds, columns, config, final=False)
    precision = pilot_precision_plan(
        {day: value["book_logistic"]["macro_f1"] for day, value in development["by_date"].items()},
        {day: value["history_logistic"]["macro_f1"] for day, value in development["by_date"].items()},
        planned_final_dates=len(config["final_dates"]),
        block_length=config["block_length_dates"], target_half_width=config["precision_half_width"],
        confidence=config["confidence"], min_final_blocks=config["min_final_blocks"],
    )
    final_result = None
    if final_folds:
        if not precision["estimated_precision_adequate"] and config["precision_gate_status"] != "exploratory_only_acknowledged":
            raise ValueError("Pilot precision is insufficient; final needs the explicit exploratory acknowledgment")
        final_result, final_signals = _section(samples, decisions, final_folds, columns, config, final=True)
        for model in MODEL_IDS:
            signals[model].extend(final_signals[model])
        primary = final_result["comparisons"]["book_logistic_vs_history_logistic"]
        actual_precision = primary["half_width"] is not None and primary["half_width"] <= config["precision_half_width"]
        final_result["precision_target_met"] = bool(precision["estimated_precision_adequate"] and actual_precision)
        final_result["research_decisiveness_met"] = bool(
            final_result["precision_target_met"]
            and primary["decision"]["status"] not in ("indeterminate", "insufficient_uncertainty_evidence")
        )
        final_result["claim_status"] = (
            primary["decision"]["status"] if final_result["precision_target_met"]
            else "exploratory_precision_unmet"
        )
    aggregate = {
        "schema_version": 1, "stage": config["stage"], "config": config,
        "coverage": {"expected_dates": config["dates"], "observed_dates": config["dates"],
                     "labelled_dates": permitted_dates, "reserved_final_dates": config["final_dates"]},
        "feature_columns": {"history_logistic": HISTORY_COLUMNS, "book_models": columns},
        "model_specifications": model_specifications(config["seed"]),
        "quality": {
            **{key: value for key, value in quality.items() if key != "exclusion_rows"},
            "causal_execution_decisions": len(decisions),
            "execution_tail_policy": "Emit decisions after warm-up including all last-horizon states; future target availability only restricts training and classification metrics.",
        },
        "development": development, "precision_plan": precision, "final": final_result,
        "signal_policy": {
            "target_long_quantity": config["target_position"],
            "description": "Predicted up requests long; down/unchanged requests flat. After the configured maximum consecutive long decisions, force one flat target before another long request.",
            "maximum_consecutive_long_decisions": config["max_holding_events"],
            "inference_delay_us": 0,
            "limitation": "This cap is a decision rule, not an execution holding-time guarantee. Pending IOC orders and segment-end unresolved inventory remain explicit simulator limitations. Execution decisions include the unlabelled last-horizon states.",
        },
        "warnings": [
            "One venue/instrument and fixed two-hour excerpts per selected date; results do not establish continuous-day or cross-market generalization.",
            "Date-block uncertainty remains conditional on dependence/stationarity assumptions; shared expanding fits may induce longer dependence.",
            "Macro-F1 uses all three fixed classes; balanced accuracy averages classes present on each true evaluation date.",
            "Classification evidence is not evidence of executable profit. Economic results require the separate declared simulator and costs.",
            "Local signals and fitted models are excluded from published aggregate artifacts.",
        ],
    }
    for section in (development, final_result):
        if section is not None:
            for fold in section["folds"]:
                for model_id, metrics in fold["models"].items():
                    for message in metrics["fit_warnings"]:
                        aggregate["warnings"].append(f"{fold['name']}/{model_id}: {message}")
    return {"aggregate": aggregate, "signals": signals}
