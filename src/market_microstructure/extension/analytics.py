"""Descriptive independent-segment accounting; no synthetic annual equity."""

from __future__ import annotations

from decimal import Decimal, localcontext
from typing import Any

from .replay import decimal_text, decimal_value


def summarize_segments(segments: list[dict[str, Any]]) -> dict[str, Any]:
    if not segments:
        raise ValueError("At least one completed segment is required")
    with localcontext() as context:
        context.prec = 64
        returns = [decimal_value(item["net_return"], "net_return") for item in segments]
        ordered = sorted(returns)
        middle = len(ordered) // 2
        median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
        amounts = {
            key: sum((decimal_value(segment[key], key) for segment in segments), Decimal(0))
            for key in (
                "net_pnl_quote", "gross_pnl_quote", "realized_pnl_quote", "unrealized_pnl_quote",
                "fees_quote", "slippage_and_rounding_quote", "turnover_quote",
                "buy_quantity_base", "sell_quantity_base", "unresolved_inventory_base",
                "unresolved_inventory_mark_quote",
            )
        }
        counters = {
            key: sum(int(segment[key]) for segment in segments)
            for key in (
                "submitted_orders", "filled_orders", "fills", "partial_ioc_orders",
                "stale_quote_rejections", "clock_skew_rejections", "cash_limited_orders",
                "ignored_pending_signals", "terminal_cancelled_orders", "exposure_time_us",
                "observed_duration_us", "roundtrip_trade_count",
            )
        }
        net_pnl = amounts.pop("net_pnl_quote")
        max_drawdown = max(decimal_value(item["max_drawdown_quote"], "drawdown") for item in segments)
        open_segments = sum(decimal_value(item["unresolved_inventory_base"], "inventory") > 0 for item in segments)
        return {
            "segment_count": len(segments),
            "sum_independent_segment_pnl_quote": decimal_text(net_pnl),
            "net_pnl_quote": decimal_text(net_pnl),
            **{key: decimal_text(value) for key, value in amounts.items()},
            **counters,
            "open_segments": open_segments,
            "unresolved_position_segments": open_segments,
            "fill_count": counters["fills"],
            "mean_segment_return": decimal_text(sum(returns, Decimal(0)) / len(returns)),
            "median_segment_return": decimal_text(median),
            "min_segment_return": decimal_text(min(returns)),
            "max_segment_return": decimal_text(max(returns)),
            "max_segment_drawdown_quote": decimal_text(max_drawdown),
            "max_drawdown_quote": decimal_text(max_drawdown),
            "max_segment_drawdown_fraction": decimal_text(max(decimal_value(item["max_drawdown_fraction"], "drawdown") for item in segments)),
            "capital_convention": "Each observed segment independently starts with initial_cash and zero inventory. PnL is summed across independent cases, not a continuous investable equity curve.",
            "annualization": "Not computed. No annualized Sharpe, compounded annual return or fabricated gap equity.",
            "inventory_convention": "Unclosed spot inventory is marked at the final observed best bid, not liquidated through a gap.",
        }
