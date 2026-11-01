"""Synthetic-only research tests; no historical outcomes are read here."""

from copy import deepcopy
from datetime import date
import json
import math
from statistics import NormalDist

import numpy as np
import pandas as pd
import pytest

from market_microstructure.extension import replication, study
from market_microstructure.extension.statistics import (
    paired_block_bootstrap, pilot_precision_plan, practical_effect_decision,
)
from market_microstructure.features import FEATURE_COLUMNS, build_samples


def fixture_config():
    dates = [value.date().isoformat() for value in pd.date_range("2021-01-01", periods=15, freq="MS")]
    return {
        "schema_version": 1, "stage": "pilot", "dates": dates,
        "initial_train_dates": 3, "development_dates": dates[3:9], "final_dates": dates[9:],
        "exchange": "bitstamp", "symbol": "BTCUSD", "horizon_events": 3,
        "threshold_ticks": 1, "tick_size": 0.01, "trailing_window": 5, "seed": 42,
        "practical_delta": 0.01, "confidence": 0.95, "block_length_dates": 3,
        "precision_half_width": 0.015, "min_final_blocks": 2, "n_resamples": 200,
        "protocol_sha256": "a" * 64, "frozen_source_revision": "b" * 40,
        "final_scoring_authorized": False, "precision_gate_status": "pending",
        "target_position": "0.001", "max_holding_events": 10, "inference_delay_us": 0,
    }


def synthetic_states(config=None, count=100):
    config = config or fixture_config()
    rows = []
    for day_index, day in enumerate(config["dates"]):
        base = (date.fromisoformat(day) - date(1970, 1, 1)).days * 86_400_000_000
        for index in range(count):
            mid = round(100 + 0.2 * np.sin((index // 4 + day_index % 3) * 0.65), 2)
            order = len(rows) + 1
            row = {
                "exchange": "bitstamp", "symbol": "BTCUSD", "session_date": day,
                "segment_id": f"{day}:window0", "source_file": f"{day}.csv",
                "source_row_position": index + 1, "provenance_key": f"fixture:{order}",
                "receive_time_us": base + 1_000_000 + index * 1000,
                "event_time_us": base + 999_900 + index * 1000, "source_order": order,
            }
            for level in range(1, 6):
                row[f"bid_price_{level}"] = round(mid - 0.01 * level, 2)
                row[f"ask_price_{level}"] = round(mid + 0.01 * level, 2)
                row[f"bid_size_{level}"] = 1.1 + 0.5 * np.sin(index * 0.23 + day_index)
                row[f"ask_size_{level}"] = 1.1 + 0.4 * np.cos(index * 0.17)
            rows.append(row)
    return pd.DataFrame(rows)


@pytest.fixture(scope="module")
def pilot():
    return study.run_study(synthetic_states(), fixture_config())


def test_block_bootstrap_pairs_dates_deterministically_and_never_rows():
    dates = fixture_config()["dates"][:9]
    a = dict(zip(dates, [0.1, 0.8, 0.4, 0.7, 0.2, 0.9, 0.5, 0.6, 0.3], strict=True))
    b = {day: 0.4 for day in dates}
    first = paired_block_bootstrap(a, b, n_resamples=300, block_length=3)
    second = paired_block_bootstrap(dict(reversed(list(a.items()))), b, n_resamples=300, block_length=3)
    assert first == second
    assert first["n_units"] == 9 and first["nonoverlapping_block_count"] == 3
    assert first["mean_difference"] == pytest.approx(np.mean(list(a.values())) - 0.4)
    assert first["ci_lower"] < first["ci_upper"]
    assert first["confidence"] == 0.95
    assert first["method"] == "paired_non_circular_moving_block_percentile_bootstrap"
    assert first["ci_lower"] <= first["mean_difference"] <= first["ci_upper"]
    with pytest.raises(ValueError, match="identical observed"):
        paired_block_bootstrap(a, {day: value for day, value in b.items() if day != dates[0]})
    insufficient = paired_block_bootstrap(a, b, min_blocks=8)
    assert insufficient["ci_lower"] is None and insufficient["status"] == "insufficient_blocks"


def test_practical_decisions_require_full_interval_not_mean_or_sign():
    assert practical_effect_decision({"ci_lower": 0.011, "ci_upper": 0.04})["positive_practical_gain"]
    assert practical_effect_decision({"ci_lower": 0.01, "ci_upper": 0.04})["status"] == "indeterminate"
    assert practical_effect_decision({"ci_lower": -0.004, "ci_upper": 0.008})["equivalence_within_margin"]
    assert practical_effect_decision({"ci_lower": -0.1, "ci_upper": 0.009})["rules_out_practical_gain"]
    assert practical_effect_decision({"ci_lower": -0.1, "ci_upper": -0.02})["negative_practical_effect"]
    assert practical_effect_decision({"ci_lower": None, "ci_upper": None})["status"] == "insufficient_uncertainty_evidence"
    with pytest.raises(ValueError):
        practical_effect_decision({"ci_lower": 0.2, "ci_upper": -0.2})


def test_precision_estimate_uses_pilot_blocks_with_fixed_floor_and_no_forced_positive():
    dates = [value.date().isoformat() for value in pd.date_range("2020-01-01", periods=12, freq="MS")]
    differences = np.repeat([-0.2, 0.2, -0.1, 0.1], 3)
    a = dict(zip(dates, 0.5 + differences, strict=True))
    b = dict.fromkeys(dates, 0.5)
    plan = pilot_precision_plan(a, b, planned_final_dates=24)
    sd = np.std([-0.2, 0.2, -0.1, 0.1], ddof=1)
    expected_blocks = max(8, math.ceil((NormalDist().inv_cdf(0.975) * sd / 0.015) ** 2))
    assert plan["estimated_required_final_dates"] == expected_blocks * 3
    assert plan["estimated_final_half_width"] == pytest.approx(NormalDist().inv_cdf(0.975) * sd / math.sqrt(8))
    assert plan["status"] == "insufficient_precision" and not plan["estimated_precision_adequate"]
    constant = pilot_precision_plan(dict.fromkeys(dates, 0.4), dict.fromkeys(dates, 0.5), planned_final_dates=24)
    assert constant["estimated_required_final_blocks"] == 8
    assert constant["positive_pilot_date_fraction"] == 0
    assert any("Zero observed" in warning for warning in constant["warnings"])


@pytest.mark.parametrize("change", [
    {"protocol_sha256": None}, {"frozen_source_revision": None}, {"unexpected": 1},
    {"inference_delay_us": 1}, {"stage": "final"}, {"seed": True},
])
def test_invalid_or_unfrozen_configuration_fails_before_fit(monkeypatch, change):
    config = fixture_config()
    config.update(change)
    monkeypatch.setattr(study, "model_factories", lambda *_: pytest.fail("fit factory accessed before validation"))
    with pytest.raises(ValueError):
        study.run_study(synthetic_states(), config)


def test_coverage_failure_precedes_any_model_fit(monkeypatch):
    config = fixture_config()
    data = synthetic_states()
    data = data.loc[data["session_date"] != config["final_dates"][0]]
    monkeypatch.setattr(study, "model_factories", lambda *_: pytest.fail("coverage was checked after factory access"))
    with pytest.raises(ValueError, match="coverage"):
        study.run_study(data, config)


def test_fold_class_feasibility_is_checked_before_any_fit(monkeypatch):
    config = fixture_config()
    data = synthetic_states()
    for side in ("bid", "ask"):
        for level in range(1, 6):
            data[f"{side}_price_{level}"] = round(100 + (-1 if side == "bid" else 1) * level * 0.01, 2)
    monkeypatch.setattr(study, "model_factories", lambda *_: pytest.fail("fit began before all-fold feasibility check"))
    with pytest.raises(ValueError, match="two target classes"):
        study.run_study(data, config)


def test_causal_features_match_labeled_features_and_include_unlabelled_tail():
    config = fixture_config()
    data = synthetic_states(config)
    labeled, columns, _ = build_samples(
        data, horizon_events=config["horizon_events"], threshold_ticks=1,
        tick_size=config["tick_size"], trailing_window=config["trailing_window"],
    )
    causal = study.causal_feature_frame(data, tick_size=0.01, trailing_window=5)
    common = causal.set_index("source_order").loc[labeled["source_order"], columns]
    pd.testing.assert_frame_equal(common.reset_index(drop=True), labeled[columns].reset_index(drop=True))
    assert len(causal) - len(labeled) == config["horizon_events"] * len(config["dates"])
    assert causal["source_order"].iloc[-1] == data["source_order"].iloc[-1]
    assert "target" not in causal.columns and "label_end_time" not in causal.columns
    changed = data.copy(deep=True)
    future = (changed["session_date"] == config["development_dates"][0]) & (changed["source_row_position"] > 60)
    for side in ("bid", "ask"):
        for level in range(1, 6):
            changed.loc[future, f"{side}_price_{level}"] += 20
            changed.loc[future, f"{side}_size_{level}"] *= 100
    changed_features = study.causal_feature_frame(changed, tick_size=0.01, trailing_window=5)
    before = (causal["session_date"] == config["development_dates"][0]) & (causal["source_row_position"] <= 60)
    pd.testing.assert_frame_equal(causal.loc[before, FEATURE_COLUMNS], changed_features.loc[before, FEATURE_COLUMNS])


def test_pilot_never_labels_reserved_dates_and_future_reserved_changes_have_no_effect(pilot, monkeypatch):
    config = fixture_config()
    data = synthetic_states(config)
    original_builder = study.build_samples
    def guarded_builder(frame, **kwargs):
        assert not set(frame["session_date"]) & set(config["final_dates"])
        return original_builder(frame, **kwargs)
    monkeypatch.setattr(study, "build_samples", guarded_builder)
    future = data["session_date"].isin(config["final_dates"])
    for side in ("bid", "ask"):
        for level in range(1, 6):
            data.loc[future, f"{side}_price_{level}"] = (data.loc[future, f"{side}_price_{level}"] + 10_000).round(2)
            data.loc[future, f"{side}_size_{level}"] *= 10_000
    assert study.run_study(data, config) == pilot
    assert pilot["aggregate"]["final"] is None
    assert set(pilot["aggregate"]["coverage"]["labelled_dates"]).isdisjoint(config["final_dates"])


def test_pilot_signals_are_out_of_sample_causal_and_include_last_horizon_states(pilot):
    config = fixture_config()
    data = synthetic_states(config).set_index("source_order")
    development = pilot["aggregate"]["development"]
    assert len(development["folds"]) == len(config["development_dates"])
    for fold in development["folds"]:
        assert set(fold["train_dates"]).isdisjoint(fold["test_dates"])
        assert max(fold["train_dates"]) < min(fold["test_dates"])
        assert fold["execution_decision_count"] == 95
        assert fold["test_count"] == 92
        assert fold["audit"]["max_train_label_end_us"] < fold["audit"]["evaluation_boundary_us"]
    for model, signals in pilot["signals"].items():
        assert len(signals) == len(config["development_dates"]) * 95
        for signal in signals:
            row = data.loc[signal["source_order"]]
            assert signal["model_id"] == model
            assert signal["available_time_us"] == row["receive_time_us"] == signal["feature_cutoff_time_us"]
            assert signal["train_label_end_time_us"] < signal["available_time_us"]
            assert row["session_date"] in config["development_dates"]
        for day in config["development_dates"]:
            final_order = int(data.loc[data["session_date"] == day].index[-1])
            assert any(signal["source_order"] == final_order for signal in signals)
    encoded = json.dumps(pilot["aggregate"], allow_nan=False)
    assert "exclusion_rows" not in encoded and "target_position" in encoded
    assert "coefficients" not in encoded and "predict_proba" not in encoded


@pytest.mark.parametrize("future_change", ["prices", "truncate", "segment"])
def test_testdate_future_changes_preserve_prior_signals(pilot, future_change):
    config = fixture_config()
    data = synthetic_states(config)
    day = config["development_dates"][0]
    future = (data["session_date"] == day) & (data["source_row_position"] > 60)
    if future_change == "truncate":
        data = data.loc[~future].copy()
    elif future_change == "segment":
        data.loc[future, "segment_id"] = "future-disconnect"
    else:
        for side in ("bid", "ask"):
            for level in range(1, 6):
                data.loc[future, f"{side}_price_{level}"] = (data.loc[future, f"{side}_price_{level}"] + 10).round(2)
                data.loc[future, f"{side}_size_{level}"] *= 10
    changed = study.run_study(data, config)
    cutoff = int(data.loc[(data["session_date"] == day) & (data["source_row_position"] == 60), "source_order"].iloc[0])
    for model in study.MODEL_IDS:
        assert [s for s in pilot["signals"][model] if s["source_order"] <= cutoff] == [
            s for s in changed["signals"][model] if s["source_order"] <= cutoff
        ]


def test_long_signal_limit_forces_flat_without_using_future_labels():
    config = fixture_config()
    frame = study.causal_feature_frame(synthetic_states(config).iloc[:100], tick_size=0.01, trailing_window=5)
    train_end = int(frame["receive_time_us"].iloc[0]) - 1
    signals = study._signals(frame, np.ones(len(frame)), "test", train_end, config)
    assert [row["target_position"] for row in signals[:12]] == ["0.001"] * 10 + ["0", "0.001"]
    assert signals[-1]["source_order"] == 100


def test_main_target_exact_cent_boundaries_are_unchanged_in_both_directions():
    data = synthetic_states().iloc[:8].copy()
    for index, half_mid in enumerate([20000, 20000, 20002, 20000, 20003, 20000, 20000, 20000]):
        bid_ticks = half_mid // 2 - 1
        ask_ticks = half_mid - bid_ticks
        for level in range(1, 6):
            data.loc[index, f"bid_price_{level}"] = (bid_ticks - level + 1) / 100
            data.loc[index, f"ask_price_{level}"] = (ask_ticks + level - 1) / 100
    samples, columns, quality = study.build_research_samples(
        data, horizon_events=1, trailing_window=1, threshold_ticks=1, tick_size=0.01,
    )
    assert samples["source_order"].tolist() == [2, 3, 4, 5, 6, 7]
    assert samples["target"].tolist() == [0, 0, 1, -1, 0, 0]
    assert quality["target_class_support"] == {"-1": 1, "0": 4, "1": 1}
    assert quality["threshold_half_ticks"] == "2"
    legacy, legacy_columns, _ = build_samples(
        data, horizon_events=1, trailing_window=1, threshold_ticks=1, tick_size=0.01,
    )
    assert columns == legacy_columns
    pd.testing.assert_frame_equal(samples[columns], legacy[columns])
    assert samples["label_session_date"].eq(samples["session_date"]).all()
    off_grid = data.copy()
    off_grid.loc[0, "bid_price_1"] += 0.001
    with pytest.raises(ValueError, match="tick grid"):
        study.build_research_samples(off_grid, horizon_events=1, trailing_window=1, tick_size=0.01)


def test_final_schedule_uses_prior_final_labels_without_overlap():
    config = fixture_config()
    config.update(stage="final", final_scoring_authorized=True, precision_gate_status="exploratory_only_acknowledged")
    result = study.run_study(synthetic_states(config), config)
    final = result["aggregate"]["final"]
    assert len(final["folds"]) == len(config["final_dates"])
    assert "prior final labels" in final["schedule"]
    for index, fold in enumerate(final["folds"]):
        assert fold["test_dates"] == [config["final_dates"][index]]
        assert fold["train_dates"] == config["dates"][:9 + index]
        assert fold["audit"]["max_train_label_end_us"] < fold["audit"]["evaluation_boundary_us"]
    assert final["comparisons"]["book_logistic_vs_history_logistic"]["minimum_blocks"] == 2
    assert isinstance(final["research_decisiveness_met"], bool)
    assert all(len(signals) == 12 * 95 for signals in result["signals"].values())


def test_next_move_adaptation_features_and_targets_do_not_cross_segments():
    config = fixture_config()
    data = synthetic_states(config).iloc[:100].copy()
    data.loc[data["source_row_position"] > 50, "segment_id"] = "after_gap"
    samples, quality = replication.build_next_move_samples(data)
    assert len(samples) > 10 and quality["terminal_runs_without_next_move"] == 2
    assert samples["label_segment_id"].eq(samples["segment_id"]).all()
    assert samples.loc[samples["segment_id"] != "after_gap", "label_end_order"].max() <= 50
    changed = data.copy(deep=True)
    future = changed["source_order"] > 60
    for side in ("bid", "ask"):
        for level in range(1, 6):
            changed.loc[future, f"{side}_price_{level}"] += 20
            changed.loc[future, f"{side}_size_{level}"] *= 100
    modified, _ = replication.build_next_move_samples(changed)
    before = samples["source_order"] < 60
    pd.testing.assert_frame_equal(
        samples.loc[before, ["source_order", "queue_imbalance"]].reset_index(drop=True),
        modified.loc[modified["source_order"] < 60, ["source_order", "queue_imbalance"]].reset_index(drop=True),
    )


def test_probability_metrics_are_proper_scores_with_explicit_single_class_warning():
    metrics = replication.binary_probability_metrics([0, 0, 1, 1], [0.5] * 4)
    assert metrics["brier_score"] == 0.25 and metrics["log_loss"] == pytest.approx(math.log(2))
    assert metrics["roc_auc"] == 0.5 and metrics["accuracy"] == 0.5
    perfect = replication.binary_probability_metrics([0, 1], [0, 1])
    assert perfect["brier_score"] == 0 and math.isfinite(perfect["log_loss"])
    absent = replication.binary_probability_metrics([1, 1], [0.7, 0.8])
    assert absent["roc_auc"] is None and absent["class_support"] == [0, 2] and absent["warnings"]
    with pytest.raises(ValueError):
        replication.binary_probability_metrics([], [])


def test_next_move_uses_exact_half_tick_midpoint_and_rejects_off_grid_prices():
    data = synthetic_states().iloc[:4].copy()
    for index, (bid, ask) in enumerate(((100.01, 100.03), (100.00, 100.04), (100.02, 100.04), (100.01, 100.03))):
        for level in range(1, 6):
            data.loc[index, f"bid_price_{level}"] = bid - (level - 1) * 0.01
            data.loc[index, f"ask_price_{level}"] = ask + (level - 1) * 0.01
    samples, _ = replication.build_next_move_samples(data)
    assert samples["source_order"].tolist() == [1, 3]
    assert samples["label_end_order"].tolist() == [3, 4]
    assert samples["target"].tolist() == [1, 0]
    data.loc[0, "bid_price_1"] += 0.001
    with pytest.raises(ValueError, match="tick grid"):
        replication.build_next_move_samples(data)


def test_adaptation_is_development_only_and_prior_is_training_frequency(monkeypatch):
    config = fixture_config()
    original = replication.build_next_move_samples
    def guard(frame, **kwargs):
        assert set(frame["session_date"]).isdisjoint(config["final_dates"])
        return original(frame, **kwargs)
    monkeypatch.setattr(replication, "build_next_move_samples", guard)
    result = replication.adapt_queue_imbalance(synthetic_states(config), config)
    assert result["numerical_reproduction"] is False
    assert result["scope"] == "development_only_methodological_adaptation"
    assert len(result["folds"]) == 6
    assert result["summary"]["paper_constant_half"]["brier_score_mean"] == 0.25
    assert set(result["labelled_dates"]).isdisjoint(result["reserved_dates_not_labelled"])
    for fold in result["folds"]:
        p = fold["empirical_training_up_probability"]
        metric = fold["models"]["empirical_prior"]
        down, up = metric["class_support"]
        assert metric["brier_score"] == pytest.approx((down * p**2 + up * (1 - p)**2) / (down + up))
        assert fold["audit"]["max_train_label_end_us"] < fold["audit"]["evaluation_boundary_us"]
    json.dumps(result, allow_nan=False)
