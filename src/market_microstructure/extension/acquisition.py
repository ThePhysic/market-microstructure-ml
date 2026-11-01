"""Bounded complete-day spot acquisition with fixed intraday selection.

Network access is explicit. Complete source gzip objects and selected original
rows remain local; only aggregate metadata/checksums belong in source control.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import re
import time
import urllib.request
from datetime import date as Date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import urlsplit, urlunsplit

from ..acquisition import AcquisitionError, HEADER_FIELDS, SAFE_HEADERS, TERMS_URL, sha256_file

DEFAULT_WINDOWS = tuple(range(0, 86_400, 10_800))
DEFAULT_WINDOW_SECONDS = 900
MAX_DATES = 64
MAX_TOTAL_BYTES = 1024**3
MAX_DISK_BYTES = 5 * 1024**3
MAX_WALL_SECONDS = 1200
MAX_COMPRESSED_PER_DATE = 16 * 1024**2
MAX_DECOMPRESSED_PER_DATE = 160 * 1024**2
MAX_LINE_BYTES = 65_536


def source_url(date: str) -> str:
    """Only the reviewed free Bitstamp spot instrument/date family is allowed."""
    try:
        parsed = Date.fromisoformat(date)
    except (ValueError, TypeError) as exc:
        raise AcquisitionError("Expected an ISO first-of-month date") from exc
    if date != parsed.isoformat() or parsed.day != 1 or not 2021 <= parsed.year <= 2024:
        raise AcquisitionError("Reviewed extension dates are monthly first days in 2021-2024")
    return f"https://datasets.tardis.dev/v1/bitstamp/book_snapshot_5/{parsed:%Y/%m/%d}/BTCUSD.csv.gz"


def validate_selection(windows: Iterable[int], window_seconds: int) -> tuple[int, ...]:
    values = tuple(windows)
    if not values or any(type(v) is not int for v in values):
        raise AcquisitionError("Window starts must be nonempty integer UTC seconds")
    if type(window_seconds) is not int or not 1 <= window_seconds <= 86_400:
        raise AcquisitionError("Window duration must be an integer in 1-86400 seconds")
    if tuple(sorted(set(values))) != values:
        raise AcquisitionError("Window starts must be unique and strictly increasing")
    if any(v < 0 or v + window_seconds > 86_400 for v in values):
        raise AcquisitionError("Windows must lie within one UTC date")
    if any(b < a + window_seconds for a, b in zip(values, values[1:])):
        raise AcquisitionError("Selection windows cannot overlap")
    return values


def _positive_int(value: int, ceiling: int, name: str) -> None:
    if type(value) is not int or not 0 < value <= ceiling:
        raise AcquisitionError(f"{name} must be a positive integer <= {ceiling}")


def _deadline_check(deadline: float | None) -> None:
    if deadline is not None and time.monotonic() > deadline:
        raise AcquisitionError("Acquisition wall-clock budget exceeded")


def _safe_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _disk_size(directory: Path) -> int:
    return sum(p.stat().st_size for p in directory.rglob("*") if p.is_file()) if directory.exists() else 0


def _selection_contract(windows: tuple[int, ...], seconds: int) -> dict[str, Any]:
    return {"window_starts_utc_seconds": list(windows), "window_seconds": seconds,
            "inclusion": "start inclusive, end exclusive, local receipt time",
            "retention": "every source observation inside each predeclared window"}


def download_day(
    date: str, raw_dir: str | Path, *, windows: Iterable[int] = DEFAULT_WINDOWS,
    window_seconds: int = DEFAULT_WINDOW_SECONDS,
    max_compressed_bytes: int = MAX_COMPRESSED_PER_DATE,
    max_decompressed_bytes: int = MAX_DECOMPRESSED_PER_DATE,
    max_new_disk_bytes: int = MAX_DISK_BYTES, timeout: float = 30,
    deadline: float | None = None, expected_source_bytes: int | None = None,
    existing_gzip: str | Path | None = None, expected_compressed_sha256: str | None = None,
    opener: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Fetch a whole gzip, validate CRC, and retain fixed windows without row caps.

    The temporary full CSV is never materialized. A bounded line buffer streams
    the complete gzip into a much smaller selected CSV. Source row ranges map
    retained records to the original full-day source order.
    """
    url = source_url(date)
    starts = validate_selection(windows, window_seconds)
    _positive_int(max_compressed_bytes, MAX_COMPRESSED_PER_DATE, "compressed cap")
    _positive_int(max_decompressed_bytes, MAX_DECOMPRESSED_PER_DATE, "decoded cap")
    _positive_int(max_new_disk_bytes, MAX_DISK_BYTES, "new disk cap")
    if not isinstance(timeout, (float, int)) or not math.isfinite(timeout) or not 0 < timeout <= 120:
        raise AcquisitionError("timeout must be finite and in (0,120]")
    _deadline_check(deadline)
    output = Path(raw_dir)
    stem = f"bitstamp_book_snapshot_5_{date}_BTCUSD"
    gzip_path = output / f"{stem}.csv.gz"
    csv_path = output / f"{stem}.selected.csv"
    manifest_path = output / f"{stem}.manifest.json"
    selection = _selection_contract(starts, window_seconds)
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if (manifest["retrieval_url"] != url or manifest["selection"] != selection
                    or manifest["requested_compressed_cap"] != max_compressed_bytes
                    or manifest["requested_decoded_cap"] != max_decompressed_bytes):
                raise AcquisitionError("Existing source has a different frozen selection/contract")
            if (sha256_file(gzip_path) != manifest["compressed_sha256"]
                    or sha256_file(csv_path) != manifest["excerpt_sha256"]):
                raise AcquisitionError("Existing source checksum mismatch")
            if expected_source_bytes is not None and manifest["source_compressed_bytes"] != expected_source_bytes:
                raise AcquisitionError("Existing source size differs from frozen catalogue")
            return manifest
        except (OSError, KeyError, json.JSONDecodeError) as exc:
            raise AcquisitionError("Incomplete or malformed cached source") from exc
    if gzip_path.exists() or csv_path.exists():
        raise AcquisitionError("Refusing to overwrite unmanifested historical files")
    output.mkdir(parents=True, exist_ok=True)
    gzip_part, csv_part = Path(str(gzip_path) + ".part"), Path(str(csv_path) + ".part")
    if gzip_part.exists() or csv_part.exists():
        raise AcquisitionError("An incomplete acquisition exists; inspect it before retrying")
    request = urllib.request.Request(url, headers={
        "Range": f"bytes=0-{max_compressed_bytes - 1}", "Accept-Encoding": "identity"})
    transferred = decoded_bytes = selected_bytes = 0
    try:
        if existing_gzip is not None:
            prior = Path(existing_gzip)
            if not expected_compressed_sha256 or sha256_file(prior) != expected_compressed_sha256:
                raise AcquisitionError("Feasibility gzip requires its previously verified checksum")
            source_bytes = prior.stat().st_size
            if not 0 < source_bytes <= min(max_compressed_bytes, max_new_disk_bytes):
                raise AcquisitionError("Reused source exceeds compressed or disk budget")
            if expected_source_bytes is not None and source_bytes != expected_source_bytes:
                raise AcquisitionError("Reused source differs from frozen catalogue size")
            with prior.open("rb") as source, gzip_part.open("xb") as handle:
                for chunk in iter(lambda: source.read(256 * 1024), b""):
                    _deadline_check(deadline)
                    handle.write(chunk)
            status, headers, response_url = None, {}, url
        else:
            with (opener or urllib.request.urlopen)(request, timeout=timeout) as response:
                status = int(response.status)
                headers = {k: response.headers.get(k) for k in SAFE_HEADERS if response.headers.get(k)}
                if response.headers.get("Content-Encoding", "identity").lower() not in ("", "identity"):
                    raise AcquisitionError("Encoded transport obscures compressed source provenance")
                if status == 206:
                    match = re.fullmatch(r"bytes 0-(\d+)/(\d+)", response.headers.get("Content-Range", ""))
                    if not match or int(match[1]) + 1 != int(match[2]):
                        raise AcquisitionError("Complete source range required; no prefix fallback")
                    source_bytes = int(match[2])
                elif status == 200 and response.headers.get("Content-Length", "").isdigit():
                    source_bytes = int(response.headers["Content-Length"])
                else:
                    raise AcquisitionError("Response does not establish a bounded complete source")
                if not 0 < source_bytes <= min(max_compressed_bytes, max_new_disk_bytes):
                    raise AcquisitionError("Complete source exceeds compressed or disk budget")
                if expected_source_bytes is not None and source_bytes != expected_source_bytes:
                    raise AcquisitionError("Source size changed from frozen catalogue")
                with gzip_part.open("xb") as handle:
                    while transferred < source_bytes:
                        _deadline_check(deadline)
                        chunk = response.read(min(256 * 1024, source_bytes - transferred))
                        if not chunk:
                            break
                        if len(chunk) > source_bytes - transferred:
                            raise AcquisitionError("Response exceeded advertised compressed size")
                        transferred += len(chunk)
                        handle.write(chunk)
                if transferred != source_bytes:
                    raise AcquisitionError("Truncated complete-source response")
                response_url = _safe_url(response.geturl())
        compressed_sha = sha256_file(gzip_part)
        provider_md5 = headers.get("x-md5", headers.get("x-amz-meta-md5", "")).strip('"')
        md5_verified = False
        if re.fullmatch(r"[0-9a-fA-F]{32}", provider_md5):
            digest = hashlib.md5(usedforsecurity=False)
            with gzip_part.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest().lower() != provider_md5.lower():
                raise AcquisitionError("Provider whole-source MD5 mismatch")
            md5_verified = True
        base_us = int(datetime.combine(Date.fromisoformat(date), datetime.min.time(), timezone.utc).timestamp()) * 1_000_000
        intervals = [(base_us + s * 1_000_000, base_us + (s + window_seconds) * 1_000_000) for s in starts]
        windows_quality = [{"window_start_utc_seconds": s, "window_seconds": window_seconds,
                            "retained_rows": 0, "first_offset_seconds": None,
                            "last_offset_seconds": None} for s in starts]
        ranges: list[dict[str, int]] = []
        total_rows = retained_rows = off_tick = off_quantity = 0
        first_receive = last_receive = None
        with gzip.open(gzip_part, "rb") as source, csv_part.open("xb") as selected:
            while True:
                _deadline_check(deadline)
                line = source.readline(MAX_LINE_BYTES + 1)
                if not line:
                    break  # gzip reader reaches EOF and validates whole-source CRC/trailer.
                decoded_bytes += len(line)
                if len(line) > MAX_LINE_BYTES or decoded_bytes > max_decompressed_bytes:
                    raise AcquisitionError("Decoded source exceeds line or total memory/disk budget")
                try:
                    row = next(csv.reader([line.decode("utf-8")], strict=True))
                except (UnicodeError, csv.Error, StopIteration) as exc:
                    raise AcquisitionError("Invalid UTF-8 CSV source") from exc
                if decoded_bytes == len(line):
                    if row != HEADER_FIELDS:
                        raise AcquisitionError("Unexpected top-five source schema")
                    selected.write(line)
                    selected_bytes += len(line)
                    continue
                total_rows += 1
                if len(row) != len(HEADER_FIELDS) or row[:2] != ["bitstamp", "BTCUSD"]:
                    raise AcquisitionError("Malformed source record or spot market mismatch")
                if not row[3].isdecimal() or not row[2].isdecimal():
                    raise AcquisitionError("Source timestamps must be integer UTC microseconds")
                receive = int(row[3])
                if not base_us <= receive < base_us + 86_400_000_000:
                    raise AcquisitionError("Source record is outside its local UTC date")
                first_receive = receive if first_receive is None else min(first_receive, receive)
                last_receive = receive if last_receive is None else max(last_receive, receive)
                window_index = next((i for i, (a, b) in enumerate(intervals) if a <= receive < b), None)
                if window_index is None:
                    continue
                retained_rows += 1
                selected_bytes += len(line)
                if source_bytes + selected_bytes > max_new_disk_bytes:
                    raise AcquisitionError("Historical disk budget exceeded")
                selected.write(line)
                if (ranges and ranges[-1]["window_index"] == window_index
                        and ranges[-1]["source_row_end"] == total_rows - 1):
                    ranges[-1]["source_row_end"] = total_rows
                    ranges[-1]["selected_row_end"] = retained_rows
                else:
                    ranges.append({"window_index": window_index, "source_row_start": total_rows,
                                   "source_row_end": total_rows, "selected_row_start": retained_rows,
                                   "selected_row_end": retained_rows})
                quality = windows_quality[window_index]
                offset = (receive - intervals[window_index][0]) / 1_000_000
                quality["retained_rows"] += 1
                quality["first_offset_seconds"] = offset if quality["first_offset_seconds"] is None else min(quality["first_offset_seconds"], offset)
                quality["last_offset_seconds"] = offset if quality["last_offset_seconds"] is None else max(quality["last_offset_seconds"], offset)
                for position in range(4, len(row), 2):
                    try:
                        price, quantity = Decimal(row[position]), Decimal(row[position + 1])
                        off_tick += not price.is_finite() or price % Decimal("0.01") != 0
                        off_quantity += not quantity.is_finite() or quantity % Decimal("0.00000001") != 0
                    except InvalidOperation:
                        off_tick += 1
                        off_quantity += 1
        if not total_rows or not retained_rows:
            raise AcquisitionError("No source/selected observations")
        for quality in windows_quality:
            a, b = quality["first_offset_seconds"], quality["last_offset_seconds"]
            quality["observed_span_seconds"] = b - a if a is not None else 0
        manifest: dict[str, Any] = {
            "schema_version": 1, "provider": "Tardis.dev", "exchange": "bitstamp", "symbol": "BTCUSD",
            "market_type": "spot", "base_currency": "BTC", "quote_currency": "USD",
            "price_unit": "USD per BTC", "size_unit": "BTC", "date": date,
            "data_type": "book_snapshot_5", "synthetic": False, "retrieval_url": url,
            "response_url_without_query": response_url, "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "http_status": status, "response_headers": headers, "requested_compressed_cap": max_compressed_bytes,
            "reused_feasibility_gzip": existing_gzip is not None,
            "requested_decoded_cap": max_decompressed_bytes, "bytes_received": transferred,
            "source_compressed_bytes": source_bytes, "decoded_source_bytes": decoded_bytes,
            "source_total_rows": total_rows, "source_span_seconds": (last_receive - first_receive) / 1_000_000,
            "retained_rows": retained_rows, "excerpt_bytes": selected_bytes, "selection": selection,
            "source_row_ranges": ranges, "window_coverage": windows_quality,
            "path": csv_path.name, "gzip_path": gzip_path.name, "excerpt_sha256": sha256_file(csv_part),
            "sha256": sha256_file(csv_part), "compressed_sha256": compressed_sha,
            "complete_source_gzip": True, "gzip_crc_verified": True, "provider_md5_verified": md5_verified,
            "csv_schema": HEADER_FIELDS, "timestamp_unit": "microseconds since Unix epoch UTC",
            "off_research_price_grid_cells": off_tick, "off_research_quantity_grid_cells": off_quantity,
            "license_url": TERMS_URL, "raw_and_sampled_data_redistribution": False,
            "trained_model_redistribution": False,
        }
        manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        if source_bytes + selected_bytes + len(manifest_text.encode("utf-8")) > max_new_disk_bytes:
            raise AcquisitionError("Historical disk budget includes acquisition metadata")
        gzip_part.replace(gzip_path)
        csv_part.replace(csv_path)
        manifest_path.write_text(manifest_text, encoding="utf-8")
        return manifest
    except (OSError, EOFError, ValueError, OverflowError) as exc:
        if isinstance(exc, AcquisitionError):
            error = exc
        else:
            error = AcquisitionError(f"Complete spot-source acquisition failed: {exc}")
        error.bytes_received = transferred
        for partial in (gzip_part, csv_part):
            partial.unlink(missing_ok=True)
        raise error from (exc if error is not exc else None)


def download_days(
    dates: Iterable[str], raw_dir: str | Path, *, windows: Iterable[int] = DEFAULT_WINDOWS,
    window_seconds: int = DEFAULT_WINDOW_SECONDS, max_total_compressed_bytes: int = MAX_TOTAL_BYTES,
    max_disk_bytes: int = MAX_DISK_BYTES, max_wall_seconds: float = MAX_WALL_SECONDS,
    existing_probe_bytes: int = 0, expected_source_sizes: dict[str, int] | None = None,
    existing_gzips: dict[str, tuple[str | Path, str]] | None = None,
    opener: Callable[..., Any] | None = None, **kwargs: Any,
) -> list[dict[str, Any]]:
    """Explicit full sources under aggregate transfer/disk/time limits; no retries."""
    selected_dates = list(dates)
    if not selected_dates or len(selected_dates) > MAX_DATES or len(set(selected_dates)) != len(selected_dates):
        raise AcquisitionError("Choose 1-64 unique dates")
    for date in selected_dates:
        source_url(date)
    starts = validate_selection(windows, window_seconds)
    _positive_int(max_total_compressed_bytes, MAX_TOTAL_BYTES, "aggregate transfer cap")
    _positive_int(max_disk_bytes, MAX_DISK_BYTES, "aggregate disk cap")
    if (type(existing_probe_bytes) is not int or existing_probe_bytes < 0
            or existing_probe_bytes >= max_total_compressed_bytes):
        raise AcquisitionError("Invalid accounted feasibility transfer")
    if not isinstance(max_wall_seconds, (float, int)) or not math.isfinite(max_wall_seconds) or not 0 < max_wall_seconds <= MAX_WALL_SECONDS:
        raise AcquisitionError("Wall-clock cap must be in (0,1200] seconds")
    if expected_source_sizes is not None and set(expected_source_sizes) != set(selected_dates):
        raise AcquisitionError("Frozen source-size catalogue must cover exactly all selected dates")
    cap = kwargs.get("max_compressed_bytes", MAX_COMPRESSED_PER_DATE)
    _positive_int(cap, MAX_COMPRESSED_PER_DATE, "compressed cap")
    if expected_source_sizes is not None:
        for value in expected_source_sizes.values():
            _positive_int(value, cap, "frozen complete-source size")
    projected = sum(expected_source_sizes.values()) if expected_source_sizes is not None else len(selected_dates) * cap
    if projected + existing_probe_bytes > max_total_compressed_bytes:
        raise AcquisitionError("Complete sources exceed aggregate transfer budget")
    deadline = time.monotonic() + max_wall_seconds
    results = []
    accounted = existing_probe_bytes
    for date in sorted(selected_dates):
        _deadline_check(deadline)
        remaining_disk = max_disk_bytes - _disk_size(Path(raw_dir))
        if remaining_disk <= 0:
            raise AcquisitionError("Historical storage budget exhausted")
        manifest = download_day(date, raw_dir, windows=starts, window_seconds=window_seconds,
                                deadline=deadline, max_new_disk_bytes=remaining_disk,
                                expected_source_bytes=expected_source_sizes[date] if expected_source_sizes else None,
                                existing_gzip=existing_gzips[date][0] if existing_gzips and date in existing_gzips else None,
                                expected_compressed_sha256=existing_gzips[date][1] if existing_gzips and date in existing_gzips else None,
                                opener=opener, **kwargs)
        accounted += manifest["bytes_received"]  # conservative: cached files count against this study budget too.
        if accounted > max_total_compressed_bytes:
            raise AcquisitionError("Historical transfer budget exceeded")
        results.append(manifest)
    target = Path(raw_dir) / "manifest.json"
    manifest_text = json.dumps(results, indent=2, sort_keys=True) + "\n"
    previous_bytes = target.stat().st_size if target.exists() else 0
    if _disk_size(Path(raw_dir)) - previous_bytes + len(manifest_text.encode("utf-8")) > max_disk_bytes:
        raise AcquisitionError("Historical disk budget includes the combined manifest")
    target.write_text(manifest_text, encoding="utf-8")
    return results
