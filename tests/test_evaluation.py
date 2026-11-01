"""Known-answer metrics and session-level uncertainty tests."""

import json

import numpy as np
import pytest
from sklearn.metrics import balanced_accuracy_score, f1_score

from market_microstructure.evaluation import (
    evaluate_predictions,
    paired_session_bootstrap,
    summarize_session_scores,
)


def test_known_three_class_confusion_matrix_and_metric_values():
    truth = [-1, -1, 0, 0, 1, 1]
    predicted = [-1, 0, 0, 1, 1, 1]
    result = evaluate_predictions(truth, predicted)
    assert result["class_order"] == [-1, 0, 1]
    assert result["confusion_matrix"] == [[1, 1, 0], [0, 1, 1], [0, 0, 2]]
    assert result["support"] == 6
    assert [row["support"] for row in result["per_class"]] == [2, 2, 2]
    assert result["macro_f1"] == pytest.approx((2 / 3 + 1 / 2 + 4 / 5) / 3)
    assert result["balanced_accuracy"] == pytest.approx(2 / 3)
    assert result["fixed_class_macro_recall"] == pytest.approx(2 / 3)
    assert result["accuracy"] == pytest.approx(2 / 3)
    assert result["warnings"] == []
    assert result["macro_f1"] == pytest.approx(
        f1_score(truth, predicted, labels=[-1, 0, 1], average="macro", zero_division=0)
    )
    assert result["balanced_accuracy"] == pytest.approx(
        balanced_accuracy_score(truth, predicted)
    )


def test_absent_classes_are_disclosed_and_balanced_accuracy_policy_is_explicit():
    result = evaluate_predictions([0, 0, 0], [0, 0, 0])
    assert result["macro_f1"] == pytest.approx(1 / 3)
    assert result["balanced_accuracy"] == 1
    assert result["fixed_class_macro_recall"] == pytest.approx(1 / 3)
    assert result["absent_true_classes"] == [-1, 1]
    assert result["unpredicted_classes"] == [-1, 1]
    assert result["balanced_accuracy_policy"] == "mean_recall_of_present_true_classes"
    assert len(result["warnings"]) == 2
    assert result["confusion_matrix"] == [[0, 0, 0], [0, 3, 0], [0, 0, 0]]


@pytest.mark.parametrize(
    ("truth", "predicted"),
    [
        ([], []),
        ([0], []),
        ([[0]], [[0]]),
        ([0, 1], [0]),
        ([-1, 2], [-1, 1]),
        ([0, np.nan], [0, 1]),
        ([0, np.inf], [0, 1]),
        (["0"], ["0"]),
        ([True], [True]),
        ([1j], [1j]),
    ],
)
def test_invalid_metric_inputs_raise_instead_of_returning_empty_success(truth, predicted):
    with pytest.raises(ValueError):
        evaluate_predictions(truth, predicted)


def test_metric_result_is_json_serializable_without_numpy_scalars():
    result = evaluate_predictions(np.array([-1, 0, 1]), np.array([0, 0, 1]))
    assert json.loads(json.dumps(result, allow_nan=False))["support"] == 3


def test_date_summary_has_one_observation_per_supplied_date_and_descriptive_warning():
    summary = summarize_session_scores({"2020-05-01": 0.6, "2020-04-01": 0.4})
    assert summary["units"] == ["2020-04-01", "2020-05-01"]
    assert summary["n_units"] == 2
    assert summary["mean"] == pytest.approx(0.5)
    assert summary["std"] == pytest.approx(np.std([0.4, 0.6], ddof=1))
    assert summary["warnings"]


def test_bootstrap_pairs_same_dates_and_is_deterministic_independent_of_mapping_order():
    a = {"d1": 0.8, "d2": 0.4, "d3": 0.65, "d4": 0.7}
    b = {"d4": 0.6, "d3": 0.55, "d2": 0.5, "d1": 0.6}
    first = paired_session_bootstrap(a, b, n_resamples=500, seed=7)
    second = paired_session_bootstrap(dict(reversed(list(a.items()))), b, n_resamples=500, seed=7)
    assert first == second
    assert first["mean_difference"] == pytest.approx(0.075)
    assert first["n_units"] == 4
    assert first["n_resamples"] == 500
    assert first["ci_lower"] <= first["mean_difference"] <= first["ci_upper"]
    assert first["analysis_unit"] == "session_or_date"
    assert first["difference_direction"] == "scores_a_minus_scores_b"
    assert first["status"] == "exploratory"
    assert first["warnings"]
    json.dumps(first, allow_nan=False)


def test_bootstrap_direction_reverses_with_score_order():
    a = {"d1": 0.8, "d2": 0.7, "d3": 0.6}
    b = {"d1": 0.3, "d2": 0.4, "d3": 0.5}
    forward = paired_session_bootstrap(a, b, n_resamples=100, seed=1)
    reverse = paired_session_bootstrap(b, a, n_resamples=100, seed=1)
    assert forward["mean_difference"] == pytest.approx(-reverse["mean_difference"])
    assert forward["ci_lower"] == pytest.approx(-reverse["ci_upper"])
    assert forward["ci_upper"] == pytest.approx(-reverse["ci_lower"])


@pytest.mark.parametrize("n_units", [1, 2])
def test_too_few_dates_return_no_interval_instead_of_false_precision(n_units):
    a = {f"d{i}": 0.7 for i in range(n_units)}
    b = {f"d{i}": 0.5 for i in range(n_units)}
    result = paired_session_bootstrap(a, b)
    assert result["status"] == "insufficient_units"
    assert result["ci_lower"] is None and result["ci_upper"] is None
    assert result["n_resamples"] == 0
    assert any("no confidence interval" in warning for warning in result["warnings"])


def test_identical_date_effects_warn_about_degenerate_interval():
    result = paired_session_bootstrap(
        {"a": 0.7, "b": 0.7, "c": 0.7},
        {"a": 0.5, "b": 0.5, "c": 0.5},
        n_resamples=100,
    )
    assert result["ci_lower"] == pytest.approx(0.2)
    assert result["ci_upper"] == pytest.approx(0.2)
    assert any("zero-width" in warning for warning in result["warnings"])


@pytest.mark.parametrize(
    ("a", "b", "kwargs"),
    [
        ({}, {}, {}),
        ({"a": 0.5}, {"b": 0.5}, {}),
        ({"a": float("nan")}, {"a": 0.5}, {}),
        ({"a": -0.1}, {"a": 0.5}, {}),
        ({"a": True}, {"a": 0.5}, {}),
        ({"": 0.5}, {"": 0.5}, {}),
        ({"a": 0.5}, {"a": 0.5}, {"confidence": 1}),
        ({"a": 0.5}, {"a": 0.5}, {"n_resamples": 99}),
        ({"a": 0.5}, {"a": 0.5}, {"n_resamples": 100001}),
        ({"a": 0.5}, {"a": 0.5}, {"seed": -1}),
    ],
)
def test_bootstrap_rejects_invalid_or_unpaired_units(a, b, kwargs):
    with pytest.raises(ValueError):
        paired_session_bootstrap(a, b, **kwargs)
