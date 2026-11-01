"""Causal top-five order-book inputs and separate future event-horizon labels.

All availability timestamps are integer UTC microseconds.  Current-state inputs
include the snapshot received at the decision cutoff; trailing inputs use that
snapshot and earlier snapshots only.  A segment, source file, or calendar-date
boundary resets every window and prevents forward labels from crossing it.
"""

from __future__ import annotations

import numbers
from datetime import date
from typing import Any

import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "spread_ticks",
    "level1_imbalance",
    "depth5_imbalance",
    "bid_depth5",
    "ask_depth5",
    "mid_change_1_ticks",
    "mid_change_window_ticks",
    "mid_volatility_ticks",
    "spread_change_1_ticks",
    "imbalance_change_1",
]

FEATURE_DESCRIPTIONS = {
    "spread_ticks": "Best ask minus best bid, divided by the declared tick size.",
    "level1_imbalance": "(Best bid size - best ask size) / their sum; zero for zero total size.",
    "depth5_imbalance": "(Top-five bid depth - ask depth) / their sum; zero for zero total depth.",
    "bid_depth5": "Sum of five bid sizes, in the source instrument's native amount unit.",
    "ask_depth5": "Sum of five ask sizes, in the source instrument's native amount unit.",
    "mid_change_1_ticks": "Current mid-price minus the previous valid state's mid-price, in ticks.",
    "mid_change_window_ticks": "Current mid-price minus the mid-price trailing_window states earlier, in ticks.",
    "mid_volatility_ticks": "Population standard deviation (ddof=0) of the last trailing_window one-state mid changes, in ticks.",
    "spread_change_1_ticks": "Current minus previous spread, in ticks.",
    "imbalance_change_1": "Current minus previous top-five depth imbalance.",
}

_PROVENANCE = [
    "exchange", "symbol", "session_date", "segment_id", "source_file",
    "source_row_position", "provenance_key", "event_time_us",
    "receive_time_us", "source_order",
]
_BOOK_COLUMNS = [
    f"{side}_{kind}_{level}"
    for side in ("bid", "ask")
    for kind in ("price", "size")
    for level in range(1, 6)
]


def _positive_integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, numbers.Integral) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def _validate_states(states: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(states, pd.DataFrame):
        raise TypeError("states must be a pandas DataFrame")
    missing = sorted(set(_PROVENANCE + _BOOK_COLUMNS) - set(states.columns))
    if missing:
        raise ValueError(f"Missing normalized-state columns: {', '.join(missing)}")
    if states.empty:
        raise ValueError("Cannot construct samples from an empty state table")
    result = states.copy().reset_index(drop=True)
    if result[_PROVENANCE].isna().any().any():
        raise ValueError("Normalized-state provenance fields must not be missing")
    for column in ("event_time_us", "receive_time_us", "source_order", "source_row_position"):
        if not pd.api.types.is_integer_dtype(result[column].dtype):
            raise ValueError(f"{column} must contain integer values")
        values = result[column].to_numpy(dtype=np.int64)
        if np.any(values < 0) or (column in ("source_order", "source_row_position") and np.any(values == 0)):
            raise ValueError(f"{column} contains an invalid negative/zero value")
    if result["provenance_key"].duplicated().any():
        raise ValueError("provenance_key must uniquely identify each normalized source row")
    source_order = result["source_order"].to_numpy(dtype=np.int64)
    received = result["receive_time_us"].to_numpy(dtype=np.int64)
    if np.any(source_order[1:] <= source_order[:-1]):
        raise ValueError("States must retain strictly increasing source_order")
    if np.any(received[1:] < received[:-1]):
        raise ValueError("receive_time_us must be nondecreasing; timestamp ties retain source_order")
    expected_days = {}
    for value in result["session_date"].unique():
        try:
            parsed = date.fromisoformat(value) if isinstance(value, str) else None
        except ValueError:
            parsed = None
        if parsed is None or parsed.isoformat() != value:
            raise ValueError("session_date must use canonical YYYY-MM-DD strings")
        expected_days[value] = (parsed - date(1970, 1, 1)).days
    if np.any(received // 86_400_000_000 != result["session_date"].map(expected_days).to_numpy(dtype=np.int64)):
        raise ValueError("session_date must equal the UTC calendar date of receive_time_us")
    try:
        book = result[_BOOK_COLUMNS].to_numpy(dtype=np.float64)
    except (TypeError, ValueError) as error:
        raise ValueError("Book prices and sizes must be numeric") from error
    if not np.isfinite(book).all():
        raise ValueError("Book prices and sizes must be finite")
    for side in ("bid", "ask"):
        prices = result[[f"{side}_price_{level}" for level in range(1, 6)]].to_numpy(dtype=float)
        sizes = result[[f"{side}_size_{level}" for level in range(1, 6)]].to_numpy(dtype=float)
        if np.any(prices <= 0) or np.any(sizes < 0):
            raise ValueError("Book prices must be positive and sizes nonnegative")
        changes = np.diff(prices, axis=1)
        if (side == "bid" and np.any(changes >= 0)) or (side == "ask" and np.any(changes <= 0)):
            raise ValueError("Book levels must be strictly ordered: descending bids and ascending asks")
    if np.any(result["bid_price_1"].to_numpy() >= result["ask_price_1"].to_numpy()):
        raise ValueError("Crossed or locked books are not valid feature inputs")
    if result["exchange"].nunique() != 1 or result["symbol"].nunique() != 1:
        raise ValueError("One feature table must contain exactly one exchange and instrument")
    # Reusing a group after another group would silently join disconnected pieces.
    keys = list(result[["session_date", "segment_id", "source_file"]].itertuples(index=False, name=None))
    seen: set[tuple[Any, ...]] = set()
    previous = None
    for key in keys:
        if key != previous:
            if key in seen:
                raise ValueError("A normalized segment is noncontiguous in source order")
            seen.add(key)
            previous = key
    return result


def _ratio(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    return np.divide(numerator, denominator, out=np.zeros_like(numerator, dtype=float), where=denominator != 0)


def build_samples(
    states: pd.DataFrame,
    *,
    horizon_events: int = 10,
    threshold_ticks: float = 1,
    tick_size: float = 0.5,
    trailing_window: int = 20,
) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    """Return causal samples, explicit input names, and attributable exclusions.

    The future endpoint is exactly H subsequent supplied valid states inside the
    same contiguous source segment.  The caller must not downsample or shuffle
    normalized states before this function without declaring a new data contract.
    A target is +1 / -1 only for a move strictly beyond +/-threshold_ticks; equal
    boundary moves are unchanged.  Warm-up exclusion precedes end-of-segment
    exclusion so exclusion counts partition all supplied states exactly once.
    """
    horizon_events = _positive_integer(horizon_events, "horizon_events")
    trailing_window = _positive_integer(trailing_window, "trailing_window")
    if isinstance(tick_size, bool) or not isinstance(tick_size, numbers.Real) or not np.isfinite(tick_size) or tick_size <= 0:
        raise ValueError("tick_size must be finite and positive")
    if isinstance(threshold_ticks, bool) or not isinstance(threshold_ticks, numbers.Real) or not np.isfinite(threshold_ticks) or threshold_ticks < 0:
        raise ValueError("threshold_ticks must be finite and nonnegative")
    threshold_price = float(threshold_ticks) * float(tick_size)
    if not np.isfinite(threshold_price):
        raise ValueError("The price threshold must be finite")
    normalized = _validate_states(states)
    pieces: list[pd.DataFrame] = []
    excluded: list[dict[str, Any]] = []
    counts = {"insufficient_history": 0, "future_unavailable": 0}
    zero_l1 = 0
    zero_depth = 0
    groups = normalized.groupby(["session_date", "segment_id", "source_file"], sort=False, dropna=False)
    segment_count = 0
    for _, group in groups:
        segment_count += 1
        group = group.reset_index(drop=True)
        size = len(group)
        best_bid = group["bid_price_1"].to_numpy(dtype=float)
        best_ask = group["ask_price_1"].to_numpy(dtype=float)
        mid = (best_bid + best_ask) / 2
        spread = (best_ask - best_bid) / float(tick_size)
        bid_depth = group[[f"bid_size_{level}" for level in range(1, 6)]].sum(axis=1).to_numpy(dtype=float)
        ask_depth = group[[f"ask_size_{level}" for level in range(1, 6)]].sum(axis=1).to_numpy(dtype=float)
        bid1 = group["bid_size_1"].to_numpy(dtype=float)
        ask1 = group["ask_size_1"].to_numpy(dtype=float)
        total1 = bid1 + ask1
        total_depth = bid_depth + ask_depth
        zero_l1 += int(np.sum(total1 == 0))
        zero_depth += int(np.sum(total_depth == 0))
        imbalance = _ratio(bid_depth - ask_depth, total_depth)
        changes = pd.Series(mid).diff() / float(tick_size)
        current = group.copy()
        current["spread_ticks"] = spread
        current["level1_imbalance"] = _ratio(bid1 - ask1, total1)
        current["depth5_imbalance"] = imbalance
        current["bid_depth5"] = bid_depth
        current["ask_depth5"] = ask_depth
        current["mid_change_1_ticks"] = changes
        current["mid_change_window_ticks"] = (pd.Series(mid) - pd.Series(mid).shift(trailing_window)) / float(tick_size)
        current["mid_volatility_ticks"] = changes.rolling(trailing_window, min_periods=trailing_window).std(ddof=0)
        current["spread_change_1_ticks"] = pd.Series(spread).diff()
        current["imbalance_change_1"] = pd.Series(imbalance).diff()
        eligible = np.arange(trailing_window, max(trailing_window, size - horizon_events))
        for position in range(size):
            reason = "insufficient_history" if position < trailing_window else (
                "future_unavailable" if position + horizon_events >= size else None
            )
            if reason is not None:
                counts[reason] += 1
                excluded.append({
                    "source_order": int(group.at[position, "source_order"]),
                    "provenance_key": str(group.at[position, "provenance_key"]),
                    "reason": reason,
                })
        if not len(eligible):
            continue
        future = eligible + horizon_events
        chosen = current.iloc[eligible].copy()
        delta = mid[future] - mid[eligible]
        chosen["feature_cutoff_time"] = group["receive_time_us"].to_numpy(dtype=np.int64)[eligible]
        chosen["label_end_time"] = group["receive_time_us"].to_numpy(dtype=np.int64)[future]
        chosen["feature_order"] = group["source_order"].to_numpy(dtype=np.int64)[eligible]
        chosen["label_end_order"] = group["source_order"].to_numpy(dtype=np.int64)[future]
        chosen["label_end_source_row_position"] = group["source_row_position"].to_numpy(dtype=np.int64)[future]
        chosen["label_provenance_key"] = group["provenance_key"].to_numpy()[future]
        chosen["label_segment_id"] = group["segment_id"].to_numpy()[future]
        chosen["label_session_date"] = group["session_date"].to_numpy()[future]
        chosen["label_source_file"] = group["source_file"].to_numpy()[future]
        chosen["target"] = np.where(delta > threshold_price, 1, np.where(delta < -threshold_price, -1, 0)).astype(np.int8)
        if not np.isfinite(chosen[FEATURE_COLUMNS].to_numpy(dtype=float)).all():
            raise ValueError("A computed feature is nonfinite; inspect source scale and declared units")
        pieces.append(chosen)
    if pieces:
        samples = pd.concat(pieces, ignore_index=True)
    else:
        extra = FEATURE_COLUMNS + [
            "feature_cutoff_time", "label_end_time", "feature_order", "label_end_order",
            "label_end_source_row_position", "label_provenance_key", "label_segment_id",
            "label_session_date", "label_source_file", "target",
        ]
        samples = pd.DataFrame(columns=list(normalized.columns) + extra)
    quality: dict[str, Any] = {
        "input_rows": len(normalized),
        "retained_samples": len(samples),
        "excluded_samples": len(normalized) - len(samples),
        "exclusions": counts,
        "exclusion_rows": excluded,
        "segments": segment_count,
        "horizon_events": horizon_events,
        "threshold_ticks": float(threshold_ticks),
        "tick_size": float(tick_size),
        "trailing_window": trailing_window,
        "zero_l1_denominator_states": zero_l1,
        "zero_depth_denominator_states": zero_depth,
        "zero_denominator_policy": "Use zero imbalance when both opposing sizes/depths are zero.",
        "information_time": "receive_time_us; ties retain ascending source_order",
        "volatility_definition": "Population std(ddof=0) of the last trailing_window one-state mid-price changes in ticks.",
        "feature_columns": list(FEATURE_COLUMNS),
    }
    assert sum(counts.values()) == quality["excluded_samples"]
    return samples, list(FEATURE_COLUMNS), quality
