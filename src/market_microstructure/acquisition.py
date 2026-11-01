"""Bounded, opt-in acquisition of free first-of-month Tardis CSV excerpts.

Compressed prefixes have local SHA-256 integrity, not whole-day gzip CRC/MD5
verification. Complete original CSV rows are retained separately for analysis.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import urllib.request
import zlib
from datetime import date as Date, datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit, urlunsplit

TERMS_URL = "https://docs.tardis.dev/legal/terms-of-service"
MAX_DATES = 12
MAX_BYTES_PER_DATE = 2 * 1024**2
MAX_ROWS_PER_DATE = 20_000
MAX_TOTAL_BYTES = 24 * 1024**2
HEADER_FIELDS = ["exchange", "symbol", "timestamp", "local_timestamp"] + [
    f"{side}[{level}].{field}"
    for level in range(5)
    for side in ("asks", "bids")
    for field in ("price", "amount")
]
SAFE_HEADERS = (
    "Content-Type", "Content-Length", "Content-Range", "Accept-Ranges",
    "ETag", "Last-Modified", "x-md5", "x-amz-meta-md5",
)


class AcquisitionError(ValueError):
    """The source response or acquisition bounds could not be verified."""


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_url(date: str, exchange: str, symbol: str) -> str:
    try:
        parsed = Date.fromisoformat(date)
    except ValueError as exc:
        raise AcquisitionError("date must be an ISO calendar date") from exc
    if date != parsed.isoformat() or parsed.day != 1:
        raise AcquisitionError("Only explicitly free first-of-month dates are supported")
    if exchange != "deribit" or symbol != "BTC-PERPETUAL":
        raise AcquisitionError("The reviewed source contract supports deribit BTC-PERPETUAL only")
    return f"https://datasets.tardis.dev/v1/{exchange}/book_snapshot_5/{parsed:%Y/%m/%d}/{symbol}.csv.gz"


def _validate_bounds(max_compressed_bytes: int, max_rows: int, max_decompressed_bytes: int) -> None:
    if type(max_compressed_bytes) is not int or not 1 <= max_compressed_bytes <= MAX_BYTES_PER_DATE:
        raise AcquisitionError("compressed cap must be an integer between 1 and 2 MiB")
    if type(max_rows) is not int or not 1 <= max_rows <= MAX_ROWS_PER_DATE:
        raise AcquisitionError("row cap must be an integer between 1 and 20,000")
    if type(max_decompressed_bytes) is not int or not 1 <= max_decompressed_bytes <= 32 * 1024**2:
        raise AcquisitionError("decompressed cap must be an integer between 1 and 32 MiB")


def _safe_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def download_excerpt(
    date: str, output_dir: str | Path, *, exchange: str = "deribit",
    symbol: str = "BTC-PERPETUAL", max_compressed_bytes: int = MAX_BYTES_PER_DATE,
    max_rows: int = MAX_ROWS_PER_DATE, max_decompressed_bytes: int = 32 * 1024**2,
    timeout: float = 30, opener: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Fetch a bounded gzip prefix; retain at most max_rows complete CSV records.

    Network access occurs only on explicit invocation. Existing matching artifacts
    are reused after both local hashes are checked. No keys or paid endpoints.
    """
    _validate_bounds(max_compressed_bytes, max_rows, max_decompressed_bytes)
    if not isinstance(timeout, (int, float)) or not 0 < timeout <= 120:
        raise AcquisitionError("timeout must be positive and at most 120 seconds")
    url = _source_url(date, exchange, symbol)
    output = Path(output_dir)
    stem = f"{exchange}_book_snapshot_5_{date}_{symbol}"
    csv_path = output / f"{stem}.csv"
    prefix_path = output / f"{stem}.csv.gz.prefix"
    manifest_path = output / f"{stem}.manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if (manifest["retrieval_url"], manifest["requested_compressed_cap"], manifest["requested_row_cap"]) != (url, max_compressed_bytes, max_rows):
                raise AcquisitionError("Existing excerpt has a different acquisition contract")
            if sha256_file(csv_path) != manifest["excerpt_sha256"]:
                raise AcquisitionError("Existing CSV excerpt checksum mismatch")
            if sha256_file(prefix_path) != manifest["compressed_sha256"]:
                raise AcquisitionError("Existing compressed prefix checksum mismatch")
            return manifest
        except (OSError, KeyError, json.JSONDecodeError) as exc:
            raise AcquisitionError("Existing acquisition artifacts are incomplete or malformed") from exc
    if csv_path.exists() or prefix_path.exists():
        raise AcquisitionError("Refusing to overwrite unmanifested source files")
    request = urllib.request.Request(url, headers={
        "Range": f"bytes=0-{max_compressed_bytes - 1}", "Accept-Encoding": "identity",
    })
    open_request = opener or urllib.request.urlopen
    compressed = bytearray()
    decoded = bytearray()
    inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
    with open_request(request, timeout=timeout) as response:
        status = int(response.status)
        headers = {key: response.headers.get(key) for key in SAFE_HEADERS if response.headers.get(key)}
        source_bytes: int | None = None
        if status == 206:
            match = re.fullmatch(r"bytes 0-(\d+)/(\d+)", response.headers.get("Content-Range", ""))
            if not match:
                raise AcquisitionError("Partial response must prove a source range starting at byte zero")
            range_end, source_bytes = map(int, match.groups())
            if range_end >= max_compressed_bytes or range_end >= source_bytes:
                raise AcquisitionError("Server returned a range beyond the requested cap or source")
            advertised_bytes = range_end + 1
        elif status == 200:
            length = response.headers.get("Content-Length", "")
            if not length.isdigit() or not 0 < int(length) <= max_compressed_bytes:
                raise AcquisitionError("Server ignored Range without proving a bounded complete response")
            advertised_bytes = source_bytes = int(length)
        else:
            raise AcquisitionError(f"Unexpected HTTP status {status}")
        if response.headers.get("Content-Encoding", "identity").lower() not in ("", "identity"):
            raise AcquisitionError("Transport encoding would make source-byte provenance ambiguous")
        while len(compressed) < max_compressed_bytes:
            chunk = response.read(min(64 * 1024, max_compressed_bytes - len(compressed)))
            if not chunk:
                break
            if len(chunk) > max_compressed_bytes - len(compressed):
                raise AcquisitionError("Response reader exceeded compressed-byte budget")
            compressed.extend(chunk)
            try:
                output_chunk = inflater.decompress(chunk, max(1, max_decompressed_bytes - len(decoded)))
            except zlib.error as exc:
                raise AcquisitionError("Response is not a valid gzip prefix") from exc
            decoded.extend(output_chunk)
            if len(decoded) > max_decompressed_bytes or inflater.unconsumed_tail:
                raise AcquisitionError("Decompression budget exceeded")
            if decoded.count(b"\n") >= max_rows + 1:
                break
        response_url = _safe_url(response.geturl())
    if not compressed or len(compressed) > advertised_bytes:
        raise AcquisitionError("Compressed length is inconsistent with the advertised range")
    last_newline = decoded.rfind(b"\n")
    if last_newline < 0:
        raise AcquisitionError("No complete CSV header within the bounded prefix")
    complete_lines = bytes(decoded[: last_newline + 1]).splitlines(keepends=True)
    excerpt = b"".join(complete_lines[: max_rows + 1])
    try:
        schema = next(csv.reader(io.StringIO(excerpt.decode("utf-8"))))
    except (UnicodeDecodeError, StopIteration, csv.Error) as exc:
        raise AcquisitionError("Source excerpt has an invalid UTF-8 CSV header") from exc
    if schema != HEADER_FIELDS:
        raise AcquisitionError("Source schema differs from the pinned top-five schema")
    retained_rows = min(len(complete_lines) - 1, max_rows)
    if retained_rows <= 0:
        raise AcquisitionError("No complete data rows were obtained")
    gzip_complete = bool(inflater.eof and len(compressed) == source_bytes)
    manifest: dict[str, Any] = {
        "schema_version": 1, "provider": "Tardis.dev", "exchange": exchange,
        "symbol": symbol, "date": date, "data_type": "book_snapshot_5", "synthetic": False,
        "retrieval_url": url, "response_url_without_query": response_url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "http_status": status, "response_headers": headers,
        "requested_compressed_cap": max_compressed_bytes, "requested_row_cap": max_rows,
        "bytes_received": len(compressed), "source_compressed_bytes": source_bytes,
        "decompressed_prefix_bytes": len(decoded), "excerpt_bytes": len(excerpt),
        "retained_rows": retained_rows,
        "discarded_complete_prefix_rows": max(0, len(complete_lines) - 1 - retained_rows),
        "source_row_start": 1, "source_row_end": retained_rows,
        "path": csv_path.name, "prefix_path": prefix_path.name,
        "sha256": hashlib.sha256(excerpt).hexdigest(),
        "excerpt_sha256": hashlib.sha256(excerpt).hexdigest(),
        "compressed_sha256": hashlib.sha256(compressed).hexdigest(),
        "csv_schema": schema, "timestamp_unit": "microseconds since Unix epoch UTC",
        "selection": "first complete source rows within a bounded compressed prefix",
        "complete_source_gzip": gzip_complete,
        "integrity_scope": (
            "Complete gzip decoded; local SHA-256 recorded."
            if gzip_complete else
            "Partial gzip prefix only. Local prefix and complete-row excerpt SHA-256 recorded; "
            "whole-source gzip CRC and provider whole-file MD5 are NOT verified."
        ),
        "license_url": TERMS_URL, "raw_and_sampled_data_redistribution": False,
        "trained_model_redistribution": False,
    }
    output.mkdir(parents=True, exist_ok=True)
    prefix_path.write_bytes(compressed)
    csv_path.write_bytes(excerpt)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def download_many(
    dates: list[str], output_dir: str | Path, *,
    max_total_compressed_bytes: int = MAX_TOTAL_BYTES, **kwargs: Any,
) -> list[dict[str, Any]]:
    """Acquire at most twelve unique dates under one aggregate application-byte cap."""
    if not dates or len(dates) > MAX_DATES or len(set(dates)) != len(dates):
        raise AcquisitionError("Choose between one and twelve distinct dates")
    if type(max_total_compressed_bytes) is not int or not 1 <= max_total_compressed_bytes <= MAX_TOTAL_BYTES:
        raise AcquisitionError("Total compressed budget must be an integer between 1 and 24 MiB")
    per_date = kwargs.get("max_compressed_bytes", MAX_BYTES_PER_DATE)
    if len(dates) * per_date > max_total_compressed_bytes:
        raise AcquisitionError("Requested ranges exceed aggregate budget; lower the per-date cap")
    results = [download_excerpt(date, output_dir, **kwargs) for date in sorted(dates)]
    if sum(item["bytes_received"] for item in results) > max_total_compressed_bytes:
        raise AcquisitionError("Aggregate compressed-byte budget exceeded")
    return results
