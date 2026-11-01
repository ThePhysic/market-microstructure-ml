"""Paired date-block uncertainty and a pilot-only precision/stopping plan.

Dates are the resampling units, never individual book updates. Contiguous
blocks preserve some adjacent-date dependence; they do not prove stationarity
or account for every dependence caused by overlapping training histories.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
import math
from numbers import Integral, Real
from statistics import NormalDist
from typing import Any

import numpy as np


def _integer(value: Any, name: str, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _positive(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not np.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return float(value)


def _confidence(value: Any) -> float:
    value = _positive(value, "confidence")
    if value >= 1:
        raise ValueError("confidence must be strictly between zero and one")
    return value


def _scores(scores: Mapping[str, float], name: str) -> dict[str, float]:
    if not isinstance(scores, Mapping) or not scores:
        raise ValueError(f"{name} must map observed dates to scores")
    result = {}
    for unit, value in scores.items():
        try:
            canonical = isinstance(unit, str) and date.fromisoformat(unit).isoformat() == unit
        except ValueError:
            canonical = False
        if not canonical:
            raise ValueError(f"{name} keys must be canonical observed YYYY-MM-DD dates")
        if isinstance(value, bool) or not isinstance(value, Real) or not np.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"{name} values must be finite scores between zero and one")
        result[unit] = float(value)
    return result


def _paired(scores_a: Mapping[str, float], scores_b: Mapping[str, float]):
    a, b = _scores(scores_a, "scores_a"), _scores(scores_b, "scores_b")
    if set(a) != set(b):
        raise ValueError("Paired comparisons require identical observed date IDs")
    units = sorted(a)
    return units, np.asarray([a[unit] - b[unit] for unit in units], dtype=float)


def paired_block_bootstrap(
    scores_a: Mapping[str, float],
    scores_b: Mapping[str, float],
    *,
    block_length: int = 3,
    n_resamples: int = 2000,
    confidence: float = 0.95,
    seed: int = 42,
    min_blocks: int = 2,
) -> dict[str, Any]:
    """Non-circular moving-block percentile interval of paired date means.

    Draw overlapping length-L blocks from chronological observed dates,
    concatenate draws and truncate to the original number of dates. Blocks do
    not wrap from the final date to the first. Observed-date gaps remain gaps.
    """
    units, differences = _paired(scores_a, scores_b)
    block_length = _integer(block_length, "block_length")
    min_blocks = _integer(min_blocks, "min_blocks", 2)
    n_resamples = _integer(n_resamples, "n_resamples", 100)
    if n_resamples > 100_000:
        raise ValueError("n_resamples must not exceed 100000")
    seed = _integer(seed, "seed", 0)
    if seed >= 2**32:
        raise ValueError("seed must be below 2**32")
    confidence = _confidence(confidence)
    n_dates = len(units)
    n_blocks = n_dates // block_length
    warnings = [
        "Exploratory moving-block date bootstrap; assumes suitable local stationarity and exchangeability of blocks.",
        "Adjacent observed dates may have calendar gaps; shared expanding training histories can create dependence beyond the chosen block length.",
        "No order-book rows are treated as IID observations.",
    ]
    result: dict[str, Any] = {
        "method": "paired_non_circular_moving_block_percentile_bootstrap",
        "metric": "macro_f1", "analysis_unit": "observed_date",
        "difference_direction": "scores_a_minus_scores_b",
        "units": units, "n_units": n_dates, "block_length_dates": block_length,
        "nonoverlapping_block_count": n_blocks, "minimum_blocks": min_blocks,
        "mean_difference": float(differences.mean()),
        "min_difference": float(differences.min()),
        "max_difference": float(differences.max()),
        "std_difference": float(differences.std(ddof=1)) if n_dates > 1 else None,
        "confidence": confidence, "ci_lower": None, "ci_upper": None,
        "half_width": None, "n_resamples": 0, "seed": seed,
        "status": "insufficient_blocks", "warnings": warnings,
    }
    if n_blocks < min_blocks:
        warnings.append(
            f"Only {n_blocks} nonoverlapping length-{block_length} date blocks; "
            f"at least {min_blocks} are required, so no interval is reported."
        )
        return result
    if n_blocks < 8:
        warnings.append("Fewer than eight nonoverlapping date blocks; interval stability is limited.")
    if np.ptp(differences) <= 1e-12:
        warnings.append("Observed date differences are identical; a zero-width interval does not establish generalization.")
    rng = np.random.default_rng(seed)
    draws_per_replication = math.ceil(n_dates / block_length)
    means = np.empty(n_resamples)
    offsets = np.arange(block_length)
    for start in range(0, n_resamples, 128):
        stop = min(start + 128, n_resamples)
        starts = rng.integers(
            0, n_dates - block_length + 1,
            size=(stop - start, draws_per_replication),
        )
        indices = (starts[..., None] + offsets).reshape(stop - start, -1)[:, :n_dates]
        means[start:stop] = differences[indices].mean(axis=1)
    tail = (1 - confidence) / 2
    lower, upper = np.quantile(means, [tail, 1 - tail])
    result.update(
        ci_lower=float(lower), ci_upper=float(upper),
        half_width=float((upper - lower) / 2),
        n_resamples=n_resamples, status="exploratory",
    )
    return result


def practical_effect_decision(interval: Mapping[str, Any], delta: float = 0.01) -> dict[str, Any]:
    """Classify the prespecified practical effect without forcing a winner."""
    delta = _positive(delta, "delta")
    lower, upper = interval.get("ci_lower"), interval.get("ci_upper")
    decision = {
        "practical_delta": delta, "positive_practical_gain": False,
        "rules_out_practical_gain": False, "equivalence_within_margin": False,
        "negative_practical_effect": False, "status": "indeterminate",
        "scope": "conditional on the declared date-block uncertainty assumptions",
    }
    if lower is None or upper is None:
        decision["status"] = "insufficient_uncertainty_evidence"
        return decision
    if not isinstance(lower, Real) or not isinstance(upper, Real) or not np.isfinite([lower, upper]).all() or lower > upper:
        raise ValueError("Interval bounds must be finite and ordered")
    positive = lower > delta
    ruled_out = upper < delta
    equivalent = lower >= -delta and upper <= delta
    negative = upper < -delta
    decision.update(
        positive_practical_gain=bool(positive),
        rules_out_practical_gain=bool(ruled_out),
        equivalence_within_margin=bool(equivalent),
        negative_practical_effect=bool(negative),
        status=(
            "positive_practical_gain" if positive else
            "equivalent_within_margin" if equivalent else
            "negative_practical_effect" if negative else
            "rules_out_practical_gain" if ruled_out else "indeterminate"
        ),
    )
    return decision


def pilot_precision_plan(
    scores_a: Mapping[str, float],
    scores_b: Mapping[str, float],
    *,
    planned_final_dates: int,
    block_length: int = 3,
    target_half_width: float = 0.015,
    confidence: float = 0.95,
    min_final_blocks: int = 8,
) -> dict[str, Any]:
    """Approximate final-date requirement from development block variability.

    This is planning, not a power guarantee. Use sample SD of nonoverlapping
    pilot block means and a normal approximation. Keep the minimum block floor
    even if the observed pilot variance is zero. Never revise final dates,
    margins or models after final scores are released.
    """
    units, differences = _paired(scores_a, scores_b)
    planned_final_dates = _integer(planned_final_dates, "planned_final_dates")
    block_length = _integer(block_length, "block_length")
    min_final_blocks = _integer(min_final_blocks, "min_final_blocks", 2)
    target_half_width = _positive(target_half_width, "target_half_width")
    confidence = _confidence(confidence)
    n_blocks = len(units) // block_length
    planned_blocks = planned_final_dates // block_length
    result: dict[str, Any] = {
        "method": "development_nonoverlapping_block_mean_SD_normal_approximation",
        "stage": "planning_only", "pilot_dates": units,
        "pilot_date_count": len(units), "pilot_block_count": n_blocks,
        "block_length_dates": block_length, "planned_final_dates": planned_final_dates,
        "planned_final_blocks": planned_blocks, "minimum_final_blocks": min_final_blocks,
        "confidence": confidence, "target_half_width": target_half_width,
        "pilot_block_mean_sd": None, "estimated_required_final_blocks": None,
        "estimated_required_final_dates": None, "estimated_final_half_width": None,
        "estimated_precision_adequate": False,
        "status": "insufficient_pilot_blocks",
        "positive_pilot_date_fraction": float(np.mean(differences > 0)),
        "mean_pilot_difference": float(differences.mean()),
        "warnings": [
            "Pilot precision estimates are approximate; they do not guarantee future variance, independence or achieved precision.",
            "Use all fixed final dates once. No optional stopping, margin changes or data extension based on intermediate final results.",
        ],
    }
    if n_blocks < 2:
        result["warnings"].append("Fewer than two complete pilot date blocks; no variance-based precision estimate.")
        return result
    blocks = differences[:n_blocks * block_length].reshape(n_blocks, block_length).mean(axis=1)
    sd = float(blocks.std(ddof=1))
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    required = max(min_final_blocks, math.ceil((z * sd / target_half_width) ** 2))
    estimate = z * sd / math.sqrt(planned_blocks) if planned_blocks else None
    result.update(
        pilot_block_mean_sd=sd,
        estimated_required_final_blocks=required,
        estimated_required_final_dates=required * block_length,
        estimated_final_half_width=estimate,
        estimated_precision_adequate=bool(planned_blocks >= required),
        status="adequate" if planned_blocks >= required else "insufficient_precision",
        positive_pilot_block_fraction=float(np.mean(blocks > 0)),
    )
    if n_blocks < 8:
        result["warnings"].append("Few pilot blocks make the planning variance uncertain.")
    if sd <= 1e-12:
        result["warnings"].append("Zero observed pilot block variance is not evidence of zero future uncertainty; the minimum-block floor still applies.")
    if not result["estimated_precision_adequate"]:
        result["warnings"].append("Planned final coverage does not meet the pilot precision estimate; research decisiveness must remain explicitly downgraded.")
    return result
