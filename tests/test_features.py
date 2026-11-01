import numpy as np
import pandas as pd
import pytest

from market_microstructure.features import FEATURE_COLUMNS, build_samples


def states(count=100, *, date="2020-01-01", start_order=1, segment="first"):
    base = int(pd.Timestamp(date, tz="UTC").value // 1000)
    rows = []
    for index in range(count):
        mid = 100 + index * 0.5
        row = {
            "exchange": "deribit", "symbol": "BTC-PERPETUAL",
            "session_date": date, "segment_id": segment,
            "source_file": date + ".csv", "source_row_position": index + 1,
            "provenance_key": f"{date}:{start_order+index}",
            "event_time_us": base + index * 1_000_000 - 100,
            "receive_time_us": base + index * 1_000_000,
            "source_order": start_order + index,
        }
        for level in range(1, 6):
            row[f"bid_price_{level}"] = mid - 0.5 - (level - 1) * 0.5
            row[f"ask_price_{level}"] = mid + 0.5 + (level - 1) * 0.5
            row[f"bid_size_{level}"] = 2.0
            row[f"ask_size_{level}"] = 1.0
        rows.append(row)
    return pd.DataFrame(rows)


def test_features_have_declared_units_and_attributable_exclusions():
    source = states()
    samples, columns, quality = build_samples(source)
    assert len(samples) == 70
    assert columns == FEATURE_COLUMNS
    assert np.isfinite(samples[columns]).all().all()
    assert quality["exclusions"] == {"insufficient_history": 20, "future_unavailable": 10}
    assert quality["retained_samples"] + quality["excluded_samples"] == len(source)
    assert len(quality["exclusion_rows"]) == quality["excluded_samples"]
    np.testing.assert_allclose(samples["spread_ticks"], 2.0)
    np.testing.assert_allclose(samples["level1_imbalance"], 1 / 3)
    np.testing.assert_allclose(samples["depth5_imbalance"], 1 / 3)
    np.testing.assert_allclose(samples["bid_depth5"], 10.0)
    np.testing.assert_allclose(samples["ask_depth5"], 5.0)
    np.testing.assert_allclose(samples["mid_change_1_ticks"], 1.0)
    np.testing.assert_allclose(samples["mid_change_window_ticks"], 20.0)
    np.testing.assert_allclose(samples["mid_volatility_ticks"], 0.0)
    assert samples["target"].eq(1).all()
    assert "target" not in columns
    assert "label_end_time" not in columns


def test_mutating_future_records_does_not_change_earlier_features():
    source = states()
    baseline, columns, _ = build_samples(source)
    changed = source.copy(deep=True)
    future = changed["source_order"] > 60
    for side in ("bid", "ask"):
        for level in range(1, 6):
            changed.loc[future, f"{side}_price_{level}"] -= 50
            changed.loc[future, f"{side}_size_{level}"] *= 100
    changed["future_only_signal"] = np.arange(len(changed)) * 999
    perturbed, actual_columns, _ = build_samples(changed)
    earlier = baseline["source_order"] <= 60
    assert earlier.sum() > 20
    assert actual_columns == columns
    assert "future_only_signal" not in actual_columns
    pd.testing.assert_frame_equal(
        baseline.loc[earlier, columns].reset_index(drop=True),
        perturbed.loc[perturbed["source_order"] <= 60, columns].reset_index(drop=True),
    )
    # At least one eligible target really did observe the deliberately changed future.
    affected = baseline["source_order"].between(51, 60)
    assert not np.array_equal(baseline.loc[affected, "target"], perturbed.loc[affected, "target"])


def test_no_feature_or_label_crosses_an_invalid_segment_or_gap():
    first = states(40)
    second = states(40, start_order=41, segment="after_gap")
    second["receive_time_us"] += 100_000_000
    second["event_time_us"] += 100_000_000
    for side in ("bid", "ask"):
        for level in range(1, 6):
            second[f"{side}_price_{level}"] += 1000
    combined = pd.concat([first, second], ignore_index=True)
    samples, _, quality = build_samples(combined)
    assert len(samples) == 20
    assert quality["segments"] == 2
    assert samples["segment_id"].eq(samples["label_segment_id"]).all()
    assert samples.loc[samples["segment_id"] == "first", "label_end_order"].max() <= 40
    assert samples.loc[samples["segment_id"] == "after_gap", "feature_order"].min() == 61
    assert samples.loc[samples["segment_id"] == "after_gap", "mid_change_window_ticks"].eq(20).all()


def test_calendar_and_file_boundaries_reset_windows_even_if_segment_id_repeats():
    first = states(35)
    second = states(35, date="2020-02-01", start_order=36)
    samples, _, quality = build_samples(pd.concat([first, second], ignore_index=True))
    assert len(samples) == 10
    assert quality["segments"] == 2
    assert samples["session_date"].eq(samples["label_session_date"]).all()
    assert samples["source_file"].eq(samples["label_source_file"]).all()


def test_three_classes_use_strict_threshold_and_future_source_provenance():
    source = states(7)
    mids = [100.0, 100.5, 101.5, 101.0, 99.5, 99.5, 101.0]
    for level in range(1, 6):
        source[f"bid_price_{level}"] = np.asarray(mids) - 0.5 - (level - 1) * 0.5
        source[f"ask_price_{level}"] = np.asarray(mids) + 0.5 + (level - 1) * 0.5
    samples, _, _ = build_samples(source, horizon_events=1, trailing_window=1, threshold_ticks=1)
    assert samples["target"].tolist() == [1, 0, -1, 0, 1]
    assert samples["label_end_order"].tolist() == [3, 4, 5, 6, 7]
    assert samples["label_provenance_key"].tolist() == source["provenance_key"].iloc[2:].tolist()


def test_equal_timestamps_keep_capture_order_and_future_endpoint_order():
    source = states()
    base = int(source["receive_time_us"].iloc[0])
    source["receive_time_us"] = base + (np.arange(len(source)) // 2) * 1_000_000
    source["event_time_us"] = source["receive_time_us"]
    first, columns, _ = build_samples(source)
    again, _, _ = build_samples(source)
    pd.testing.assert_frame_equal(first, again)
    assert first["feature_order"].tolist() == list(range(21, 91))
    assert (first["label_end_order"] - first["feature_order"]).eq(10).all()
    assert np.isfinite(first[columns]).all().all()


def test_zero_opposing_depth_is_explicitly_finite():
    source = states()
    for side in ("bid", "ask"):
        for level in range(1, 6):
            source[f"{side}_size_{level}"] = 0.0
    samples, columns, quality = build_samples(source)
    assert len(samples) > 0
    assert samples["level1_imbalance"].eq(0).all()
    assert samples["depth5_imbalance"].eq(0).all()
    assert quality["zero_l1_denominator_states"] == 100
    assert np.isfinite(samples[columns]).all().all()


def test_short_segments_are_reported_rather_than_vacuously_passing():
    samples, columns, quality = build_samples(states(9))
    assert samples.empty
    assert set(columns).issubset(samples.columns)
    assert quality["retained_samples"] == 0
    assert quality["excluded_samples"] == 9
    assert quality["exclusions"] == {"insufficient_history": 9, "future_unavailable": 0}
    with pytest.raises(ValueError, match="empty"):
        build_samples(states().iloc[:0])


@pytest.mark.parametrize("arguments", [
    {"horizon_events": 0}, {"horizon_events": 1.5}, {"horizon_events": True},
    {"trailing_window": 0}, {"tick_size": 0}, {"tick_size": float("nan")},
    {"threshold_ticks": -1}, {"threshold_ticks": float("inf")},
])
def test_invalid_research_parameters_are_rejected(arguments):
    with pytest.raises(ValueError):
        build_samples(states(), **arguments)


@pytest.mark.parametrize("mutation", ["missing", "decreased_time", "duplicated_order", "crossed", "unordered_depth", "negative_size", "nonfinite"])
def test_malformed_normalized_inputs_are_rejected(mutation):
    source = states()
    if mutation == "missing":
        source = source.drop(columns="bid_price_5")
    elif mutation == "decreased_time":
        source.loc[40, "receive_time_us"] = source.loc[39, "receive_time_us"] - 1
    elif mutation == "duplicated_order":
        source.loc[40, "source_order"] = source.loc[39, "source_order"]
    elif mutation == "crossed":
        source.loc[40, "bid_price_1"] = source.loc[40, "ask_price_1"]
    elif mutation == "unordered_depth":
        source.loc[40, "ask_price_5"] = source.loc[40, "ask_price_1"] - 1
    elif mutation == "negative_size":
        source.loc[40, "ask_size_1"] = -1
    else:
        source.loc[40, "bid_price_1"] = np.inf
    with pytest.raises(ValueError):
        build_samples(source)


def test_noncontiguous_reused_segment_is_rejected():
    source = states()
    source.loc[30:60, "segment_id"] = "different"
    with pytest.raises(ValueError, match="noncontiguous"):
        build_samples(source)


def test_declared_session_date_must_match_actual_utc_receipt_date():
    source = states()
    source["session_date"] = "2020-02-01"
    with pytest.raises(ValueError, match="UTC calendar date"):
        build_samples(source)
