from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
import json

import pytest

from market_microstructure.config import ResearchConfig, config_from_dict, load_config


DATES = tuple(f"2020-{month:02d}-01" for month in range(1, 9))


def valid_config(**changes):
    return ResearchConfig(dates=DATES, rows_per_date=120, **changes)


def test_configuration_roundtrips_without_mutating_the_input(tmp_path):
    config = valid_config()
    payload = config.to_dict()
    original = deepcopy(payload)
    path = tmp_path / "research.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert load_config(path) == config_from_dict(payload) == config
    assert payload == original
    assert isinstance(config.dates, tuple)
    assert isinstance(config.robustness, tuple)
    with pytest.raises(FrozenInstanceError):
        config.seed = 99


@pytest.mark.parametrize("field,value", [
    ("seed", -1), ("seed", 2**32), ("seed", True),
    ("schema_version", 2), ("horizon_events", 0), ("horizon_events", 2.5),
    ("trailing_window", 0), ("min_train_dates", False), ("holdout_dates", 0),
    ("threshold_ticks", -1), ("threshold_ticks", "1"),
    ("threshold_ticks", float("nan")), ("tick_size", 0),
    ("tick_size", float("inf")), ("gap_seconds", -1),
    ("gap_seconds", True), ("exchange", "other"), ("symbol", "OTHER"),
    ("data_type", "trades"), ("rows_per_date", 20_001),
    ("rows_per_date", 35),  # Cannot support the required 20-state sensitivity.
    ("max_compressed_bytes_per_date", 2 * 1024**2 + 1),
    ("max_total_transfer_bytes", 24 * 1024**2 + 1),
    ("max_total_transfer_bytes", 100),
])
def test_invalid_parameters_fail_before_an_experiment(field, value):
    with pytest.raises(ValueError):
        replace(valid_config(), **{field: value})


def test_finite_threshold_components_cannot_overflow_the_price_band():
    with pytest.raises(ValueError, match="finite"):
        valid_config(threshold_ticks=1e300, tick_size=1e300)


@pytest.mark.parametrize("dates", [
    (), tuple(reversed(DATES)), DATES + (DATES[-1],),
    DATES[:5], ("2020-01-02",) + DATES[1:],
    ("2020-1-1",) + DATES[1:], (None,) + DATES[1:],
    tuple(f"2020-{month:02d}-01" for month in range(1, 13)) + ("2021-01-01",),
])
def test_date_order_count_and_schema_are_explicit(dates):
    with pytest.raises(ValueError):
        ResearchConfig(dates=dates, rows_per_date=120)


@pytest.mark.parametrize("payload", [
    [], "not-an-object", {"dates": DATES},
    {"dates": list(DATES), "unknown": "ignored-configuration-is-dangerous"},
    {"dates": list(DATES), "robustness": []},
    {"dates": list(DATES), "robustness": {"alternate_horizon_events": 10}},
])
def test_unknown_or_malformed_json_configuration_is_rejected(payload):
    with pytest.raises(ValueError):
        config_from_dict(payload)


@pytest.mark.parametrize("robustness", [
    {"feature_ablation": "remove_imbalance", "alternate_horizon_events": 20, "development_only": True},
    (["feature_ablation", "remove_imbalance"], ["alternate_horizon_events", 20], ["development_only", True]),
    (("feature_ablation", "remove_imbalance"), ("alternate_horizon_events", 20.0), ("development_only", True)),
    (("feature_ablation", "remove_imbalance"), ("alternate_horizon_events", 20), ("development_only", 1)),
])
def test_robustness_contract_requires_immutable_correctly_typed_settings(robustness):
    with pytest.raises(ValueError):
        valid_config(robustness=robustness)
