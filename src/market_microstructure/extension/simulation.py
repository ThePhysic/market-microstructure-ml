"""Decimal spot-only marketable IOC simulation on later observed books.

This intentionally models neither passive queues nor a continuously tradeable
market between supplied segments. Detailed ledgers are local historical assets.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR, localcontext
import hashlib
import json
import re
from typing import Any, Iterable, Mapping

import pandas as pd

from .analytics import summarize_segments
from .replay import (
    DecisionView, ReplayError, decimal_text, decimal_value, integer_value,
    iter_observations,
)

ZERO = Decimal(0)
BPS = Decimal(10_000)


@dataclass(frozen=True)
class SimulationConfig:
    initial_cash: Any = "10000"
    max_position: Any = "0.001"
    quantity_step: Any = "0.00000001"
    price_tick: Any = "0.01"
    fee_bps: Any = "10"
    slippage_bps: Any = "1"
    latency_us: int = 100_000
    max_quote_age_us: int = 30_000_000
    exchange: str = "bitstamp"
    symbol: str = "BTCUSD"
    base_currency: str = "BTC"
    quote_currency: str = "USD"
    market_type: str = "spot"
    dataset_id: str = "unspecified"
    model_id: str = "unspecified"
    scenario_id: str = "base"

    def __post_init__(self) -> None:
        for name in ("initial_cash", "max_position", "quantity_step", "price_tick", "fee_bps", "slippage_bps"):
            value = decimal_value(getattr(self, name), name)
            if value < 0 or (name not in ("fee_bps", "slippage_bps") and value == 0):
                raise ValueError(f"{name} must be {'nonnegative' if name in ('fee_bps', 'slippage_bps') else 'positive'}")
            object.__setattr__(self, name, value)
        if self.quantity_step > self.max_position:
            raise ValueError("max_position must allow at least one quantity_step")
        if self.fee_bps >= BPS or self.slippage_bps >= BPS:
            raise ValueError("Spot fees and adverse slippage must be below 10000 bps")
        for name in ("latency_us", "max_quote_age_us"):
            object.__setattr__(self, name, integer_value(getattr(self, name), name))
        for name in ("exchange", "symbol", "dataset_id", "model_id", "scenario_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a nonempty string")
        for name in ("base_currency", "quote_currency"):
            if not isinstance(getattr(self, name), str) or not re.fullmatch(r"[A-Z0-9]{2,12}", getattr(self, name)):
                raise ValueError(f"{name} must be an uppercase currency code")
        if self.base_currency == self.quote_currency:
            raise ValueError("Base and quote currencies must differ")
        if self.market_type != "spot":
            raise ValueError("Only explicit spot accounting is implemented")
        if self.exchange.lower() in {"deribit", "binance-futures", "bitmex"} or any(
            marker in self.symbol.upper() for marker in ("PERPETUAL", "PERP", "SWAP", "FUTURE")
        ):
            raise ValueError("Derivative/inverse instruments cannot use this spot simulator")

    def to_dict(self) -> dict[str, Any]:
        return {
            item.name: decimal_text(value) if isinstance(value := getattr(self, item.name), Decimal) else value
            for item in fields(self)
        }


@dataclass(frozen=True)
class _Signal:
    source_order: int
    available_time_us: int
    target_position: Decimal
    model_id: str
    train_label_end_time_us: int
    feature_cutoff_time_us: int


def _signals(records: Iterable[Mapping[str, Any]], config: SimulationConfig) -> tuple[dict[int, _Signal], str]:
    if isinstance(records, (str, bytes, Mapping)) or records is None:
        raise ValueError("signals must be an iterable of signal records")
    result = {}
    previous_order = 0
    model_id = None
    required = {item.name for item in fields(_Signal)}
    for record in records:
        if not isinstance(record, Mapping) or required - set(record):
            raise ValueError("Every signal must contain the declared timing, target, model and source fields")
        order = integer_value(record["source_order"], "signal source_order", positive=True)
        if order <= previous_order:
            raise ValueError("Signal source_order must be unique and strictly increasing")
        available = integer_value(record["available_time_us"], "available_time_us")
        train_end = integer_value(record["train_label_end_time_us"], "train_label_end_time_us")
        cutoff = integer_value(record["feature_cutoff_time_us"], "feature_cutoff_time_us")
        if train_end >= available:
            raise ValueError("A training label ending at/after signal availability is future leakage")
        if cutoff > available:
            raise ValueError("A feature cutoff later than signal availability is future leakage")
        target = decimal_value(record["target_position"], "target_position")
        if not ZERO <= target <= config.max_position:
            raise ValueError("Signal target_position violates long/flat spot exposure bounds")
        identity = record["model_id"]
        if not isinstance(identity, str) or not identity.strip():
            raise ValueError("Signal model_id must be a nonempty string")
        if model_id is not None and identity != model_id:
            raise ValueError("Simulate one model at a time; mixed model signals are ambiguous")
        if config.model_id != "unspecified" and config.model_id != identity:
            raise ValueError("Signal model_id differs from SimulationConfig")
        model_id = identity
        result[order] = _Signal(order, available, target, identity, train_end, cutoff)
        previous_order = order
    return result, model_id or config.model_id


def _round_steps(value: Decimal, step: Decimal, rounding=ROUND_FLOOR) -> Decimal:
    return (value / step).to_integral_value(rounding=rounding) * step


def _hash(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _signal_hash(signals: Mapping[int, _Signal]) -> str:
    """Hash canonical normalized signal records in source order without a copy."""
    digest = hashlib.sha256()
    for signal in signals.values():
        record = {
            item.name: decimal_text(value) if isinstance(value := getattr(signal, item.name), Decimal) else value
            for item in fields(signal)
        }
        digest.update(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


_COUNTERS = (
    "submitted_orders", "filled_orders", "fills", "partial_ioc_orders",
    "stale_quote_rejections", "clock_skew_rejections", "cash_limited_orders",
    "ignored_pending_signals", "terminal_cancelled_orders", "roundtrip_trade_count",
    "exposure_time_us",
)


class _Engine:
    def __init__(self, config: SimulationConfig, model_id: str) -> None:
        self.config = config
        self.model_id = model_id
        self.cash = config.initial_cash
        self.position = ZERO
        self.cost_basis = ZERO
        self.realized = ZERO
        self.pending: dict[str, Any] | None = None
        self.current: dict[str, Any] | None = None
        self.last: DecisionView | None = None
        self.orders: list[dict[str, Any]] = []
        self.fills: list[dict[str, Any]] = []
        self.ledger: list[dict[str, Any]] = []
        self.signal_events: list[dict[str, Any]] = []
        self.segments: list[dict[str, Any]] = []

    def begin(self, observation: DecisionView) -> None:
        self.cash, self.position = self.config.initial_cash, ZERO
        self.cost_basis = self.realized = ZERO
        self.last = None
        self.current = {
            "session_date": observation.session_date, "segment_id": observation.segment_id,
            "source_file": observation.source_file, "source_order_start": observation.source_order,
            "start_time_us": observation.receive_time_us, "observations": 0,
            **{key: 0 for key in _COUNTERS},
            "_fees": ZERO, "_slippage": ZERO, "_turnover": ZERO,
            "_buy": ZERO, "_sell": ZERO, "_peak": self.config.initial_cash,
            "_drawdown": ZERO, "_drawdown_fraction": ZERO,
        }

    def mark(self, observation: DecisionView, *, terminal: bool = False) -> None:
        assert self.current is not None
        equity = self.cash + self.position * observation.bids[0].price
        self.current["_peak"] = max(self.current["_peak"], equity)
        drawdown = self.current["_peak"] - equity
        self.current["_drawdown"] = max(self.current["_drawdown"], drawdown)
        fraction = drawdown / self.current["_peak"] if self.current["_peak"] else ZERO
        self.current["_drawdown_fraction"] = max(self.current["_drawdown_fraction"], fraction)
        self.ledger.append({
            "event": "segment_end" if terminal else "observation",
            "source_order": observation.source_order, "receive_time_us": observation.receive_time_us,
            "session_date": observation.session_date, "segment_id": observation.segment_id,
            "provenance_key": observation.provenance_key, "model_id": self.model_id,
            "cash_quote": decimal_text(self.cash), "position_base": decimal_text(self.position),
            "equity_marked_bid_quote": decimal_text(equity),
            "pending_order_id": self.pending["order_id"] if self.pending is not None else None,
        })

    def cancel_terminal(self, reason: str) -> None:
        assert self.current is not None and self.last is not None
        if self.pending is not None:
            self.pending.update(
                status="cancelled", reason=reason,
                cancelled_quantity_base=self.pending["quantity_base"],
                terminal_time_us=self.last.receive_time_us,
                terminal_source_order=self.last.source_order,
            )
            self.current["terminal_cancelled_orders"] += 1
            self.pending = None

    def finish(self, reason: str) -> None:
        assert self.current is not None and self.last is not None
        self.cancel_terminal(reason)
        self.mark(self.last, terminal=True)
        mark_value = self.position * self.last.bids[0].price
        equity = self.cash + mark_value
        pnl = equity - self.config.initial_cash
        # Cash/position accounting is the authoritative exact marked PnL.
        unrealized = pnl - self.realized
        summary = {
            key: value for key, value in self.current.items() if not key.startswith("_")
        }
        summary.update({
            "end_time_us": self.last.receive_time_us,
            "source_order_end": self.last.source_order,
            "observed_duration_us": self.last.receive_time_us - self.current["start_time_us"],
            "initial_cash_quote": decimal_text(self.config.initial_cash),
            "final_cash_quote": decimal_text(self.cash),
            "final_equity_marked_bid_quote": decimal_text(equity),
            "net_pnl_quote": decimal_text(pnl),
            "gross_pnl_quote": decimal_text(pnl + self.current["_fees"]),
            "realized_pnl_quote": decimal_text(self.realized),
            "unrealized_pnl_quote": decimal_text(unrealized),
            "net_return": decimal_text(pnl / self.config.initial_cash),
            "fees_quote": decimal_text(self.current["_fees"]),
            "slippage_and_rounding_quote": decimal_text(self.current["_slippage"]),
            "turnover_quote": decimal_text(self.current["_turnover"]),
            "buy_quantity_base": decimal_text(self.current["_buy"]),
            "sell_quantity_base": decimal_text(self.current["_sell"]),
            "unresolved_inventory_base": decimal_text(self.position),
            "unresolved_inventory_mark_quote": decimal_text(mark_value),
            "unresolved_inventory": self.position != ZERO,
            "max_drawdown_quote": decimal_text(self.current["_drawdown"]),
            "max_drawdown_fraction": decimal_text(self.current["_drawdown_fraction"]),
            "terminal_policy": reason + "; open inventory marked at last observed best bid, never force-filled",
        })
        self.segments.append(summary)
        self.current = None
        self.last = None

    def receive(self, observation: DecisionView, signal: _Signal) -> None:
        assert self.current is not None
        if signal.available_time_us != observation.receive_time_us:
            raise ValueError("Signal availability must equal its matched source observation receipt timestamp")
        if signal.feature_cutoff_time_us > observation.receive_time_us:
            raise ValueError("A signal cannot use features later than its source event")
        target = _round_steps(signal.target_position, self.config.quantity_step)
        decision = {
            "source_order": observation.source_order, "available_time_us": signal.available_time_us,
            "feature_cutoff_time_us": signal.feature_cutoff_time_us,
            "train_label_end_time_us": signal.train_label_end_time_us, "model_id": signal.model_id,
            "requested_target_position_base": decimal_text(signal.target_position),
            "rounded_target_position_base": decimal_text(target),
        }
        if self.pending is not None:
            self.current["ignored_pending_signals"] += 1
            decision.update(status="ignored", reason="pending_order_exists_keep_first")
        else:
            delta = target - self.position
            quantity = _round_steps(abs(delta), self.config.quantity_step)
            if quantity == ZERO:
                decision.update(status="no_order", reason="already_at_rounded_target")
            else:
                order = {
                    "order_id": f"order-{len(self.orders)+1:08d}", "model_id": self.model_id,
                    "session_date": observation.session_date, "segment_id": observation.segment_id,
                    "origin_source_order": observation.source_order,
                    "origin_provenance_key": observation.provenance_key,
                    "submitted_time_us": signal.available_time_us,
                    "eligible_time_us": signal.available_time_us + self.config.latency_us,
                    "side": "buy" if delta > 0 else "sell", "type": "marketable_ioc",
                    "quantity_base": decimal_text(quantity),
                    "requested_target_position_base": decimal_text(signal.target_position),
                    "rounded_target_position_base": decimal_text(target),
                    "filled_quantity_base": "0", "status": "pending",
                }
                self.orders.append(order)
                self.pending = order
                self.current["submitted_orders"] += 1
                decision.update(status="submitted", order_id=order["order_id"])
        self.signal_events.append(decision)

    def reject(self, observation: DecisionView, reason: str) -> None:
        assert self.pending is not None
        self.pending.update(
            status="rejected", reason=reason, attempted_time_us=observation.receive_time_us,
            attempted_source_order=observation.source_order,
            cancelled_quantity_base=self.pending["quantity_base"],
        )
        self.pending = None

    def execute(self, observation: DecisionView) -> None:
        assert self.pending is not None and self.current is not None
        order = self.pending
        if observation.source_order <= order["origin_source_order"] or observation.receive_time_us < order["eligible_time_us"]:
            return
        age = observation.receive_time_us - observation.event_time_us
        if age < 0:
            self.current["clock_skew_rejections"] += 1
            self.reject(observation, "exchange_clock_ahead")
            return
        if age > self.config.max_quote_age_us:
            self.current["stale_quote_rejections"] += 1
            self.reject(observation, "stale_quote")
            return
        remaining = decimal_value(order["quantity_base"], "order quantity")
        filled = ZERO
        cash_limited = False
        execution_rejection = None
        levels = observation.asks if order["side"] == "buy" else observation.bids
        fee_rate = self.config.fee_bps / BPS
        slip_rate = self.config.slippage_bps / BPS
        for level_index, level in enumerate(levels, start=1):
            if remaining == ZERO:
                break
            raw_price = level.price * (1 + slip_rate if order["side"] == "buy" else 1 - slip_rate)
            execution_price = _round_steps(
                raw_price, self.config.price_tick,
                ROUND_CEILING if order["side"] == "buy" else ROUND_FLOOR,
            )
            if execution_price <= 0:
                execution_rejection = "nonpositive_adverse_execution_price"
                break
            available = _round_steps(level.quantity, self.config.quantity_step)
            if order["side"] == "buy":
                affordable = _round_steps(
                    self.cash / (execution_price * (1 + fee_rate)), self.config.quantity_step,
                )
                cap = _round_steps(self.config.max_position - self.position, self.config.quantity_step)
                wanted = min(remaining, available, cap)
                if affordable < wanted:
                    cash_limited = True
                quantity = min(wanted, affordable)
            else:
                quantity = min(remaining, available, self.position)
                quantity = _round_steps(quantity, self.config.quantity_step)
            if quantity <= ZERO:
                continue
            notional = quantity * execution_price
            fee = notional * fee_rate
            adverse_cost = quantity * abs(execution_price - level.price)
            if order["side"] == "buy":
                self.cash -= notional + fee
                self.position += quantity
                self.cost_basis += notional + fee
                self.current["_buy"] += quantity
            else:
                previous_position = self.position
                allocated_cost = self.cost_basis if quantity == previous_position else self.cost_basis * quantity / previous_position
                self.cash += notional - fee
                self.position -= quantity
                self.cost_basis -= allocated_cost
                self.realized += notional - fee - allocated_cost
                self.current["_sell"] += quantity
                if self.position == ZERO:
                    self.cost_basis = ZERO
                    self.current["roundtrip_trade_count"] += 1
            if self.cash < ZERO or not ZERO <= self.position <= self.config.max_position:
                raise RuntimeError("Spot accounting invariant violated: cash or position crossed a bound")
            self.current["_fees"] += fee
            self.current["_slippage"] += adverse_cost
            self.current["_turnover"] += notional
            self.current["fills"] += 1
            self.fills.append({
                "fill_id": f"fill-{len(self.fills)+1:08d}", "order_id": order["order_id"],
                "model_id": self.model_id, "source_order": observation.source_order,
                "receive_time_us": observation.receive_time_us,
                "provenance_key": observation.provenance_key,
                "session_date": observation.session_date, "segment_id": observation.segment_id,
                "side": order["side"], "book_level": level_index,
                "quantity_base": decimal_text(quantity),
                "observed_price_quote": decimal_text(level.price),
                "execution_price_quote": decimal_text(execution_price),
                "notional_quote": decimal_text(notional), "fee_quote": decimal_text(fee),
                "slippage_and_rounding_quote": decimal_text(adverse_cost),
                "cash_after_quote": decimal_text(self.cash),
                "position_after_base": decimal_text(self.position),
            })
            remaining -= quantity
            filled += quantity
        if cash_limited:
            self.current["cash_limited_orders"] += 1
        if filled:
            self.current["filled_orders"] += 1
        if remaining and filled:
            self.current["partial_ioc_orders"] += 1
        order.update(
            attempted_time_us=observation.receive_time_us,
            attempted_source_order=observation.source_order,
            filled_quantity_base=decimal_text(filled),
            cancelled_quantity_base=decimal_text(remaining),
            status="filled" if remaining == ZERO else ("partially_filled_cancelled" if filled else "rejected"),
            reason="complete" if remaining == ZERO else (
                execution_rejection or ("insufficient_cash" if cash_limited else "insufficient_displayed_depth")
            ),
        )
        self.pending = None


def simulate(
    states: pd.DataFrame | Iterable[pd.DataFrame],
    signals: Iterable[Mapping[str, Any]],
    config: SimulationConfig | Mapping[str, Any],
) -> dict[str, Any]:
    """Run deterministic long/flat spot simulation; return JSON-safe local detail.

    Phase order at every observation is boundary cancellation/reset, execution of
    eligible older orders, receipt of this event's signal, and best-bid marking.
    New signals cannot execute on their own observation even with zero latency.
    """
    if isinstance(config, Mapping):
        unknown = set(config) - {item.name for item in fields(SimulationConfig)}
        if unknown:
            raise ValueError(f"Unknown simulation configuration keys: {sorted(unknown)}")
        config = SimulationConfig(**config)
    if not isinstance(config, SimulationConfig):
        raise TypeError("config must be SimulationConfig or its field mapping")
    with localcontext() as context:
        context.prec = 64
        signal_map, model_id = _signals(signals, config)
        unused = set(signal_map)
        engine = _Engine(config, model_id)
        observations = 0
        try:
            for observation in iter_observations(
                states, price_tick=config.price_tick, quantity_step=config.quantity_step,
            ):
                if (observation.exchange, observation.symbol) != (config.exchange, config.symbol):
                    raise ValueError("Observed venue/instrument differs from the explicit spot configuration")
                if engine.current is None or engine.last is not None and engine.last.segment_key != observation.segment_key:
                    if engine.current is not None:
                        engine.finish("segment_boundary")
                    engine.begin(observation)
                assert engine.current is not None
                if engine.last is not None and engine.position > ZERO:
                    engine.current["exposure_time_us"] += observation.receive_time_us - engine.last.receive_time_us
                engine.current["observations"] += 1
                if engine.pending is not None:
                    engine.execute(observation)
                if observation.source_order in signal_map:
                    engine.receive(observation, signal_map[observation.source_order])
                    unused.remove(observation.source_order)
                engine.mark(observation)
                engine.last = observation
                observations += 1
        except InvalidOperation as error:
            raise ValueError("Decimal arithmetic precision was exceeded by the supplied accounting magnitudes") from error
        if unused:
            raise ValueError(f"Signals reference unmatched source_order values: {sorted(unused)}")
        engine.finish("end_of_replay")
        ledger_hash = _hash(engine.ledger)
        assumptions = {
            "accounting": "Spot quote-currency cash and base-quantity long/flat inventory only; no inverse, leverage, shorting, funding or borrowing.",
            "inference_delay": "Signals are available exactly at their matched source receipt timestamp; execution latency represents the declared action delay.",
            "event_phases": ["cancel at segment boundary/reset", "execute eligible older IOC", "receive current signal", "mark at current best bid"],
            "zero_latency": "A strictly later source event is always required; a tied receipt microsecond is eligible only when source_order is later.",
            "pending_policy": "Keep first pending order; record subsequent signals as ignored until its attempt or segment-end cancellation.",
            "execution": "One marketable IOC consumes each displayed side level at most once in the execution observation. Cancel unfilled remainder immediately; no passive/queue/fill-probability claims.",
            "historical_book": "Each later observed snapshot replaces displayed liquidity. Own orders do not alter the historical feed; no endogenous market-impact feedback is modeled.",
            "quote_age": "execution receive_time_us minus exchange event_time_us; reject negative clock skew and age above max_quote_age_us.",
            "rounding": "Target/fill quantities round down to quantity_step. Adverse buy prices round up and sell prices down to price_tick.",
            "fees": "Charge fee_bps on actual execution notional exactly in Decimal quote units. Venue-specific fee/minimum-charge rounding is not modeled.",
            "cash_limits": "Affordable buy quantities include fees and are rounded down; no negative cash or excess base exposure.",
            "segments": "Each declared source/date/segment is an independent case starting with initial_cash and zero inventory. No gap liquidity or continuous annual equity is fabricated.",
            "segment_end": "Cancel pending orders and mark unclosed inventory at the last observed best bid; no unobserved liquidation fill.",
            "gross_pnl": "Net marked PnL plus fees; adverse execution/slippage remains included. Zero-cost replay is a separate diagnostic.",
            "gap_detection": "Segment identifiers come from upstream normalization/window selection; absent disconnect events cannot be reconstructed here.",
            "zero_cost_diagnostic": config.fee_bps == ZERO and config.slippage_bps == ZERO,
            "redistribution": "Orders, fills, ledger, signal events and per-segment detail remain local. Export aggregate metrics/hashes only.",
        }
        result = {
            "schema_version": 1, "simulation_type": "spot_marketable_ioc_hypothetical",
            "model_id": model_id, "config": config.to_dict(),
            "market": {"exchange": config.exchange, "symbol": config.symbol,
                       "base_currency": config.base_currency, "quote_currency": config.quote_currency,
                       "market_type": "spot", "depth_quantity_unit": "base", "price_unit": "quote per base"},
            "observations": observations, "signals": len(signal_map),
            "orders": engine.orders, "fills": engine.fills, "ledger": engine.ledger,
            "signal_events": engine.signal_events, "segments": engine.segments,
            "aggregate": summarize_segments(engine.segments), "ledger_sha256": ledger_hash,
            "signals_sha256": _signal_hash(signal_map),
            "assumptions": assumptions,
        }
        result["simulation_sha256"] = _hash({
            "config": result["config"], "market": result["market"], "model_id": model_id,
            "ledger_sha256": ledger_hash, "signals_sha256": result["signals_sha256"],
            "orders": engine.orders, "fills": engine.fills,
            "signal_events": engine.signal_events,
        })
        return result
