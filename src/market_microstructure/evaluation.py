"""Classification and date-level descriptive uncertainty for order-book research."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Integral, Real
from typing import Any

import numpy as np
from numpy.typing import ArrayLike
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

CLASS_ORDER = (-1, 0, 1)
CLASS_NAMES = ("down", "unchanged", "up")
BALANCED_ACCURACY_POLICY = "mean_recall_of_present_true_classes"


def _labels(values: ArrayLike, name: str) -> np.ndarray:
    array = np.asarray(values)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{name} must be a nonempty one-dimensional label array")
    if array.dtype.kind not in "iuf" or not np.isfinite(array).all():
        raise ValueError(f"{name} must contain only numeric labels -1, 0, 1")
    if not np.isin(array, CLASS_ORDER).all():
        raise ValueError(f"{name} must contain only labels -1, 0, 1")
    return array.astype(np.int64, copy=False)


def evaluate_predictions(y_true: ArrayLike, y_pred: ArrayLike) -> dict[str, Any]:
    """Evaluate exactly the same eligible rows using a fixed class ordering.

    Macro F1 always averages all three declared classes, assigning zero when a
    class has no support or predictions. Balanced accuracy follows the standard
    convention: average recall over classes present in y_true. The fixed-three-
    class macro recall is also returned, so absent-class cases are not hidden by
    that convention. A missing class is explicitly disclosed in warnings.
    """
    truth, predicted = _labels(y_true, "y_true"), _labels(y_pred, "y_pred")
    if truth.shape != predicted.shape:
        raise ValueError("y_true and y_pred must contain the same number of rows")

    precision, recall, f1, support = precision_recall_fscore_support(
        truth, predicted, labels=list(CLASS_ORDER), zero_division=0
    )
    matrix = confusion_matrix(truth, predicted, labels=list(CLASS_ORDER))
    present = support > 0
    absent = [label for label, count in zip(CLASS_ORDER, support, strict=True) if count == 0]
    unpredicted = [
        label for label, count in zip(CLASS_ORDER, matrix.sum(axis=0), strict=True)
        if count == 0
    ]
    warnings: list[str] = []
    if absent:
        warnings.append(
            "True classes absent: "
            + ", ".join(str(label) for label in absent)
            + ". Macro F1 keeps all three classes; balanced accuracy averages only present true classes."
        )
    if unpredicted:
        warnings.append(
            "No predictions for classes: "
            + ", ".join(str(label) for label in unpredicted)
            + ". Undefined precision/F1 components use zero."
        )
    per_class = [
        {
            "label": int(label),
            "name": name,
            "precision": float(p),
            "recall": float(r),
            "f1": float(f),
            "support": int(n),
        }
        for label, name, p, r, f, n in zip(
            CLASS_ORDER, CLASS_NAMES, precision, recall, f1, support, strict=True
        )
    ]
    return {
        "class_order": list(CLASS_ORDER),
        "macro_f1": float(np.mean(f1)),
        "balanced_accuracy": float(np.mean(recall[present])),
        "balanced_accuracy_policy": BALANCED_ACCURACY_POLICY,
        "fixed_class_macro_recall": float(np.mean(recall)),
        "accuracy": float(np.mean(truth == predicted)),
        "per_class": per_class,
        "confusion_matrix": matrix.astype(int).tolist(),
        "support": int(truth.size),
        "correct": int(np.count_nonzero(truth == predicted)),
        "absent_true_classes": absent,
        "unpredicted_classes": unpredicted,
        "warnings": warnings,
    }


def _session_scores(scores: Mapping[str, float], name: str) -> dict[str, float]:
    if not isinstance(scores, Mapping) or not scores:
        raise ValueError(f"{name} must be a nonempty mapping from session/date ID to score")
    result: dict[str, float] = {}
    for unit, value in scores.items():
        if not isinstance(unit, str) or not unit.strip():
            raise ValueError(f"{name} must use nonempty string session/date identifiers")
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"{name}[{unit!r}] must be a finite score from 0 to 1")
        converted = float(value)
        if not np.isfinite(converted) or not 0 <= converted <= 1:
            raise ValueError(f"{name}[{unit!r}] must be a finite score from 0 to 1")
        result[unit] = converted
    return result


def summarize_session_scores(scores: Mapping[str, float]) -> dict[str, Any]:
    """Describe date/session metrics without treating individual rows as IID."""
    validated = _session_scores(scores, "scores")
    units = sorted(validated)
    values = np.asarray([validated[unit] for unit in units], dtype=float)
    return {
        "analysis_unit": "session_or_date",
        "units": units,
        "n_units": len(units),
        "mean": float(values.mean()),
        "std": float(values.std(ddof=1)) if len(units) > 1 else None,
        "min": float(values.min()),
        "max": float(values.max()),
        "scores_by_unit": {unit: validated[unit] for unit in units},
        "warnings": (
            ["Fewer than 10 observed dates/sessions; dispersion is descriptive and generalization is uncertain."]
            if len(units) < 10 else []
        ),
    }


def paired_session_bootstrap(
    scores_a: Mapping[str, float],
    scores_b: Mapping[str, float],
    *,
    confidence: float = 0.95,
    n_resamples: int = 2000,
    seed: int = 42,
) -> dict[str, Any]:
    """Bootstrap paired session/date score differences (A minus B).

    The input contains one score per held-out date or whole session. The caller
    must not pass individual order-book rows as the analysis units. Sessions are
    resampled as indivisible pairs, and no estimator is refitted in this helper.
    With fewer than three units, no interval is reported. All intervals remain
    exploratory because exchangeability/independence of dates is an assumption,
    and overlapping training windows are not additional independent evidence.
    """
    a, b = _session_scores(scores_a, "scores_a"), _session_scores(scores_b, "scores_b")
    if set(a) != set(b):
        raise ValueError("paired comparisons require identical session/date identifiers")
    if isinstance(confidence, bool) or not isinstance(confidence, Real) or not 0 < confidence < 1:
        raise ValueError("confidence must be a number strictly between zero and one")
    if (
        isinstance(n_resamples, bool)
        or not isinstance(n_resamples, Integral)
        or not 100 <= n_resamples <= 100_000
    ):
        raise ValueError("n_resamples must be an integer from 100 through 100000")
    if isinstance(seed, bool) or not isinstance(seed, Integral) or not 0 <= seed < 2**32:
        raise ValueError("seed must be an integer between 0 and 2**32 - 1")

    units = sorted(a)
    differences = np.asarray([a[unit] - b[unit] for unit in units], dtype=float)
    n_units = len(units)
    warnings = [
        "Exploratory session/date bootstrap: assumes exchangeable independent evaluation units; "
        "overlapping training folds do not create independent observations."
    ]
    result: dict[str, Any] = {
        "method": "paired_percentile_bootstrap_of_session_mean_differences",
        "analysis_unit": "session_or_date",
        "difference_direction": "scores_a_minus_scores_b",
        "units": units,
        "n_units": n_units,
        "mean_difference": float(differences.mean()),
        "min_difference": float(differences.min()),
        "max_difference": float(differences.max()),
        "std_difference": float(differences.std(ddof=1)) if n_units > 1 else None,
        "confidence": float(confidence),
        "ci_lower": None,
        "ci_upper": None,
        "n_resamples": 0,
        "seed": int(seed),
        "status": "insufficient_units" if n_units < 3 else "exploratory",
        "warnings": warnings,
    }
    if n_units < 3:
        warnings.append("Fewer than 3 session/date units; no confidence interval is reported.")
        return result
    if n_units < 10:
        warnings.append(
            "Fewer than 10 session/date units; the percentile interval may be unstable and must not be read as proof of generalization."
        )
    if np.ptp(differences) <= 1e-12:
        warnings.append(
            "Observed differences are identical; a zero-width interval does not prove generalization."
        )
    rng = np.random.default_rng(int(seed))
    bootstrap_means = np.empty(int(n_resamples), dtype=float)
    for start in range(0, int(n_resamples), 256):
        stop = min(start + 256, int(n_resamples))
        chosen = rng.integers(0, n_units, size=(stop - start, n_units))
        bootstrap_means[start:stop] = differences[chosen].mean(axis=1)
    tail = (1.0 - float(confidence)) / 2.0
    lower, upper = np.quantile(bootstrap_means, [tail, 1.0 - tail])
    result.update(
        ci_lower=float(lower), ci_upper=float(upper), n_resamples=int(n_resamples)
    )
    return result
