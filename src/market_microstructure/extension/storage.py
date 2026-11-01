"""Local-only normalization and checked batch storage, preserving source order."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Iterator

import numpy as np
import pandas as pd

from ..acquisition import sha256_file
from ..data import DataIntegrityError, NORMALIZED_COLUMNS, ingest_files


def _local_path(directory: Path, filename: str) -> Path:
    if not isinstance(filename, str) or Path(filename).name != filename or filename in ("", ".", ".."):
        raise DataIntegrityError("Artifact path must be a portable basename")
    target = directory / filename
    if target.resolve().parent != directory.resolve():
        raise DataIntegrityError("Artifact path escapes its storage directory")
    return target


def validate_states(states: pd.DataFrame) -> None:
    """Check normalized identity/order/time, including ordering across batches."""
    if list(states.columns[:len(NORMALIZED_COLUMNS)]) != NORMALIZED_COLUMNS:
        raise DataIntegrityError("Expected normalized top-five columns in canonical order")
    if states.empty:
        raise DataIntegrityError("No normalized observations")
    for key in ("source_order", "receive_time_us", "event_time_us", "source_row_position"):
        if not pd.api.types.is_integer_dtype(states[key]):
            raise DataIntegrityError(f"{key} must retain exact integer precision")
    if ((states["source_order"].diff().dropna() <= 0).any()
            or (states["receive_time_us"].diff().dropna() < 0).any()
            or (states["source_row_position"] <= 0).any()):
        raise DataIntegrityError("States must preserve increasing source order and nondecreasing receipt time")
    if states["provenance_key"].isna().any() or states["provenance_key"].duplicated().any():
        raise DataIntegrityError("Duplicate/missing provenance")
    book = states[NORMALIZED_COLUMNS[10:]].to_numpy(dtype=np.float64)
    bids = states[[f"bid_price_{i}" for i in range(1, 6)]].to_numpy()
    asks = states[[f"ask_price_{i}" for i in range(1, 6)]].to_numpy()
    sizes = states[[f"{side}_size_{i}" for i in range(1, 6) for side in ("bid", "ask")]].to_numpy()
    if (not np.isfinite(book).all() or (bids <= 0).any() or (asks <= 0).any()
            or (sizes < 0).any() or (bids[:, 0] >= asks[:, 0]).any()
            or (np.diff(bids, axis=1) >= 0).any() or (np.diff(asks, axis=1) <= 0).any()):
        raise DataIntegrityError("Malformed normalized five-level book")


def _ranges(manifest: dict[str, Any]) -> list[dict[str, int]]:
    ranges = manifest.get("source_row_ranges", [])
    if not ranges:
        raise DataIntegrityError("Missing original-source row mapping")
    expected_selected, previous_source = 1, 0
    for item in ranges:
        names = ("source_row_start", "source_row_end", "selected_row_start", "selected_row_end", "window_index")
        if any(type(item.get(k)) is not int for k in names):
            raise DataIntegrityError("Source row mappings must retain integer positions")
        a, b, c, d = (item[k] for k in names[:4])
        if (a <= previous_source or b < a or c != expected_selected or d < c or b - a != d - c
                or item["window_index"] < 0 or item["window_index"] >= len(manifest["selection"]["window_starts_utc_seconds"])):
            raise DataIntegrityError("Source row mapping is inconsistent or overlaps")
        expected_selected, previous_source = d + 1, b
    if expected_selected != manifest["retained_rows"] + 1 or previous_source > manifest["source_total_rows"]:
        raise DataIntegrityError("Source row mapping does not cover the selected source")
    return ranges


def _one_date(manifest: dict[str, Any], raw_dir: Path, source_offset: int, gap_seconds: float):
    path = _local_path(raw_dir, manifest["path"])
    zipped = _local_path(raw_dir, manifest["gzip_path"])
    if sha256_file(zipped) != manifest["compressed_sha256"]:
        raise DataIntegrityError("Complete gzip checksum mismatch")
    ranges = _ranges(manifest)
    frame, quality = ingest_files([path], exchange="bitstamp", symbol="BTCUSD",
                                  gap_seconds=gap_seconds, manifests=[manifest])
    if quality["total_rows"] != manifest["retained_rows"]:
        raise DataIntegrityError("Selected CSV row count differs from manifest")
    ends = np.array([r["selected_row_end"] for r in ranges], dtype=np.int64)
    selected_positions = frame["source_row_position"].to_numpy()
    indices = np.searchsorted(ends, selected_positions, side="left")
    original = np.array([r["source_row_start"] - r["selected_row_start"] for r in ranges], dtype=np.int64)[indices] + selected_positions
    window_indices = np.array([r["window_index"] for r in ranges], dtype=np.int64)[indices]
    starts = manifest["selection"]["window_starts_utc_seconds"]
    duration = manifest["selection"]["window_seconds"]
    seconds = (frame["receive_time_us"].to_numpy() % 86_400_000_000) / 1_000_000
    if any(not starts[w] <= sec < starts[w] + duration for w, sec in zip(window_indices, seconds)):
        raise DataIntegrityError("Selection-row mapping disagrees with receipt-time windows")
    frame["source_row_position"] = original
    frame["source_order"] = original + source_offset
    frame["provenance_key"] = [f"{manifest['compressed_sha256']}:{row}" for row in original]
    frame["segment_id"] = [f"{date}:w{window:02d}:{segment}" for date, window, segment
                           in zip(frame["session_date"], window_indices, frame["segment_id"])]
    # Detailed exclusions stay local and refer to original full-source positions too.
    for item in quality["exclusions"]:
        position = item["source_row_position"]
        row_range = ranges[int(np.searchsorted(ends, position, side="left"))]
        item["source_row_position"] = position + row_range["source_row_start"] - row_range["selected_row_start"]
        item["source_order"] = item["source_row_position"] + source_offset
    quality["segments"] = int(frame["segment_id"].nunique())
    validate_states(frame)
    return frame, quality


def iter_normalized_batches(
    manifests: Iterable[dict[str, Any]], raw_dir: str | Path, *, gap_seconds: float = 30,
    batch_rows: int = 50_000,
) -> Iterator[tuple[pd.DataFrame, dict[str, Any] | None]]:
    """Normalize one date at a time; batching never resets temporal state.

    Each date's quality record accompanies its first batch. Row positions/order
    count the complete original sources, including unselected intraday events.
    """
    if type(batch_rows) is not int or batch_rows <= 0:
        raise DataIntegrityError("batch_rows must be a positive integer")
    sources = sorted(list(manifests), key=lambda m: m["date"])
    if not sources or len({m["date"] for m in sources}) != len(sources):
        raise DataIntegrityError("One unambiguous source per selected date is required")
    source_offset = 0
    last_order = last_receive = None
    for manifest in sources:
        if manifest.get("exchange") != "bitstamp" or manifest.get("symbol") != "BTCUSD" or manifest.get("market_type") != "spot":
            raise DataIntegrityError("Expected reviewed Bitstamp BTCUSD spot sources")
        frame, quality = _one_date(manifest, Path(raw_dir), source_offset, gap_seconds)
        if last_order is not None and (frame["source_order"].iloc[0] <= last_order or frame["receive_time_us"].iloc[0] < last_receive):
            raise DataIntegrityError("Normalized date boundary violates source/time order")
        for position in range(0, len(frame), batch_rows):
            yield frame.iloc[position:position + batch_rows].reset_index(drop=True), quality if position == 0 else None
        source_offset += manifest["source_total_rows"]
        last_order, last_receive = int(frame["source_order"].iloc[-1]), int(frame["receive_time_us"].iloc[-1])


def load_states(
    manifests: Iterable[dict[str, Any]], raw_dir: str | Path, *, gap_seconds: float = 30,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Adapter to original ingestion with full-source provenance and window IDs."""
    frames, reports = [], []
    for frame, quality in iter_normalized_batches(manifests, raw_dir, gap_seconds=gap_seconds):
        frames.append(frame)
        if quality is not None:
            reports.append(quality)
    result = pd.concat(frames, ignore_index=True)
    validate_states(result)
    counts, reasons = Counter(), Counter()
    for quality in reports:
        counts.update(quality["counts"])
        reasons.update(quality["exclusion_counts"])
    return result, {
        "schema_version": 1, "total_rows": sum(r["total_rows"] for r in reports),
        "retained_rows": len(result), "excluded_rows": sum(r["excluded_rows"] for r in reports),
        "counts": dict(counts), "exclusion_counts": dict(reasons),
        "exclusions": [e for r in reports for e in r["exclusions"]],
        "per_file": [f for r in reports for f in r["per_file"]],
        "segments": int(result["segment_id"].nunique()), "sessions": sorted(result["session_date"].unique().tolist()),
        "price_unit": "USD per BTC", "size_unit": "BTC", "gap_seconds": gap_seconds,
        "provenance_policy": "complete source gzip SHA-256 plus original full-source row; global order includes unselected rows",
        "warnings": reports[0]["warnings"] + ["Each predeclared intraday window starts a distinct segment."],
    }


def iter_state_batches(states: pd.DataFrame, batch_rows: int = 50_000) -> Iterator[pd.DataFrame]:
    validate_states(states)
    if type(batch_rows) is not int or batch_rows <= 0:
        raise DataIntegrityError("batch_rows must be a positive integer")
    for position in range(0, len(states), batch_rows):
        yield states.iloc[position:position + batch_rows].reset_index(drop=True)


def write_state_store(states: pd.DataFrame, directory: str | Path, *, batch_rows: int = 50_000) -> dict[str, Any]:
    """Optional ignored/local numeric+Unicode NPZ store; no pickle/object arrays."""
    validate_states(states)
    if list(states.columns) != NORMALIZED_COLUMNS:
        raise DataIntegrityError("State-store schema accepts normalized columns only")
    target = Path(directory)
    if target.exists() and any(target.iterdir()):
        raise DataIntegrityError("State-store output must be empty")
    target.mkdir(parents=True, exist_ok=True)
    metadata: dict[str, Any] = {"schema_version": 1, "rows": len(states), "columns": list(states.columns),
                                "dtypes": [str(states[c].dtype) for c in states], "chunks": []}
    for index, batch in enumerate(iter_state_batches(states, batch_rows)):
        name = f"states-{index:05d}.npz"
        arrays = {f"c{i:03d}": batch[c].to_numpy(dtype=str) if batch[c].dtype == object else batch[c].to_numpy()
                  for i, c in enumerate(batch.columns)}
        if any(array.dtype.kind not in "iufUSb" for array in arrays.values()):
            raise DataIntegrityError("State store supports only numeric/string normalized columns")
        np.savez_compressed(target / name, **arrays)
        metadata["chunks"].append({"path": name, "rows": len(batch), "sha256": sha256_file(target / name)})
    (target / "manifest.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return metadata


def read_state_store(directory: str | Path) -> pd.DataFrame:
    source = Path(directory)
    metadata = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if metadata.get("schema_version") != 1 or metadata.get("columns") != NORMALIZED_COLUMNS:
        raise DataIntegrityError("Unexpected local state-store schema")
    frames = []
    for item in metadata["chunks"]:
        path = _local_path(source, item["path"])
        if sha256_file(path) != item["sha256"]:
            raise DataIntegrityError("State-store chunk checksum mismatch")
        with np.load(path, allow_pickle=False) as archive:
            frame = pd.DataFrame({c: archive[f"c{i:03d}"] for i, c in enumerate(metadata["columns"])})
        if len(frame) != item["rows"]:
            raise DataIntegrityError("State-store chunk row count mismatch")
        for column, dtype in zip(metadata["columns"], metadata["dtypes"]):
            if dtype not in ("int64", "float64", "object"):
                raise DataIntegrityError("Unexpected normalized dtype")
            frame[column] = frame[column].astype(dtype)
        frames.append(frame)
    result = pd.concat(frames, ignore_index=True)
    if len(result) != metadata["rows"]:
        raise DataIntegrityError("State-store total row count mismatch")
    validate_states(result)
    return result
