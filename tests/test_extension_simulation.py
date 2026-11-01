from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
import json

import pandas as pd
import pytest

from market_microstructure.extension.analytics import summarize_segments
from market_microstructure.extension.replay import iter_observations
from market_microstructure.extension.simulation import SimulationConfig, simulate


BASE = int(pd.Timestamp("2021-01-01T12:00:00Z").value // 1000)


def book(count=4, *, bids=None, asks=None, segments=None, timestamps=None):
    bids = bids or [99] * count
    asks = asks or [100] * count
    segments = segments or ["one"] * count
    timestamps = timestamps or [BASE + index * 1_000_000 for index in range(count)]
    rows = []
    for index in range(count):
        row = {
            "exchange": "bitstamp", "symbol": "BTCUSD", "session_date": "2021-01-01",
            "segment_id": segments[index], "source_file": "synthetic-test.csv",
            "source_row_position": index + 1, "provenance_key": f"test:{index+1}",
            "event_time_us": timestamps[index] - 1000,
            "receive_time_us": timestamps[index], "source_order": index + 1,
        }
        for level in range(1, 6):
            row[f"bid_price_{level}"] = float(bids[index] - level + 1)
            row[f"ask_price_{level}"] = float(asks[index] + level - 1)
            row[f"bid_size_{level}"] = 10.0
            row[f"ask_size_{level}"] = 10.0
        rows.append(row)
    return pd.DataFrame(rows)


def config(**changes):
    parameters = {
        "initial_cash": "1000", "max_position": "2", "quantity_step": "0.1",
        "price_tick": "1", "fee_bps": "0", "slippage_bps": "0", "latency_us": 0,
        "max_quote_age_us": 1_000_000, "dataset_id": "explicit-synthetic-test",
    }
    parameters.update(changes)
    return SimulationConfig(**parameters)


def signal(source, position, states, **changes):
    row = states.loc[states["source_order"] == source].iloc[0]
    record = {
        "source_order": source, "available_time_us": int(row["receive_time_us"]),
        "target_position": str(position), "model_id": "test-model",
        "train_label_end_time_us": BASE - 1_000_000,
        "feature_cutoff_time_us": int(row["receive_time_us"]),
    }
    record.update(changes)
    return record


def d(value):
    return Decimal(value)


def test_hand_calculated_roundtrip_charges_both_fees_and_marks_drawdown():
    states = book(bids=[99, 99, 109, 109], asks=[100, 100, 110, 110])
    result = simulate(states, [signal(1, 1, states), signal(3, 0, states)], config(fee_bps="10"))
    assert [fill["source_order"] for fill in result["fills"]] == [2, 4]
    assert [fill["execution_price_quote"] for fill in result["fills"]] == ["100", "109"]
    assert [fill["fee_quote"] for fill in result["fills"]] == ["0.1", "0.109"]
    summary = result["aggregate"]
    assert d(summary["net_pnl_quote"]) == d("8.791")
    assert d(summary["gross_pnl_quote"]) == d("9")
    assert d(summary["fees_quote"]) == d("0.209")
    assert d(summary["realized_pnl_quote"]) == d("8.791")
    assert d(summary["unrealized_pnl_quote"]) == 0
    assert d(summary["max_drawdown_quote"]) == d("1.1")
    assert summary["roundtrip_trade_count"] == 1
    assert summary["exposure_time_us"] == 2_000_000
    assert summary["fill_count"] == 2
    assert result["segments"][0]["final_cash_quote"] == "1008.791"
    assert result["ledger"][-1]["pending_order_id"] is None
    json.dumps(result, allow_nan=False)


def test_adverse_slippage_and_price_rounding_are_in_the_accounting():
    states = book(bids=[99, 99, 109, 109], asks=[100, 100, 110, 110])
    result = simulate(
        states, [signal(1, 1, states), signal(3, 0, states)],
        config(fee_bps="10", slippage_bps="100"),
    )
    assert [fill["execution_price_quote"] for fill in result["fills"]] == ["101", "107"]
    assert d(result["aggregate"]["slippage_and_rounding_quote"]) == 3
    assert d(result["aggregate"]["fees_quote"]) == d("0.208")
    assert d(result["aggregate"]["net_pnl_quote"]) == d("5.792")
    assert d(result["aggregate"]["gross_pnl_quote"]) == 6


def test_partial_depth_fills_cancel_remaining_ioc_quantity():
    states = book(2)
    for level, quantity in enumerate([0.2, 0.1, 0, 0, 0], start=1):
        states.loc[1, f"ask_size_{level}"] = quantity
    result = simulate(states, [signal(1, 2, states)], config())
    order = result["orders"][0]
    assert order["status"] == "partially_filled_cancelled"
    assert order["filled_quantity_base"] == "0.3"
    assert order["cancelled_quantity_base"] == "1.7"
    assert [fill["book_level"] for fill in result["fills"]] == [1, 2]
    assert [fill["quantity_base"] for fill in result["fills"]] == ["0.2", "0.1"]
    assert result["segments"][0]["unresolved_inventory_base"] == "0.3"
    assert d(result["aggregate"]["net_pnl_quote"]) == d("-0.4")
    assert result["aggregate"]["partial_ioc_orders"] == 1


def test_buy_cash_limit_includes_fees_and_never_borrows():
    states = book(2)
    result = simulate(
        states, [signal(1, 2, states)], config(initial_cash="100.5", fee_bps="100"),
    )
    assert result["orders"][0]["reason"] == "insufficient_cash"
    assert result["orders"][0]["filled_quantity_base"] == "0.9"
    assert result["segments"][0]["final_cash_quote"] == "9.6"
    assert result["aggregate"]["cash_limited_orders"] == 1
    assert all(d(row["cash_quote"]) >= 0 for row in result["ledger"])
    assert all(d(row["position_base"]) <= 2 for row in result["ledger"])


def test_no_affordable_lot_is_an_explicit_rejection():
    states = book(2)
    result = simulate(states, [signal(1, 1, states)], config(initial_cash="0.01"))
    assert not result["fills"]
    assert result["orders"][0]["status"] == "rejected"
    assert result["orders"][0]["reason"] == "insufficient_cash"
    assert result["aggregate"]["net_pnl_quote"] == "0"


def test_target_rounds_down_to_lot_without_exceeding_requested_exposure():
    states = book(2)
    result = simulate(states, [signal(1, "1.09", states)], config())
    assert result["orders"][0]["requested_target_position_base"] == "1.09"
    assert result["orders"][0]["rounded_target_position_base"] == "1"
    assert result["fills"][0]["quantity_base"] == "1"


def test_partial_sale_cost_basis_and_unresolved_inventory_reconcile_exactly():
    states = book(bids=[99, 99, 110, 110], asks=[100, 100, 111, 111])
    for level in range(1, 6):
        states.loc[3, f"bid_size_{level}"] = 1.0 if level == 1 else 0.0
    result = simulate(states, [signal(1, 2, states), signal(3, 0, states)], config(fee_bps="10"))
    end = result["segments"][0]
    assert end["unresolved_inventory_base"] == "1"
    assert d(end["realized_pnl_quote"]) == d("9.79")
    assert d(end["unrealized_pnl_quote"]) == d("9.9")
    assert d(end["net_pnl_quote"]) == d("19.69")
    assert d(end["realized_pnl_quote"]) + d(end["unrealized_pnl_quote"]) == d(end["net_pnl_quote"])
    assert result["aggregate"]["roundtrip_trade_count"] == 0


def test_zero_latency_requires_a_later_source_event_even_at_tied_timestamps():
    states = book(2, timestamps=[BASE, BASE])
    result = simulate(states, [signal(1, 1, states)], config())
    assert len(result["fills"]) == 1
    assert result["fills"][0]["source_order"] == 2
    assert result["fills"][0]["receive_time_us"] == BASE
    delayed = simulate(states, [signal(1, 1, states)], config(latency_us=1))
    assert delayed["fills"] == []
    assert delayed["orders"][0]["reason"] == "end_of_replay"


def test_last_observation_order_cannot_fill_on_its_own_book():
    states = book(1)
    result = simulate(states, [signal(1, 1, states)], config())
    assert result["fills"] == []
    assert result["orders"][0]["status"] == "cancelled"
    assert result["orders"][0]["reason"] == "end_of_replay"


def test_keep_first_pending_policy_ignores_intervening_signals_without_stacking():
    states = book(5)
    result = simulate(
        states, [signal(1, 1, states), signal(2, 2, states), signal(3, 2, states)],
        config(latency_us=2_000_000),
    )
    assert [fill["source_order"] for fill in result["fills"]] == [3, 5]
    assert [order["quantity_base"] for order in result["orders"]] == ["1", "1"]
    assert result["signal_events"][1]["reason"] == "pending_order_exists_keep_first"
    assert result["aggregate"]["ignored_pending_signals"] == 1
    assert result["segments"][0]["unresolved_inventory_base"] == "2"


def test_pending_order_is_cancelled_across_an_observed_segment_boundary():
    states = book(4, segments=["a", "a", "b", "b"])
    result = simulate(states, [signal(1, 1, states)], config(latency_us=2_000_000))
    assert not result["fills"]
    assert result["orders"][0]["reason"] == "segment_boundary"
    assert len(result["segments"]) == 2
    assert result["aggregate"]["net_pnl_quote"] == "0"


def test_open_inventory_is_marked_then_independent_cash_restarts_without_a_fake_sale():
    states = book(4, segments=["a", "a", "b", "b"])
    result = simulate(states, [signal(1, 1, states)], config())
    first, second = result["segments"]
    assert len(result["fills"]) == 1 and result["fills"][0]["side"] == "buy"
    assert first["unresolved_inventory_base"] == "1"
    assert first["net_pnl_quote"] == "-1"
    assert second["initial_cash_quote"] == second["final_cash_quote"] == "1000"
    assert second["unresolved_inventory_base"] == "0"
    assert result["aggregate"]["sum_independent_segment_pnl_quote"] == "-1"
    assert result["aggregate"]["unresolved_position_segments"] == 1
    assert "continuous investable" in result["aggregate"]["capital_convention"]
    assert "annualized" in result["aggregate"]["annualization"]
    assert "final_cash_quote" not in result["aggregate"]


@pytest.mark.parametrize("age,reason,counter", [
    (2_000_000, "stale_quote", "stale_quote_rejections"),
    (-1, "exchange_clock_ahead", "clock_skew_rejections"),
])
def test_stale_and_clock_skew_quotes_are_preserved_but_not_executed(age, reason, counter):
    states = book(2)
    states.loc[1, "event_time_us"] = int(states.loc[1, "receive_time_us"]) - age
    assert len(list(iter_observations(states))) == 2
    result = simulate(states, [signal(1, 1, states)], config())
    assert not result["fills"]
    assert result["orders"][0]["reason"] == reason
    assert result["aggregate"][counter] == 1


def test_future_book_perturbation_cannot_change_earlier_ledger_or_fills():
    original = book(6)
    signals = [signal(1, 1, original), signal(3, 0, original)]
    first = simulate(original, signals, config())
    changed = original.copy(deep=True)
    later = changed["source_order"] > 3
    for side in ("bid", "ask"):
        for level in range(1, 6):
            changed.loc[later, f"{side}_price_{level}"] += 500
            changed.loc[later, f"{side}_size_{level}"] *= 10
    second = simulate(changed, signals, config())
    assert [row for row in first["ledger"] if row["source_order"] <= 3] == [
        row for row in second["ledger"] if row["source_order"] <= 3
    ]
    assert [row for row in first["fills"] if row["source_order"] <= 3] == [
        row for row in second["fills"] if row["source_order"] <= 3
    ]
    assert first["aggregate"]["net_pnl_quote"] != second["aggregate"]["net_pnl_quote"]
    assert first["ledger_sha256"] != second["ledger_sha256"]


def test_splitting_batches_does_not_change_tie_order_or_canonical_ledger():
    states = book(5, timestamps=[BASE, BASE, BASE + 1_000_000, BASE + 2_000_000, BASE + 3_000_000])
    signals = [signal(1, 1, states), signal(3, 0, states)]
    whole = simulate(states, signals, config())
    batches = [states.iloc[:1], states.iloc[:0], states.iloc[1:3], states.iloc[3:]]
    split = simulate(iter(batches), signals, config())
    assert split == whole
    assert split["ledger_sha256"] == whole["ledger_sha256"]


def test_decision_view_is_deeply_immutable_and_contains_no_future_handle():
    states = book(2)
    view = next(iter_observations(states))
    with pytest.raises(FrozenInstanceError):
        view.source_order = 2
    with pytest.raises(FrozenInstanceError):
        view.bids[0].price = d("1")
    with pytest.raises(AttributeError):
        _ = view.future
    price = view.bids[0].price
    states.loc[0, "bid_price_1"] = 1000
    assert view.bids[0].price == price


@pytest.mark.parametrize("field,value", [
    ("initial_cash", "0"), ("max_position", "-1"), ("quantity_step", "0"),
    ("price_tick", "NaN"), ("initial_cash", "Infinity"), ("fee_bps", "-1"),
    ("slippage_bps", "10000"), ("latency_us", -1), ("latency_us", True),
    ("max_quote_age_us", 0.5), ("max_quote_age_us", False),
    ("initial_cash", True), ("market_type", "inverse"),
    ("base_currency", "USD"),
])
def test_invalid_accounting_configuration_is_rejected(field, value):
    with pytest.raises(ValueError):
        config(**{field: value})


def test_existing_inverse_instrument_can_never_silently_use_spot_accounting():
    with pytest.raises(ValueError, match="Derivative/inverse"):
        config(exchange="deribit", symbol="BTC-PERPETUAL")


@pytest.mark.parametrize("mutation", [
    "duplicate_order", "duplicate_provenance", "decreasing_receipt", "crossed",
    "unordered", "negative_quantity", "nonfinite", "off_tick", "off_lot",
    "wrong_date", "noncontiguous_segment", "different_market",
])
def test_invalid_replay_observations_are_rejected(mutation):
    states = book(3)
    if mutation == "duplicate_order":
        states.loc[1, "source_order"] = 1
    elif mutation == "duplicate_provenance":
        states.loc[1, "provenance_key"] = states.loc[0, "provenance_key"]
    elif mutation == "decreasing_receipt":
        states.loc[1, "receive_time_us"] = BASE - 1
    elif mutation == "crossed":
        states.loc[1, "bid_price_1"] = states.loc[1, "ask_price_1"]
    elif mutation == "unordered":
        states.loc[1, "ask_price_2"] = states.loc[1, "ask_price_1"]
    elif mutation == "negative_quantity":
        states.loc[1, "ask_size_1"] = -1
    elif mutation == "nonfinite":
        states.loc[1, "ask_price_1"] = float("nan")
    elif mutation == "off_tick":
        states.loc[1, "ask_price_1"] += 0.1
    elif mutation == "off_lot":
        states.loc[1, "ask_size_1"] = 0.15
    elif mutation == "wrong_date":
        states["session_date"] = "2021-02-01"
    elif mutation == "noncontiguous_segment":
        states["segment_id"] = ["a", "b", "a"]
    else:
        states.loc[1, "exchange"] = "other"
    with pytest.raises(ValueError):
        simulate(states, [], config())


@pytest.mark.parametrize("mutation", [
    "future_training", "future_features", "wrong_available", "unmatched",
    "negative_target", "excess_target", "nan_target", "duplicate", "mixed_model",
])
def test_invalid_or_leaking_signals_are_rejected(mutation):
    states = book(3)
    records = [signal(1, 1, states)]
    if mutation == "future_training":
        records[0]["train_label_end_time_us"] = records[0]["available_time_us"]
    elif mutation == "future_features":
        records[0]["feature_cutoff_time_us"] += 1
    elif mutation == "wrong_available":
        records[0]["available_time_us"] += 1
    elif mutation == "unmatched":
        records[0]["source_order"] = 999
    elif mutation == "negative_target":
        records[0]["target_position"] = "-0.1"
    elif mutation == "excess_target":
        records[0]["target_position"] = "2.1"
    elif mutation == "nan_target":
        records[0]["target_position"] = "NaN"
    elif mutation == "duplicate":
        records.append(dict(records[0]))
    else:
        records.append(signal(2, 0, states, model_id="another-model"))
    with pytest.raises(ValueError):
        simulate(states, records, config())


def test_empty_replay_is_rejected_and_flat_signals_do_not_create_short_positions():
    states = book(2)
    with pytest.raises(ValueError, match="at least one"):
        simulate(states.iloc[:0], [], config())
    result = simulate(states, [signal(1, 0, states)], config())
    assert result["orders"] == result["fills"] == []
    assert result["aggregate"]["net_pnl_quote"] == "0"
    assert result["aggregate"]["unresolved_position_segments"] == 0
    with pytest.raises(ValueError):
        summarize_segments([])


def test_tiny_spot_lots_and_fractional_fees_ignore_the_callers_decimal_precision():
    states = book(4, bids=[100] * 4, asks=[100.01] * 4)
    signals = [signal(1, "0.00000001", states), signal(3, 0, states)]
    with localcontext() as caller:
        caller.prec = 6
        result = simulate(
            states, signals,
            config(initial_cash="10000", max_position="0.00000001",
                   quantity_step="0.00000001", price_tick="0.01",
                   fee_bps="10", slippage_bps="1"),
        )
        assert caller.prec == 6
    assert [fill["execution_price_quote"] for fill in result["fills"]] == ["100.03", "99.99"]
    assert result["aggregate"]["fees_quote"] == "0.0000000020002"
    assert result["aggregate"]["net_pnl_quote"] == "-0.0000000024002"
    assert result["segments"][0]["final_cash_quote"] == "9999.9999999975998"


def test_signal_lineage_hash_changes_even_when_financial_orders_do_not():
    states = book(2)
    first_signals = [signal(1, 1, states)]
    other_signals = [signal(1, 1, states, train_label_end_time_us=BASE - 2_000_000)]
    first = simulate(states, first_signals, config())
    second = simulate(states, other_signals, config())
    assert first["ledger_sha256"] == second["ledger_sha256"]
    assert first["fills"] == second["fills"]
    assert first["signals_sha256"] != second["signals_sha256"]
    assert first["simulation_sha256"] != second["simulation_sha256"]


def test_float_artifacts_are_not_hidden_by_grid_tolerances():
    states = book(2)
    states.loc[1, "ask_price_1"] = 100.00000000000001
    with pytest.raises(ValueError, match="price_tick grid"):
        simulate(states, [], config(price_tick="0.01"))
