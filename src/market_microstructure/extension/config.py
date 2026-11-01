"""Strict JSON experiment configuration and immutable research identity."""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal, InvalidOperation
import json
import math
from pathlib import Path
from typing import Any

from ..manifests import digest

TOP_KEYS = {"schema_version", "name", "market", "data", "research", "simulation", "scenarios", "publication"}
RESEARCH_KEYS = {
    "schema_version", "stage", "dates", "initial_train_dates", "development_dates",
    "final_dates", "exchange", "symbol", "horizon_events", "threshold_ticks",
    "tick_size", "trailing_window", "seed", "practical_delta", "confidence",
    "block_length_dates", "precision_half_width", "min_final_blocks", "n_resamples",
    "protocol_sha256", "frozen_source_revision", "final_scoring_authorized",
    "precision_gate_status", "target_position", "max_holding_events", "inference_delay_us",
}
RUNTIME_RESEARCH_KEYS = {"stage", "protocol_sha256", "frozen_source_revision", "final_scoring_authorized", "precision_gate_status"}


def _keys(value: Any, expected: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"{label} must contain exactly the declared keys: {sorted(expected)}")


def _integer(value: Any, label: str, minimum: int, maximum: int) -> None:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{label} must be an integer in [{minimum}, {maximum}]")


def _number(value: Any, label: str, minimum: float, maximum: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(f"{label} must be finite and in [{minimum}, {maximum}]")


def _decimal(value: Any, label: str, positive: bool = True) -> Decimal:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a decimal string")
    try:
        parsed = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f"Invalid {label}") from error
    if not parsed.is_finite() or parsed < 0 or (positive and parsed == 0):
        raise ValueError(f"{label} must be finite and {'positive' if positive else 'nonnegative'}")
    return parsed


def validate_config(value: Any) -> dict[str, Any]:
    _keys(value, TOP_KEYS, "configuration")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("Unsupported configuration schema_version")
    if not isinstance(value["name"], str) or not value["name"].strip():
        raise ValueError("name must be a nonempty string")
    market = value["market"]
    _keys(market, {"exchange", "symbol", "instrument_type", "base_currency", "quote_currency", "price_tick", "quantity_step"}, "market")
    if (market["exchange"], market["symbol"], market["instrument_type"], market["base_currency"], market["quote_currency"]) != ("bitstamp", "BTCUSD", "spot", "BTC", "USD"):
        raise ValueError("The reviewed extension supports Bitstamp BTCUSD spot only")
    _decimal(market["price_tick"], "price_tick")
    _decimal(market["quantity_step"], "quantity_step")
    if Decimal(market["price_tick"]) != Decimal("0.01") or Decimal(market["quantity_step"]) != Decimal("0.00000001"):
        raise ValueError("The reviewed spot data require the declared cent/base-quantity grids")
    data = value["data"]
    _keys(data, {"dates", "windows_seconds", "window_seconds", "gap_seconds", "max_total_compressed_bytes", "max_disk_bytes", "max_wall_seconds", "max_compressed_bytes_per_date", "max_decompressed_bytes_per_date", "minimum_window_states", "minimum_window_span_seconds", "maximum_window_edge_gap_seconds", "maximum_excluded_fraction"}, "data")
    dates = data["dates"]
    if not isinstance(dates, list) or not 4 <= len(dates) <= 64 or dates != sorted(set(dates)):
        raise ValueError("dates must be 4-64 sorted distinct ISO dates")
    for item in dates:
        parsed = date.fromisoformat(item)
        if parsed.isoformat() != item or parsed.day != 1:
            raise ValueError("Only canonical free first-of-month dates are supported")
    _integer(data["window_seconds"], "window_seconds", 60, 3600)
    windows = data["windows_seconds"]
    if not isinstance(windows, list) or not windows or any(type(x) is not int for x in windows) or windows != sorted(set(windows)):
        raise ValueError("windows must be sorted distinct integer UTC seconds")
    if windows[0] < 0 or windows[-1] + data["window_seconds"] > 86400 or any(b < a + data["window_seconds"] for a, b in zip(windows, windows[1:])):
        raise ValueError("Windows overlap or escape their UTC date")
    _number(data["gap_seconds"], "gap_seconds", 0.001, 3600)
    _integer(data["minimum_window_states"], "minimum_window_states", 1, 1000000)
    _integer(data["minimum_window_span_seconds"], "minimum_window_span_seconds", 1, data["window_seconds"])
    _integer(data["maximum_window_edge_gap_seconds"], "maximum_window_edge_gap_seconds", 0, data["window_seconds"])
    _number(data["maximum_excluded_fraction"], "maximum_excluded_fraction", 0, .1)
    for key, maximum in {"max_total_compressed_bytes": 1024**3, "max_disk_bytes": 5*1024**3, "max_wall_seconds": 1200, "max_compressed_bytes_per_date": 16*1024**2, "max_decompressed_bytes_per_date": 160*1024**2}.items():
        _integer(data[key], key, 1, maximum)
    research = value["research"]
    _keys(research, RESEARCH_KEYS, "research")
    if research["schema_version"] != 1 or type(research["schema_version"]) is not int:
        raise ValueError("Unsupported research schema")
    if research["dates"] != dates or (research["exchange"], research["symbol"]) != (market["exchange"], market["symbol"]):
        raise ValueError("Research and acquisition markets/dates differ")
    _integer(research["initial_train_dates"], "initial_train_dates", 2, len(dates)-2)
    n = research["initial_train_dates"]
    if not isinstance(research["development_dates"], list) or not isinstance(research["final_dates"], list) or not research["development_dates"] or not research["final_dates"] or dates[n:] != research["development_dates"] + research["final_dates"]:
        raise ValueError("Initial, development and final dates must partition the chronological data")
    for key, low, high in (("horizon_events", 1, 1000), ("trailing_window", 1, 1000), ("seed", 0, 2**32-1), ("block_length_dates", 1, len(dates)), ("n_resamples", 100, 10000), ("min_final_blocks", 2, 32), ("max_holding_events", 1, 1000), ("inference_delay_us", 0, 0)):
        _integer(research[key], key, low, high)
    for key, low, high in (("threshold_ticks", 0, 1000), ("tick_size", 1e-12, 100), ("practical_delta", 1e-6, 1), ("confidence", .5, .999), ("precision_half_width", 1e-6, 1)):
        _number(research[key], key, low, high)
    if Decimal(str(research["tick_size"])) != Decimal(market["price_tick"]):
        raise ValueError("Research tick_size must equal the accounting price_tick")
    if research["stage"] not in {"pilot", "final"} or type(research["final_scoring_authorized"]) is not bool:
        raise ValueError("Invalid research execution authorization")
    _decimal(research["target_position"], "target_position")
    simulation = value["simulation"]
    _keys(simulation, {"initial_cash", "max_position", "quantity_step", "price_tick", "fee_bps", "slippage_bps", "latency_us", "max_quote_age_us"}, "simulation")
    for key in ("initial_cash", "max_position", "quantity_step", "price_tick"):
        _decimal(simulation[key], key)
    for key in ("fee_bps", "slippage_bps"):
        _decimal(simulation[key], key, False)
    for key in ("latency_us", "max_quote_age_us"):
        _integer(simulation[key], key, 0, 86400*1000000)
    if simulation["quantity_step"] != market["quantity_step"] or simulation["price_tick"] != market["price_tick"] or Decimal(research["target_position"]) > Decimal(simulation["max_position"]):
        raise ValueError("Simulation grids/exposure disagree with the research contract")
    if len(research["final_dates"]) // research["block_length_dates"] < research["min_final_blocks"]:
        raise ValueError("Final dates must cover the declared minimum block count")
    if research["practical_delta"] >= 1:
        raise ValueError("practical_delta must be below one")
    from .simulation import SimulationConfig
    # Validate executable assumptions before any data loading, registry mutation
    # or fitting. An invalid scenario must never consume reserved outcomes.
    SimulationConfig(**simulation)
    if not isinstance(value["scenarios"], list) or not value["scenarios"]:
        raise ValueError("At least one execution scenario is required")
    names = []
    for scenario in value["scenarios"]:
        _keys(scenario, {"name", "fee_bps", "slippage_bps", "latency_us"}, "scenario")
        if not isinstance(scenario["name"], str) or not scenario["name"].isidentifier():
            raise ValueError("Scenario name must be an identifier")
        names.append(scenario["name"])
        _decimal(scenario["fee_bps"], "fee_bps", False)
        _decimal(scenario["slippage_bps"], "slippage_bps", False)
        _integer(scenario["latency_us"], "latency_us", 0, 86400*1000000)
        SimulationConfig(**{**simulation, **{key: scenario[key] for key in ("fee_bps", "slippage_bps", "latency_us")}})
    if len(names) != len(set(names)):
        raise ValueError("Duplicate scenario names")
    expected_publication = {"historical_rows": False, "signals": False, "trade_ledgers": False, "fitted_models": False, "aggregate_results": True}
    if value["publication"] != expected_publication or any(type(x) is not bool for x in value["publication"].values()):
        raise ValueError("Restricted historical assets must remain local")
    return deepcopy(value)


def load_config(path: str | Path) -> dict[str, Any]:
    return validate_config(json.loads(Path(path).read_text(encoding="utf-8")))


def protocol_identity(config: dict[str, Any]) -> str:
    """Execution authorization is recorded separately from scientific choices."""
    scientific = deepcopy(config)
    scientific["research"] = {key: val for key, val in config["research"].items() if key not in RUNTIME_RESEARCH_KEYS}
    return digest(scientific)
