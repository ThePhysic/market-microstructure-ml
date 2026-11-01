"""Strict receipt-order replay exposing an immutable current observation only."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from numbers import Integral
from typing import Any, Iterable, Iterator

import pandas as pd


class ReplayError(ValueError):
    """A replay input does not satisfy the declared observation contract."""


def decimal_value(value: Any, name: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ReplayError(f"{name} must be a finite decimal number")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise ReplayError(f"{name} must be a finite decimal number") from error
    if not result.is_finite():
        raise ReplayError(f"{name} must be finite")
    return result


def decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    result = format(value, "f")
    return result.rstrip("0").rstrip(".") if "." in result else result


def integer_value(value: Any, name: str, *, positive: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ReplayError(f"{name} must be an integer, not a boolean or floating value")
    result = int(value)
    if result < (1 if positive else 0):
        raise ReplayError(f"{name} must be {'positive' if positive else 'nonnegative'}")
    return result


def on_grid(value: Decimal, step: Decimal) -> bool:
    """Exact rational grid test; never use binary-float remainder tolerances."""
    numerator, denominator = value.as_integer_ratio()
    step_numerator, step_denominator = step.as_integer_ratio()
    return (numerator * step_denominator) % (denominator * step_numerator) == 0


@dataclass(frozen=True)
class BookLevel:
    price: Decimal
    quantity: Decimal


@dataclass(frozen=True)
class DecisionView:
    """No reference to a DataFrame, replay cursor, future row, or mutable book."""

    exchange: str
    symbol: str
    session_date: str
    segment_id: str
    source_file: str
    source_row_position: int
    provenance_key: str
    event_time_us: int
    receive_time_us: int
    source_order: int
    bids: tuple[BookLevel, ...]
    asks: tuple[BookLevel, ...]

    @property
    def segment_key(self) -> tuple[str, str, str]:
        return self.session_date, self.segment_id, self.source_file


Observation = DecisionView

_META = [
    "exchange", "symbol", "session_date", "segment_id", "source_file",
    "source_row_position", "provenance_key", "event_time_us", "receive_time_us", "source_order",
]
_BOOK = [
    f"{side}_{kind}_{level}"
    for side in ("bid", "ask") for kind in ("price", "size") for level in range(1, 6)
]


def iter_observations(
    states: pd.DataFrame | Iterable[pd.DataFrame],
    *,
    price_tick: Any | None = None,
    quantity_step: Any | None = None,
) -> Iterator[DecisionView]:
    """Validate and yield observations without sorting or crossing batch rules.

    Empty batches are allowed, an empty complete replay is not. Exchange-clock
    skew is preserved for the execution layer's explicit quote-age rejection.
    Duplicate provenance, receipt regressions, and reused disjoint segments fail.
    """
    tick = decimal_value(price_tick, "price_tick") if price_tick is not None else None
    lot = decimal_value(quantity_step, "quantity_step") if quantity_step is not None else None
    if (tick is not None and tick <= 0) or (lot is not None and lot <= 0):
        raise ReplayError("price_tick and quantity_step must be positive")
    batches = (states,) if isinstance(states, pd.DataFrame) else states
    if isinstance(batches, (str, bytes, dict)) or batches is None:
        raise ReplayError("Replay expects a DataFrame or iterable of DataFrame batches")
    seen_provenance: set[str] = set()
    seen_segments: set[tuple[str, str, str]] = set()
    previous_segment: tuple[str, str, str] | None = None
    previous_order = 0
    previous_receive = -1
    market: tuple[str, str] | None = None
    count = 0
    for batch in batches:
        if not isinstance(batch, pd.DataFrame):
            raise ReplayError("Each replay batch must be a pandas DataFrame")
        if batch.columns.duplicated().any():
            raise ReplayError("Duplicate replay column names are ambiguous")
        missing = sorted(set(_META + _BOOK) - set(batch.columns))
        if missing:
            raise ReplayError(f"Missing replay columns: {', '.join(missing)}")
        names = list(batch.columns)
        for values in batch.itertuples(index=False, name=None):
            row = dict(zip(names, values, strict=True))
            for key in ("exchange", "symbol", "session_date", "segment_id", "source_file", "provenance_key"):
                if not isinstance(row[key], str) or not row[key].strip():
                    raise ReplayError(f"{key} must be a nonempty string")
            order = integer_value(row["source_order"], "source_order", positive=True)
            received = integer_value(row["receive_time_us"], "receive_time_us")
            event_time = integer_value(row["event_time_us"], "event_time_us")
            source_position = integer_value(row["source_row_position"], "source_row_position", positive=True)
            if order <= previous_order or received < previous_receive:
                raise ReplayError("Replay must preserve increasing source_order and nondecreasing receipt timestamps")
            if row["provenance_key"] in seen_provenance:
                raise ReplayError("Duplicate replay provenance_key")
            try:
                day = date.fromisoformat(row["session_date"])
            except ValueError as error:
                raise ReplayError("session_date must be canonical YYYY-MM-DD") from error
            if day.isoformat() != row["session_date"]:
                raise ReplayError("session_date must be canonical YYYY-MM-DD")
            if received // 86_400_000_000 != (day - date(1970, 1, 1)).days:
                raise ReplayError("session_date disagrees with the UTC receipt timestamp")
            observed_market = row["exchange"], row["symbol"]
            if market is not None and observed_market != market:
                raise ReplayError("A replay must contain exactly one venue and instrument")
            market = observed_market
            sides = {}
            for side in ("bid", "ask"):
                levels = []
                for level in range(1, 6):
                    price = decimal_value(row[f"{side}_price_{level}"], f"{side}_price_{level}")
                    quantity = decimal_value(row[f"{side}_size_{level}"], f"{side}_size_{level}")
                    if price <= 0 or quantity < 0:
                        raise ReplayError("Prices must be positive and displayed quantities nonnegative")
                    if tick is not None and not on_grid(price, tick):
                        raise ReplayError(f"{side} price is not on the declared price_tick grid")
                    if lot is not None and not on_grid(quantity, lot):
                        raise ReplayError(f"{side} quantity is not on the declared quantity_step grid")
                    levels.append(BookLevel(price, quantity))
                prices = [item.price for item in levels]
                if side == "bid" and any(a <= b for a, b in zip(prices, prices[1:])):
                    raise ReplayError("Bid levels must be strictly descending")
                if side == "ask" and any(a >= b for a, b in zip(prices, prices[1:])):
                    raise ReplayError("Ask levels must be strictly ascending")
                sides[side] = tuple(levels)
            if sides["bid"][0].price >= sides["ask"][0].price:
                raise ReplayError("Crossed or locked books cannot be replayed")
            observation = DecisionView(
                exchange=row["exchange"], symbol=row["symbol"],
                session_date=row["session_date"], segment_id=row["segment_id"],
                source_file=row["source_file"], source_row_position=source_position,
                provenance_key=row["provenance_key"], event_time_us=event_time,
                receive_time_us=received, source_order=order,
                bids=sides["bid"], asks=sides["ask"],
            )
            key = observation.segment_key
            if key != previous_segment:
                if key in seen_segments:
                    raise ReplayError("A source segment cannot reappear after another segment")
                seen_segments.add(key)
                previous_segment = key
            seen_provenance.add(observation.provenance_key)
            previous_order, previous_receive = order, received
            count += 1
            yield observation
    if not count:
        raise ReplayError("A complete replay must contain at least one observation")
