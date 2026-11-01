"""Chronological walk-forward splits with independently auditable label purging."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date
import hashlib
import numbers
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Fold:
    """Indices are positional (iloc), never DataFrame index labels."""

    name: str
    train_indices: np.ndarray
    test_indices: np.ndarray
    train_dates: tuple[str, ...]
    test_dates: tuple[str, ...]
    purged_count: int = 0
    audit: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for key in ("train_indices", "test_indices"):
            array = np.asarray(getattr(self, key))
            if array.ndim != 1 or array.dtype.kind not in "iu":
                raise ValueError(f"{key} must be a one-dimensional integer array")
            array = array.astype(np.int64, copy=True)
            array.setflags(write=False)
            object.__setattr__(self, key, array)
        object.__setattr__(self, "train_dates", tuple(self.train_dates))
        object.__setattr__(self, "test_dates", tuple(self.test_dates))
        if isinstance(self.purged_count, bool) or not isinstance(self.purged_count, numbers.Integral) or self.purged_count < 0:
            raise ValueError("purged_count must be a nonnegative integer")


_REQUIRED = ["session_date", "feature_cutoff_time", "label_end_time", "feature_order", "label_end_order"]


def _validate_samples(samples: pd.DataFrame) -> None:
    if not isinstance(samples, pd.DataFrame):
        raise TypeError("samples must be a pandas DataFrame")
    missing = sorted(set(_REQUIRED) - set(samples.columns))
    if missing:
        raise ValueError(f"Missing sample metadata: {', '.join(missing)}")
    if samples.empty:
        raise ValueError("Cannot evaluate an empty sample table")
    if samples[_REQUIRED].isna().any().any():
        raise ValueError("Temporal metadata must not be missing")
    for column in _REQUIRED[1:]:
        if not pd.api.types.is_integer_dtype(samples[column].dtype):
            raise ValueError(f"{column} must contain integer microseconds/order values")
        if np.any(samples[column].to_numpy(dtype=np.int64) < 0):
            raise ValueError(f"{column} must not contain negative values")
    expected_days = {}
    for value in samples["session_date"].unique():
        if not isinstance(value, str):
            raise ValueError("session_date must use canonical YYYY-MM-DD strings")
        try:
            valid = date.fromisoformat(value).isoformat() == value
        except ValueError:
            valid = False
        if not valid:
            raise ValueError(f"Invalid canonical session_date: {value!r}")
        expected_days[value] = (date.fromisoformat(value) - date(1970, 1, 1)).days
    cutoffs = samples["feature_cutoff_time"].to_numpy(dtype=np.int64)
    endpoints = samples["label_end_time"].to_numpy(dtype=np.int64)
    order = samples["feature_order"].to_numpy(dtype=np.int64)
    end_order = samples["label_end_order"].to_numpy(dtype=np.int64)
    if np.any(cutoffs[1:] < cutoffs[:-1]) or np.any(order[1:] <= order[:-1]):
        raise ValueError("Samples must preserve chronological cutoff/source order")
    if np.any(endpoints < cutoffs) or np.any(end_order <= order):
        raise ValueError("Every target endpoint must follow its decision in source order and not precede it in time")
    dates = samples["session_date"].to_numpy()
    if np.any(cutoffs // 86_400_000_000 != samples["session_date"].map(expected_days).to_numpy(dtype=np.int64)):
        raise ValueError("session_date disagrees with the UTC decision timestamp")
    if np.any(dates[1:] < dates[:-1]):
        raise ValueError("Session dates must be chronological")
    for label_column, feature_column in (
        ("label_segment_id", "segment_id"),
        ("label_session_date", "session_date"),
        ("label_source_file", "source_file"),
    ):
        if label_column in samples:
            if feature_column not in samples or not samples[label_column].eq(samples[feature_column]).all():
                raise ValueError(f"{label_column} crosses a declared feature session/segment/source boundary")


def _index_hash(values: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(values, dtype="<i8").tobytes()).hexdigest()


def audit_fold(samples: pd.DataFrame, fold: Fold) -> dict[str, Any]:
    """Reject leaky, empty, overlapping, reordered, or mismatched fold records.

    The time rule is deliberately conservative at timestamp ties: all training
    labels must end *strictly before* the earliest evaluation decision timestamp.
    Source-order endpoints are checked independently as a second proof.
    """
    _validate_samples(samples)
    train_indices, test_indices = fold.train_indices, fold.test_indices
    for kind, indices in (("train", train_indices), ("test", test_indices)):
        if not len(indices):
            raise ValueError(f"{fold.name}: {kind} partition is empty")
        if np.any(indices < 0) or np.any(indices >= len(samples)):
            raise ValueError(f"{fold.name}: {kind} index out of bounds")
        if np.any(indices[1:] <= indices[:-1]):
            raise ValueError(f"{fold.name}: {kind} indices are duplicated or reordered")
    if np.intersect1d(train_indices, test_indices).size:
        raise ValueError(f"{fold.name}: train/test rows overlap")
    train, test = samples.iloc[train_indices], samples.iloc[test_indices]
    train_dates = tuple(train["session_date"].drop_duplicates())
    test_dates = tuple(test["session_date"].drop_duplicates())
    if train_dates != fold.train_dates or test_dates != fold.test_dates:
        raise ValueError(f"{fold.name}: declared dates disagree with actual partition rows")
    boundary = int(test["feature_cutoff_time"].min())
    max_train_end = int(train["label_end_time"].max())
    if max_train_end >= boundary:
        raise ValueError(f"{fold.name}: training label interval overlaps an evaluation boundary")
    if int(train["feature_cutoff_time"].max()) >= boundary:
        raise ValueError(f"{fold.name}: training decisions are not strictly earlier than evaluation")
    first_eval_order = int(test["feature_order"].min())
    max_train_end_order = int(train["label_end_order"].max())
    if max_train_end_order >= first_eval_order:
        raise ValueError(f"{fold.name}: training label source order reaches evaluation")
    return {
        "name": fold.name,
        "train_rows": len(train),
        "test_rows": len(test),
        "train_dates": list(train_dates),
        "test_dates": list(test_dates),
        "purged_count": int(fold.purged_count),
        "evaluation_boundary_us": boundary,
        "max_train_label_end_us": max_train_end,
        "first_evaluation_order": first_eval_order,
        "max_train_label_end_order": max_train_end_order,
        "strict_time_boundary": True,
        "strict_source_order_boundary": True,
        "train_index_sha256": _index_hash(train_indices),
        "test_index_sha256": _index_hash(test_indices),
        "train_feature_order_sha256": _index_hash(train["feature_order"].to_numpy()),
        "test_feature_order_sha256": _index_hash(test["feature_order"].to_numpy()),
    }


def _make_fold(
    samples: pd.DataFrame, name: str, train_dates: list[str], test_dates: list[str]
) -> Fold:
    candidate = np.flatnonzero(samples["session_date"].isin(train_dates).to_numpy())
    test_indices = np.flatnonzero(samples["session_date"].isin(test_dates).to_numpy())
    if not len(candidate) or not len(test_indices):
        raise ValueError(f"{name}: requested dates have no eligible samples")
    boundary = int(samples.iloc[test_indices]["feature_cutoff_time"].min())
    keep = samples.iloc[candidate]["label_end_time"].to_numpy() < boundary
    train_indices = candidate[keep]
    if not len(train_indices):
        raise ValueError(f"{name}: purging removed every training sample")
    # If a whole date loses every sample, declared dates must still describe the
    # actual rows rather than silently claiming that date was represented.
    actual_train_dates = tuple(samples.iloc[train_indices]["session_date"].drop_duplicates())
    fold = Fold(
        name=name, train_indices=train_indices, test_indices=test_indices,
        train_dates=actual_train_dates, test_dates=tuple(test_dates),
        purged_count=int(np.sum(~keep)),
    )
    metadata = audit_fold(samples, fold)
    metadata["candidate_train_rows"] = len(candidate)
    metadata["requested_train_dates"] = list(train_dates)
    metadata["purged_feature_orders"] = [
        int(value) for value in samples.iloc[candidate[~keep]]["feature_order"]
    ]
    return replace(fold, audit=metadata)


def walk_forward(
    samples: pd.DataFrame,
    *,
    min_train_dates: int = 3,
    holdout_dates: int = 2,
) -> tuple[list[Fold], Fold, dict[str, Any]]:
    """Expand training across observed dates, reserving the final date block.

    Missing intervening calendar days are never synthesized. Each development
    fold tests one later observed date. The final fold trains on permitted
    pre-holdout observations and tests only the last holdout_dates observed dates.
    """
    _validate_samples(samples)
    for name, value in (("min_train_dates", min_train_dates), ("holdout_dates", holdout_dates)):
        if isinstance(value, bool) or not isinstance(value, numbers.Integral) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    dates = list(samples["session_date"].drop_duplicates())
    if len(dates) < min_train_dates + holdout_dates + 1:
        raise ValueError(
            "Insufficient independent observed dates: need training dates, at least "
            "one development date, and a separate final holdout"
        )
    development_dates = dates[:-holdout_dates]
    final_dates = dates[-holdout_dates:]
    folds = [
        _make_fold(samples, f"walk_forward_{index-min_train_dates+1:02d}", development_dates[:index], [development_dates[index]])
        for index in range(min_train_dates, len(development_dates))
    ]
    holdout = _make_fold(samples, "final_holdout", development_dates, final_dates)
    held_out = set(map(int, holdout.test_indices))
    used_in_development = set()
    for fold in folds:
        used_in_development.update(map(int, fold.train_indices))
        used_in_development.update(map(int, fold.test_indices))
    if held_out & used_in_development:
        raise ValueError("Final holdout rows leaked into development folds")
    audit = {
        "strategy": "expanding observed-date walk-forward; one validation date per development fold",
        "observed_dates": dates,
        "development_dates": development_dates,
        "holdout_dates": final_dates,
        "development_fold_count": len(folds),
        "final_holdout_excluded_from_development": True,
        "purge_rule": "Keep a train row only if label_end_time < earliest evaluation feature_cutoff_time.",
        "timestamp_tie_policy": "Conservative purge at equal endpoint/cutoff times; stable source order.",
        "calendar_gaps": "Unobserved dates are gaps, not a continuous backtest.",
        "total_development_purged_rows": sum(fold.purged_count for fold in folds),
        "final_holdout_purged_rows": holdout.purged_count,
        "folds": [fold.audit for fold in folds],
        "final_holdout": holdout.audit,
    }
    return folds, holdout, audit
