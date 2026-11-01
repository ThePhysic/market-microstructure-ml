"""Streaming, auditable normalization of Tardis top-five order-book CSV rows."""
from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .acquisition import HEADER_FIELDS, sha256_file


class DataIntegrityError(ValueError):
    """A source file or manifest cannot be safely interpreted."""


PRICE_COLUMNS = [f"{side}_price_{level}" for level in range(1, 6) for side in ("bid", "ask")]
SIZE_COLUMNS = [f"{side}_size_{level}" for level in range(1, 6) for side in ("bid", "ask")]
NORMALIZED_COLUMNS = [
    "exchange", "symbol", "session_date", "segment_id", "source_file",
    "source_row_position", "provenance_key", "event_time_us", "receive_time_us", "source_order",
] + [name for level in range(1, 6) for name in (
    f"bid_price_{level}", f"ask_price_{level}", f"bid_size_{level}", f"ask_size_{level}"
)]
MIN_TIME_US = 946_684_800_000_000
MAX_TIME_US = 4_102_444_800_000_000


def _timestamp(value: str | None) -> int:
    if not isinstance(value, str) or not value.isdecimal():
        raise ValueError("invalid_timestamp")
    parsed = int(value)
    if not MIN_TIME_US <= parsed < MAX_TIME_US:
        raise ValueError("timestamp_unit_or_range")
    return parsed


def _date_from_us(value: int) -> str:
    return datetime.fromtimestamp(value / 1_000_000, tz=timezone.utc).date().isoformat()


def _date_hint(path: Path, manifest: dict[str, Any] | None) -> str | None:
    if manifest and isinstance(manifest.get("date"), str):
        return manifest["date"]
    match = re.search(r"(?<!\d)(\d{4}-\d{2}-\d{2})(?!\d)", path.name)
    return match.group(1) if match else None


def _manifest_mapping(manifests: Any, paths: list[Path]) -> dict[str, dict[str, Any]]:
    if manifests is None:
        result = {}
        for path in paths:
            companion = path.with_suffix(".manifest.json")
            if companion.exists():
                result[str(path.resolve())] = json.loads(companion.read_text(encoding="utf-8"))
        return result
    if isinstance(manifests, dict):
        values = list(manifests.values()) if "sha256" not in manifests else [manifests]
    else:
        values = list(manifests)
    result = {}
    for path in paths:
        matches = [value for value in values if isinstance(value, dict) and Path(value.get("path", "")).name == path.name]
        if len(matches) != 1:
            raise DataIntegrityError(f"Expected one unambiguous manifest for {path.name}")
        result[str(path.resolve())] = matches[0]
    return result


def ingest_files(
    paths: Iterable[str | Path], *, exchange: str = "deribit",
    symbol: str = "BTC-PERPETUAL", gap_seconds: float = 30, manifests: Any = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return valid normalized states and attributable source-row exclusions.

    Invalid rows reset the following segment. Receive-time regressions are
    excluded against a valid-state high-water mark. Exact duplicate source rows
    are excluded; repeated books with different timestamps are counted/retained.
    """
    if not isinstance(gap_seconds, (int, float)) or not math.isfinite(gap_seconds) or gap_seconds <= 0:
        raise DataIntegrityError("gap_seconds must be finite and positive")
    source_paths = [Path(path) for path in paths]
    if not source_paths:
        raise DataIntegrityError("At least one CSV source file is required")
    if len({str(path.resolve()) for path in source_paths}) != len(source_paths):
        raise DataIntegrityError("The same source path was provided more than once")
    manifest_map = _manifest_mapping(manifests, source_paths)
    source_paths.sort(key=lambda path: (_date_hint(path, manifest_map.get(str(path.resolve()))) or "", path.name))
    global_counts: Counter[str] = Counter()
    exclusion_counts: Counter[str] = Counter()
    exclusions: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    file_reports = []
    source_order = 0
    last_global_receive: int | None = None
    for file_index, path in enumerate(source_paths):
        if not path.is_file():
            raise DataIntegrityError(f"Source file does not exist: {path}")
        file_hash = sha256_file(path)
        manifest = manifest_map.get(str(path.resolve()))
        if manifest is not None:
            expected_hash = manifest.get("excerpt_sha256", manifest.get("sha256"))
            if not isinstance(expected_hash, str) or expected_hash != file_hash:
                raise DataIntegrityError(f"SHA-256 mismatch for {path.name}")
            if manifest.get("exchange", exchange) != exchange or manifest.get("symbol", symbol) != symbol:
                raise DataIntegrityError(f"Manifest market mismatch for {path.name}")
        expected_date = _date_hint(path, manifest)
        counts: Counter[str] = Counter()
        seen_rows: set[tuple[Any, ...]] = set()
        last_book: tuple[float, ...] | None = None
        high_water: int | None = None
        previous_file_receive = last_global_receive
        last_parsed_receive: int | None = None
        last_event: int | None = None
        segment_number = 0
        break_next = False
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, strict=True)
            if reader.fieldnames != HEADER_FIELDS:
                raise DataIntegrityError(f"Unexpected CSV schema in {path.name}; expected pinned top-five columns")
            try:
                for row_position, row in enumerate(reader, start=1):
                    source_order += 1
                    counts["total_rows"] += 1
                    reasons: list[str] = []
                    if None in row or any(value is None for value in row.values()):
                        reasons.append("malformed_row")
                    row_tuple = tuple(row.get(name) for name in HEADER_FIELDS)
                    if row_tuple in seen_rows:
                        reasons.append("duplicate_row")
                        counts["duplicate_rows"] += 1
                    seen_rows.add(row_tuple)
                    if row.get("exchange") != exchange or row.get("symbol") != symbol:
                        reasons.append("market_mismatch")
                    event_time = receive_time = None
                    try:
                        event_time = _timestamp(row.get("timestamp"))
                        receive_time = _timestamp(row.get("local_timestamp"))
                    except ValueError as exc:
                        reasons.append(str(exc))
                    if receive_time is not None:
                        if last_parsed_receive is not None:
                            if receive_time == last_parsed_receive:
                                counts["tied_receive_timestamps"] += 1
                            elif receive_time < last_parsed_receive:
                                counts["receive_timestamp_decreases"] += 1
                        last_parsed_receive = receive_time
                        if high_water is not None and receive_time < high_water:
                            reasons.append("receive_time_before_high_watermark")
                        if previous_file_receive is not None and receive_time < previous_file_receive:
                            reasons.append("receive_time_before_previous_file")
                        actual_date = _date_from_us(receive_time)
                        if expected_date is None:
                            expected_date = actual_date
                        if actual_date != expected_date:
                            reasons.append("session_date_mismatch")
                    if event_time is not None:
                        if last_event is not None and event_time < last_event:
                            counts["event_timestamp_decreases"] += 1
                        last_event = event_time
                    normalized: dict[str, Any] = {}
                    for level in range(5):
                        for raw_side, side in (("bids", "bid"), ("asks", "ask")):
                            for raw_field, field in (("price", "price"), ("amount", "size")):
                                value = row.get(f"{raw_side}[{level}].{raw_field}")
                                if value in (None, ""):
                                    reasons.append("depth_insufficiency_or_missing_value")
                                    continue
                                try:
                                    number = float(value)
                                except (ValueError, TypeError):
                                    reasons.append("unparsable_book_value")
                                    continue
                                if not math.isfinite(number):
                                    reasons.append("nonfinite_book_value")
                                elif field == "price" and number <= 0:
                                    reasons.append("nonpositive_price")
                                elif field == "size" and number < 0:
                                    reasons.append("negative_amount")
                                else:
                                    normalized[f"{side}_{field}_{level + 1}"] = number
                                    if field == "size" and number == 0:
                                        counts["zero_amount_cells"] += 1
                    if len(normalized) == 20:
                        bids = [normalized[f"bid_price_{level}"] for level in range(1, 6)]
                        asks = [normalized[f"ask_price_{level}"] for level in range(1, 6)]
                        if bids[0] >= asks[0]:
                            reasons.append("crossed_or_locked_book")
                        if any(bids[i] <= bids[i + 1] for i in range(4)) or any(asks[i] >= asks[i + 1] for i in range(4)):
                            reasons.append("unsorted_or_duplicate_price_levels")
                    if reasons:
                        reasons = sorted(set(reasons))
                        counts["excluded_rows"] += 1
                        exclusion_counts.update(reasons)
                        exclusions.append({
                            "source_file": path.name, "source_row_position": row_position,
                            "source_order": source_order, "reasons": reasons,
                        })
                        break_next = True
                        continue
                    assert receive_time is not None and event_time is not None and expected_date is not None
                    gap = high_water is not None and receive_time - high_water > gap_seconds * 1_000_000
                    if gap:
                        counts["gaps"] += 1
                    if break_next or gap:
                        segment_number += 1
                    break_next = False
                    book_tuple = tuple(normalized[name] for name in NORMALIZED_COLUMNS[10:])
                    if last_book == book_tuple:
                        counts["repeated_book_payloads"] += 1
                    last_book = book_tuple
                    high_water = receive_time
                    last_global_receive = receive_time
                    records.append({
                        "exchange": exchange, "symbol": symbol, "session_date": expected_date,
                        "segment_id": f"{expected_date}:{file_index:03d}:{segment_number:05d}",
                        "source_file": path.name, "source_row_position": row_position,
                        "provenance_key": f"{file_hash}:{row_position}",
                        "event_time_us": event_time, "receive_time_us": receive_time,
                        "source_order": source_order, **normalized,
                    })
                    counts["retained_rows"] += 1
            except csv.Error as exc:
                raise DataIntegrityError(f"Malformed CSV at physical line {reader.line_num} in {path.name}") from exc
        global_counts.update(counts)
        file_reports.append({
            "source_file": path.name, "sha256": file_hash, "session_date": expected_date,
            "counts": dict(counts), "manifest_verified": manifest is not None,
        })
    frame = pd.DataFrame.from_records(records, columns=NORMALIZED_COLUMNS)
    for column in ("source_row_position", "event_time_us", "receive_time_us", "source_order"):
        frame[column] = frame[column].astype(np.int64)
    for column in PRICE_COLUMNS + SIZE_COLUMNS:
        frame[column] = frame[column].astype(np.float64)
    quality: dict[str, Any] = {
        "schema_version": 1, "total_rows": global_counts["total_rows"],
        "retained_rows": global_counts["retained_rows"], "excluded_rows": global_counts["excluded_rows"],
        "counts": dict(global_counts), "exclusion_counts": dict(exclusion_counts),
        "exclusions": exclusions, "per_file": file_reports,
        "segments": int(frame["segment_id"].nunique()),
        "sessions": sorted(frame["session_date"].unique().tolist()),
        "timestamp_unit": "microseconds since Unix epoch UTC",
        "availability_policy": "local receipt timestamp; original source position breaks ties",
        "gap_seconds": gap_seconds,
        "warnings": [
            "Vendor-reconstructed snapshots may already have crossed levels removed upstream.",
            "CSV lacks disconnect markers; gap segmentation is a heuristic, not proof of a complete feed.",
            "Zero amounts are retained with counts; imbalance features need a zero-denominator policy.",
        ],
    }
    assert quality["total_rows"] == quality["retained_rows"] + quality["excluded_rows"]
    return frame, quality
