"""Synthetic tests of model contracts; these are not market-result evidence."""

import numpy as np
import pytest
from sklearn.exceptions import NotFittedError
from sklearn.pipeline import Pipeline
from sklearn.utils.validation import check_is_fitted

from market_microstructure.models import MODEL_ORDER, model_factories, model_specifications


def _training_problem():
    rng = np.random.default_rng(17)
    x = rng.normal(size=(240, 4))
    x[::9, 0] = np.nan
    x[::11, 2] = np.nan
    target = np.digitize(np.nan_to_num(x[:, 0]) + 0.3 * x[:, 1], [-0.45, 0.45]) - 1
    return x[:180], target[:180], x[180:], target[180:]


def test_factories_are_fresh_unfitted_pipelines_in_fixed_order():
    factories = model_factories()
    assert tuple(factories) == MODEL_ORDER
    for factory in factories.values():
        first, second = factory(), factory()
        assert isinstance(first, Pipeline)
        assert first is not second
        assert first.named_steps["imputer"] is not second.named_steps["imputer"]
        with pytest.raises(NotFittedError):
            check_is_fitted(first.named_steps["classifier"])


def test_preprocessing_is_fit_on_training_rows_and_unchanged_by_prediction_shift():
    train_x, train_y, test_x, _ = _training_problem()
    expected_median = np.nanmedian(train_x, axis=0)
    expected_imputed = np.where(np.isnan(train_x), expected_median, train_x)
    model = model_factories()["logistic"]().fit(train_x, train_y)
    imputer = model.named_steps["imputer"]
    scaler = model.named_steps["scaler"]
    np.testing.assert_allclose(imputer.statistics_, expected_median)
    np.testing.assert_allclose(scaler.mean_, expected_imputed.mean(axis=0))
    imputer_before, mean_before = imputer.statistics_.copy(), scaler.mean_.copy()

    shifted_test = np.nan_to_num(test_x, nan=1e6) + 1e6
    predictions = model.predict(shifted_test)
    assert predictions.shape == (len(test_x),)
    np.testing.assert_array_equal(imputer.statistics_, imputer_before)
    np.testing.assert_array_equal(scaler.mean_, mean_before)
    assert not np.allclose(
        scaler.mean_, np.nanmean(np.concatenate([train_x, shifted_test]), axis=0)
    ), "The adversarial held-out shift must distinguish a globally fitted scaler."


@pytest.mark.parametrize("name", MODEL_ORDER)
def test_model_fits_predicts_and_reproduces_on_nonempty_three_class_fixture(name):
    train_x, train_y, test_x, test_y = _training_problem()
    assert set(train_y) == {-1, 0, 1}
    first = model_factories(13)[name]().fit(train_x, train_y)
    second = model_factories(13)[name]().fit(train_x, train_y)
    pred = first.predict(test_x)
    assert len(pred) == len(test_y) > 0
    assert set(pred).issubset({-1, 0, 1})
    np.testing.assert_array_equal(pred, second.predict(test_x))
    np.testing.assert_allclose(first.predict_proba(test_x), second.predict_proba(test_x))
    np.testing.assert_allclose(first.predict_proba(test_x).sum(axis=1), 1)


def test_majority_prediction_uses_training_distribution_only():
    train_x, train_y, test_x, _ = _training_problem()
    train_y = np.zeros_like(train_y)
    train_y[:10] = -1
    train_y[10:20] = 1
    model = model_factories()["majority"]().fit(train_x, train_y)
    np.testing.assert_array_equal(model.predict(test_x + 1e8), np.zeros(len(test_x)))


def test_boosted_disables_internal_early_stopping_and_has_bounded_complexity():
    model = model_factories(7)["boosted"]().named_steps["classifier"]
    assert model.early_stopping is False
    assert model.max_iter == 100
    assert model.max_leaf_nodes == 7
    assert model.max_depth == 3
    assert model.random_state == 7


def test_single_class_logistic_fit_fails_explicitly_instead_of_model_substitution():
    train_x, train_y, _, _ = _training_problem()
    with pytest.raises(ValueError, match="at least 2 classes"):
        model_factories()["logistic"]().fit(train_x, np.zeros_like(train_y))


def test_empty_input_is_rejected_by_models():
    for factory in model_factories().values():
        with pytest.raises(ValueError):
            factory().fit(np.empty((0, 4)), np.empty(0, dtype=int))


@pytest.mark.parametrize("seed", [-1, 2**32, True, 1.5, "42"])
def test_invalid_seeds_fail_before_factories_are_used(seed):
    with pytest.raises(ValueError, match="seed"):
        model_factories(seed)


def test_recorded_settings_match_model_parameters():
    specs = model_specifications(23)
    for name, factory in model_factories(23).items():
        parameters = factory().named_steps["classifier"].get_params()
        for key, value in specs[name].items():
            if key not in {"class", "preprocessing"}:
                assert parameters[key] == value
