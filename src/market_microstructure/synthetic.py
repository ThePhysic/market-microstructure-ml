"""Small deterministic offline fixtures, explicitly unrelated to market evidence."""

from __future__ import annotations

import calendar
from collections.abc import Sequence
import csv
from datetime import date as Date, datetime, time, timezone
import hashlib
import io
import json
from pathlib import Path
import random
from typing import Any


PROVIDER = "project-generated synthetic fixture"
HEADER_FIELDS = ["exchange", "symbol", "timestamp", "local_timestamp"] + [
    f"{side}[{level}].{field}"
    for level in range(5)
    for side in ("asks", "bids")
    for field in ("price", "amount")
]


def _validated_arguments(
    dates: Sequence[str], rows_per_date: int, seed: int
) -> list[str]:
    if isinstance(dates, (str, bytes)) or not isinstance(dates, Sequence):
        raise ValueError("dates must be a sequence of canonical YYYY-MM-DD strings")
    if not 1 <= len(dates) <= 12 or len(set(dates)) != len(dates):
        raise ValueError("Choose between one and twelve distinct fixture dates")
    normalized = []
    for value in dates:
        try:
            parsed = Date.fromisoformat(value) if isinstance(value, str) else None
        except ValueError:
            parsed = None
        if parsed is None or parsed.isoformat() != value:
            raise ValueError("Fixture dates must be canonical YYYY-MM-DD strings")
        if not Date(2000, 1, 1) <= parsed < Date(2100, 1, 1):
            raise ValueError("Fixture dates must lie within 2000–2099 UTC")
        normalized.append(value)
    if type(rows_per_date) is not int or not 1 <= rows_per_date <= 20_000:
        raise ValueError("rows_per_date must be an integer between 1 and 20,000")
    if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed must be an integer between 0 and 2**32 - 1")
    return sorted(normalized)


def _stream(seed: int, date: str, purpose: str) -> random.Random:
    digest = hashlib.sha256(f"synthetic-v1:{seed}:{date}:{purpose}".encode("ascii")).digest()
    return random.Random(int.from_bytes(digest, "big"))


def _csv_payload(date: str, rows_per_date: int, seed: int) -> bytes:
    prices = _stream(seed, date, "price")
    sizes = _stream(seed, date, "size")
    day = Date.fromisoformat(date)
    midday = datetime.combine(day, time(12), timezone.utc)
    base_us = calendar.timegm(midday.utctimetuple()) * 1_000_000
    best_bid_ticks = 20_000
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(HEADER_FIELDS)
    for index in range(rows_per_date):
        # Future price increments do not consume or depend on order-size draws.
        best_bid_ticks += prices.choice((-1, 0, 0, 1))
        receive_us = base_us + (index // 2) * 100_000
        row: list[Any] = ["deribit", "BTC-PERPETUAL", receive_us - 2_500, receive_us]
        for level in range(5):
            ask_price = (best_bid_ticks + 2 + level) * 0.5
            bid_price = (best_bid_ticks - level) * 0.5
            # Quote-native USD amounts are independently drawn multiples of $10.
            ask_amount = sizes.randint(5, 5000) * 10
            bid_amount = sizes.randint(5, 5000) * 10
            row.extend((f"{ask_price:.1f}", ask_amount, f"{bid_price:.1f}", bid_amount))
        writer.writerow(row)
    return output.getvalue().encode("utf-8")


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def generate_fixture(
    raw_dir: str | Path,
    *,
    dates: Sequence[str],
    rows_per_date: int = 300,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Write byte-reproducible Tardis-schema *synthetic* CSVs and manifests.

    This is software-test data, never empirical evidence. Independent streams
    generate price increments and order sizes; no future price signal is planted
    in sizes. A fixed spread intentionally supplies a simple mathematical fixture.
    Existing differing files, or a non-synthetic aggregate manifest, are refused.
    """
    normalized_dates = _validated_arguments(dates, rows_per_date, seed)
    output = Path(raw_dir)
    if output.exists() and not output.is_dir():
        raise ValueError("raw_dir must name a directory")
    aggregate_path = output / "manifest.json"
    if aggregate_path.exists():
        try:
            existing = json.loads(aggregate_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise ValueError("Existing manifest cannot be verified as a generated fixture") from error
        if not isinstance(existing, list) or not existing or any(
            not isinstance(entry, dict)
            or entry.get("synthetic") is not True
            or entry.get("provider") != PROVIDER
            for entry in existing
        ):
            raise ValueError("Refusing to overwrite a non-synthetic source manifest")
    files: dict[str, bytes] = {}
    manifests: list[dict[str, Any]] = []
    for value in normalized_dates:
        name = f"synthetic_book_snapshot_5_{value}_BTC-PERPETUAL.csv"
        payload = _csv_payload(value, rows_per_date, seed)
        checksum = hashlib.sha256(payload).hexdigest()
        manifest: dict[str, Any] = {
            "schema_version": 1,
            "provider": PROVIDER,
            "synthetic": True,
            "exchange": "deribit",
            "symbol": "BTC-PERPETUAL",
            "date": value,
            "data_type": "book_snapshot_5",
            "path": name,
            "sha256": checksum,
            "excerpt_sha256": checksum,
            "excerpt_bytes": len(payload),
            "retained_rows": rows_per_date,
            "source_row_start": 1,
            "source_row_end": rows_per_date,
            "csv_schema": list(HEADER_FIELDS),
            "timestamp_unit": "microseconds since Unix epoch UTC",
            "amount_unit": "synthetic USD quote-native amounts, multiples of 10",
            "seed": seed,
            "generator": "synthetic-v1; independent per-date price/size PRNG streams",
            "selection": "All generated rows; not a historical-market excerpt.",
            "integrity_scope": "SHA-256 of the complete generated CSV.",
            "raw_and_sampled_data_redistribution": True,
            "license_note": "Project-generated test fixture; contains no vendor market data.",
            "market_evidence": False,
        }
        files[name] = payload
        files[Path(name).with_suffix(".manifest.json").name] = _json_bytes(manifest)
        manifests.append(manifest)
    # Check every planned immutable source artifact before creating/writing any.
    for name, payload in files.items():
        existing_path = output / name
        if existing_path.exists() and (
            not existing_path.is_file() or existing_path.read_bytes() != payload
        ):
            raise ValueError(f"Existing fixture differs: {name}; choose a fresh output directory")
    output.mkdir(parents=True, exist_ok=True)
    for name, payload in files.items():
        destination = output / name
        if not destination.exists():
            destination.write_bytes(payload)
    aggregate_path.write_bytes(_json_bytes(manifests))
    return manifests
