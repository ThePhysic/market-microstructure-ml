from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from market_microstructure.splits import Fold, audit_fold, walk_forward


def samples(days=8, per_day=12):
    rows = []
    for month in range(1, days + 1):
        session_date = f"2020-{month:02d}-01"
        base = int(pd.Timestamp(session_date, tz="UTC").value // 1000)
        for position in range(per_day):
            order = len(rows) * 10 + 1
            rows.append({
                "session_date": session_date,
                "feature_cutoff_time": base + position * 1_000_000,
                "label_end_time": base + position * 1_000_000 + 500_000,
                "feature_order": order,
                "label_end_order": order + 3,
                "target": position % 3 - 1,
            })
    return pd.DataFrame(rows)


def test_expanding_date_folds_exclude_final_holdout_everywhere():
    source = samples()
    folds, holdout, metadata = walk_forward(source)
    assert len(folds) == 3
    assert folds[0].train_dates == ("2020-01-01", "2020-02-01", "2020-03-01")
    assert folds[0].test_dates == ("2020-04-01",)
    assert len(folds[-1].train_dates) == 5
    assert holdout.train_dates == tuple(f"2020-{month:02d}-01" for month in range(1, 7))
    assert holdout.test_dates == ("2020-07-01", "2020-08-01")
    held_out = set(holdout.test_indices)
    for fold in folds:
        assert held_out.isdisjoint(fold.train_indices)
        assert held_out.isdisjoint(fold.test_indices)
        proof = audit_fold(source, fold)
        assert proof["strict_time_boundary"]
        assert proof["strict_source_order_boundary"]
    assert metadata["final_holdout_excluded_from_development"] is True


def test_purge_removes_training_labels_that_end_at_or_beyond_evaluation_boundary():
    # These generic supplied intervals deliberately cross dates to exercise the
    # splitter's defense. Production build_samples never makes cross-date labels.
    source = samples()
    boundary = source.loc[36, "feature_cutoff_time"]
    source.loc[34:35, "label_end_time"] = [boundary, boundary + 1]
    source.loc[34:35, "label_end_order"] = [source.loc[36, "feature_order"], source.loc[36, "feature_order"] + 1]
    folds, _, _ = walk_forward(source)
    first = folds[0]
    assert first.purged_count == 2
    assert 34 not in first.train_indices and 35 not in first.train_indices
    assert first.audit["purged_feature_orders"] == source.loc[34:35, "feature_order"].tolist()
    assert first.audit["candidate_train_rows"] == 36
    assert len(first.train_indices) == 34
    audit_fold(source, first)


def test_final_holdout_boundary_is_purged_independently():
    source = samples()
    boundary = source.loc[72, "feature_cutoff_time"]
    source.loc[71, "label_end_time"] = boundary
    source.loc[71, "label_end_order"] = source.loc[72, "feature_order"]
    folds, holdout, audit = walk_forward(source)
    assert holdout.purged_count == 1
    assert 71 not in holdout.train_indices
    assert all(fold.purged_count == 0 for fold in folds)
    assert audit["final_holdout_purged_rows"] == 1


def test_a_known_leaky_fold_is_actually_rejected():
    source = samples()
    folds, _, _ = walk_forward(source)
    clean = folds[0]
    contaminated = source.copy()
    contaminated.loc[clean.train_indices[-1], "label_end_time"] = contaminated.loc[clean.test_indices[0], "feature_cutoff_time"]
    with pytest.raises(ValueError, match="overlaps"):
        audit_fold(contaminated, clean)


def test_source_order_proof_rejects_fake_safe_timestamps():
    source = samples()
    folds, _, _ = walk_forward(source)
    source.loc[folds[0].train_indices[-1], "label_end_order"] = source.loc[folds[0].test_indices[0], "feature_order"]
    with pytest.raises(ValueError, match="source order"):
        audit_fold(source, folds[0])


def test_split_hashes_are_deterministic_with_nondefault_dataframe_index():
    source = samples()
    source.index = np.arange(len(source)) + 5000
    first, first_holdout, first_audit = walk_forward(source)
    second, second_holdout, second_audit = walk_forward(source.copy())
    assert first_audit == second_audit
    assert first_audit["calendar_gaps"].startswith("Unobserved dates")
    for a, b in zip(first + [first_holdout], second + [second_holdout]):
        np.testing.assert_array_equal(a.train_indices, b.train_indices)
        np.testing.assert_array_equal(a.test_indices, b.test_indices)


@pytest.mark.parametrize("bad_kind", ["overlap", "empty", "duplicate", "out_of_bounds", "date_mismatch"])
def test_invalid_fold_records_do_not_produce_successful_audits(bad_kind):
    source = samples()
    fold = walk_forward(source)[0][0]
    if bad_kind == "overlap":
        bad = replace(fold, train_indices=np.append(fold.train_indices, fold.test_indices[0]))
    elif bad_kind == "empty":
        bad = replace(fold, train_indices=np.array([], dtype=int))
    elif bad_kind == "duplicate":
        bad = replace(fold, test_indices=np.append(fold.test_indices, fold.test_indices[-1]))
    elif bad_kind == "out_of_bounds":
        bad = replace(fold, test_indices=np.array([len(source)], dtype=int))
    else:
        bad = replace(fold, test_dates=("2020-12-01",))
    with pytest.raises(ValueError):
        audit_fold(source, bad)


def test_fold_indices_are_immutable_integer_position_arrays():
    source = samples()
    fold = walk_forward(source)[0][0]
    with pytest.raises(ValueError):
        fold.train_indices[0] = 999
    with pytest.raises(ValueError, match="integer"):
        Fold("bad", np.array([1.0]), np.array([2]), ("2020-01-01",), ("2020-02-01",))


def test_labels_cannot_claim_another_declared_segment_or_session():
    source = samples()
    source["segment_id"] = source["session_date"]
    source["label_segment_id"] = source["segment_id"]
    source.loc[10, "label_segment_id"] = "other"
    with pytest.raises(ValueError, match="crosses"):
        walk_forward(source)


@pytest.mark.parametrize("arguments", [
    {"min_train_dates": 0}, {"min_train_dates": True}, {"min_train_dates": 1.5},
    {"holdout_dates": 0}, {"holdout_dates": 1.5},
])
def test_invalid_split_parameters_are_rejected(arguments):
    with pytest.raises(ValueError):
        walk_forward(samples(), **arguments)


def test_empty_or_insufficient_independent_dates_are_rejected():
    with pytest.raises(ValueError, match="empty"):
        walk_forward(samples().iloc[:0])
    with pytest.raises(ValueError, match="Insufficient"):
        walk_forward(samples(days=5))


def test_input_order_and_earlier_label_endpoint_are_rejected():
    source = samples()
    shuffled = source.iloc[::-1].reset_index(drop=True)
    with pytest.raises(ValueError, match="chronological"):
        walk_forward(shuffled)
    source.loc[5, "label_end_time"] = source.loc[5, "feature_cutoff_time"] - 1
    with pytest.raises(ValueError, match="endpoint"):
        walk_forward(source)


def test_actual_utc_dates_cannot_be_relabelled_as_more_independent_sessions():
    source = samples()
    source.loc[source["session_date"] == "2020-04-01", "session_date"] = "2020-03-02"
    with pytest.raises(ValueError, match="UTC decision timestamp"):
        walk_forward(source)
