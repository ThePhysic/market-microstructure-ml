"""Outcome-free, date/window coverage gates; no labels or model metrics."""
from __future__ import annotations

from typing import Any, Iterable

import pandas as pd

from ..data import DataIntegrityError
from .acquisition import DEFAULT_WINDOWS, DEFAULT_WINDOW_SECONDS, validate_selection
from .storage import validate_states


def summarize_coverage(
    states: pd.DataFrame, manifests: Iterable[dict[str, Any]], *,
    windows: Iterable[int] = DEFAULT_WINDOWS, window_seconds: int = DEFAULT_WINDOW_SECONDS,
    min_window_rows: int = 100, min_window_span_seconds: float = 840,
    max_edge_gap_seconds: float = 60, max_excluded_fraction: float = 0.01,
) -> dict[str, Any]:
    """Objective eligibility, separate from feed-completeness or target support.

    Defaults require at least 100 valid states spanning 14 of 15 minutes with
    each edge within 60 seconds. A passing span is not evidence of no outages.
    The caller must freeze these bounds before fitting, not adapt them to scores.
    """
    validate_states(states)
    starts = validate_selection(windows, window_seconds)
    if (type(min_window_rows) is not int or min_window_rows <= 0
            or not 0 <= min_window_span_seconds <= window_seconds
            or not 0 <= max_edge_gap_seconds <= window_seconds
            or not 0 <= max_excluded_fraction <= 1):
        raise DataIntegrityError("Invalid objective coverage thresholds")
    sources = sorted(list(manifests), key=lambda m: m["date"])
    if not sources or len({m["date"] for m in sources}) != len(sources):
        raise DataIntegrityError("Coverage requires one manifest per unique date")
    expected_dates = [m["date"] for m in sources]
    if sorted(states["session_date"].unique().tolist()) != expected_dates:
        raise DataIntegrityError("Observed normalized dates differ from predeclared sources")
    results = []
    for manifest in sources:
        if manifest["selection"]["window_starts_utc_seconds"] != list(starts) or manifest["selection"]["window_seconds"] != window_seconds:
            raise DataIntegrityError("Coverage selection differs from source contract")
        date_frame = states.loc[states["session_date"] == manifest["date"]]
        seconds = (date_frame["receive_time_us"] % 86_400_000_000) / 1_000_000
        window_results = []
        for index, start in enumerate(starts):
            frame = date_frame.loc[(seconds >= start) & (seconds < start + window_seconds)]
            offsets = (frame["receive_time_us"] % 86_400_000_000) / 1_000_000 - start
            first = float(offsets.iloc[0]) if len(frame) else None
            last = float(offsets.iloc[-1]) if len(frame) else None
            span = last - first if first is not None else 0.0
            reasons = []
            if len(frame) < min_window_rows:
                reasons.append("insufficient_valid_states")
            if span < min_window_span_seconds:
                reasons.append("insufficient_window_span")
            if first is None or first > max_edge_gap_seconds or window_seconds - last > max_edge_gap_seconds:
                reasons.append("window_edge_coverage")
            segment_lengths = frame.groupby("segment_id", sort=False).size()
            window_results.append({"window_index": index, "window_start_utc_seconds": start,
                "valid_states": len(frame), "first_offset_seconds": first, "last_offset_seconds": last,
                "observed_span_seconds": span, "segments": len(segment_lengths),
                "segments_with_at_least_31_states": int((segment_lengths >= 31).sum()),
                "eligible": not reasons, "reasons": reasons})
        excluded = manifest["retained_rows"] - len(date_frame)
        fraction = excluded / manifest["retained_rows"] if manifest["retained_rows"] else 1.0
        reasons = []
        if fraction < 0 or fraction > max_excluded_fraction:
            reasons.append("excluded_fraction")
        if not all(w["eligible"] for w in window_results):
            reasons.append("ineligible_window")
        results.append({"date": manifest["date"], "valid_states": len(date_frame), "excluded_states": excluded,
                        "excluded_fraction": fraction, "windows": window_results,
                        "eligible": not reasons, "reasons": reasons})
    return {"schema_version": 1, "eligible": all(r["eligible"] for r in results),
            "dates": len(results), "windows": len(results) * len(starts), "valid_states": len(states),
            "sampled_seconds_per_date": len(starts) * window_seconds,
            "thresholds": {"min_window_rows": min_window_rows, "min_window_span_seconds": min_window_span_seconds,
                           "max_edge_gap_seconds": max_edge_gap_seconds, "max_excluded_fraction": max_excluded_fraction},
            "per_date": results, "warnings": [
                "Observed spans do not establish continuous source capture; CSV has no explicit disconnect markers.",
                "Noncontiguous first-of-month observations do not form a continuous backtest.",
                "Coverage gates examine no targets or predictive scores."]}
