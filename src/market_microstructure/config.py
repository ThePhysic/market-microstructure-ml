"""Validated, immutable research choices, independent of observed scores."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import json
import math
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ResearchConfig:
    schema_version: int = 1
    exchange: str = "deribit"
    symbol: str = "BTC-PERPETUAL"
    data_type: str = "book_snapshot_5"
    dates: tuple[str, ...] = ()
    horizon_events: int = 10
    threshold_ticks: float = 1.0
    tick_size: float = 0.5
    trailing_window: int = 20
    gap_seconds: float = 30.0
    min_train_dates: int = 3
    holdout_dates: int = 2
    seed: int = 42
    rows_per_date: int = 20_000
    max_compressed_bytes_per_date: int = 524_288
    max_total_transfer_bytes: int = 25_165_824
    robustness: tuple[tuple[str, Any], ...] = (
        ("feature_ablation", "remove_imbalance"),
        ("alternate_horizon_events", 20),
        ("development_only", True),
    )

    def __post_init__(self) -> None:
        integer_fields = (
            "schema_version", "horizon_events", "trailing_window", "min_train_dates",
            "holdout_dates", "seed", "rows_per_date", "max_compressed_bytes_per_date",
            "max_total_transfer_bytes",
        )
        for name in integer_fields:
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")
            if value < (0 if name == "seed" else 1):
                raise ValueError(f"{name} is out of range")
        if self.schema_version != 1:
            raise ValueError("Unsupported config schema_version")
        if self.seed >= 2**32:
            raise ValueError("seed must be smaller than 2**32")
        for name in ("threshold_ticks", "tick_size", "gap_seconds"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be a finite number")
            if not math.isfinite(value) or value < (0 if name == "threshold_ticks" else 1e-12):
                raise ValueError(f"{name} is out of range")
        if not math.isfinite(self.threshold_ticks * self.tick_size):
            raise ValueError("The target threshold must remain finite in price units")
        if self.exchange != "deribit" or self.symbol != "BTC-PERPETUAL":
            raise ValueError("This research contract supports only deribit BTC-PERPETUAL")
        if self.data_type != "book_snapshot_5":
            raise ValueError("This research contract requires top-five snapshots")
        if not isinstance(self.dates, tuple) or not all(isinstance(value, str) for value in self.dates):
            raise ValueError("dates must be immutable canonical date strings")
        if not self.dates or tuple(sorted(set(self.dates))) != self.dates:
            raise ValueError("dates must be nonempty, unique, and chronologically sorted")
        if len(self.dates) > 12:
            raise ValueError("At most twelve sample dates are authorized")
        for value in self.dates:
            parsed = date.fromisoformat(value)
            if parsed.isoformat() != value or parsed.day != 1:
                raise ValueError("Only canonical first-of-month free sample dates are supported")
        if len(self.dates) < self.min_train_dates + self.holdout_dates + 1:
            raise ValueError("Not enough independent dates for development and final holdout")
        if self.rows_per_date > 20_000 or self.rows_per_date <= self.trailing_window + max(self.horizon_events, 20):
            raise ValueError("rows_per_date must exceed history+horizon and be at most 20000")
        if self.max_compressed_bytes_per_date > 2 * 1024**2:
            raise ValueError("Per-date compressed download cap exceeds the authorized 2 MiB ceiling")
        if self.max_total_transfer_bytes > 24 * 1024**2:
            raise ValueError("Total transfer cap exceeds the authorized 24 MiB ceiling")
        if self.max_total_transfer_bytes < len(self.dates) * self.max_compressed_bytes_per_date:
            raise ValueError("Total transfer cap cannot cover the configured per-date maxima")
        if not isinstance(self.robustness, tuple) or any(
            not isinstance(pair, tuple) or len(pair) != 2 or not isinstance(pair[0], str)
            for pair in self.robustness
        ):
            raise ValueError("robustness settings must be immutable pairs")
        choices = dict(self.robustness)
        if (
            len(self.robustness) != 3
            or type(choices.get("alternate_horizon_events")) is not int
            or choices.get("development_only") is not True
        ):
            raise ValueError("Robustness fields must use the exact declared types")
        if choices != {
            "feature_ablation": "remove_imbalance",
            "alternate_horizon_events": 20,
            "development_only": True,
        }:
            raise ValueError("Only the two predeclared development-only robustness checks are supported")

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["dates"] = list(self.dates)
        result["robustness"] = dict(self.robustness)
        return result


def config_from_dict(document: dict[str, Any]) -> ResearchConfig:
    document = dict(document) if isinstance(document, dict) else document
    if not isinstance(document, dict):
        raise ValueError("Config must be a JSON object")
    allowed = set(ResearchConfig.__dataclass_fields__)
    unknown = set(document) - allowed
    if unknown:
        raise ValueError(f"Unknown configuration fields: {sorted(unknown)}")
    if not isinstance(document.get("dates"), list):
        raise ValueError("Config dates must be an explicit list")
    document["dates"] = tuple(document["dates"])
    if "robustness" in document:
        if not isinstance(document["robustness"], dict):
            raise ValueError("robustness must be an object")
        document["robustness"] = tuple(document["robustness"].items())
    return ResearchConfig(**document)


def load_config(path: str | Path) -> ResearchConfig:
    with Path(path).open(encoding="utf-8") as stream:
        return config_from_dict(json.load(stream))
