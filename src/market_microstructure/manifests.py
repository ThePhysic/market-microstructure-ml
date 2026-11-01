"""Portable hashes, JSON serialization and code provenance."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
from typing import Any


def jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "tolist"):
        return jsonable(value.tolist())
    if hasattr(value, "item"):
        return value.item()
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: str | Path) -> str:
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            result.update(chunk)
    return result.hexdigest()


def write_json(path: str | Path, value: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(
        json.dumps(jsonable(value), indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(destination)


def frame_digest(frame: Any) -> str:
    result = hashlib.sha256()
    result.update(canonical_bytes({"columns": list(frame.columns), "dtypes": list(map(str, frame.dtypes))}))
    for start in range(0, len(frame), 5000):
        text = frame.iloc[start:start + 5000].to_csv(
            index=False, header=start == 0, float_format="%.17g", lineterminator="\n"
        )
        result.update(text.encode("utf-8"))
    return result.hexdigest()


def code_provenance(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root)
    source_root = root / "src"
    source_hashes = {
        str(path.relative_to(root)).replace("\\", "/"): sha256_file(path)
        for path in sorted(source_root.rglob("*.py"))
    }
    scientific_names = {
        "acquisition.py", "config.py", "data.py", "evaluation.py", "experiment.py",
        "features.py", "manifests.py", "models.py", "splits.py",
    }
    scientific_hashes = {
        name: checksum for name, checksum in source_hashes.items()
        if Path(name).name in scientific_names
    }
    build_hashes = {
        name: sha256_file(root / name) if (root / name).is_file() else None
        for name in ("pyproject.toml", "uv.lock", ".python-version")
    }

    def git(*args: str) -> str | None:
        try:
            completed = subprocess.run(
                ["git", *args], cwd=root, capture_output=True, text=True, timeout=10,
                check=False,
            )
            return completed.stdout.strip() if completed.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            return None

    status = git("status", "--porcelain")
    return {
        "revision": git("rev-parse", "HEAD"),
        "dirty_tree": bool(status) if status is not None else True,
        "source_sha256": digest(source_hashes),
        "source_files": source_hashes,
        "scientific_sha256": digest(scientific_hashes),
        "build_files": build_hashes,
        "build_sha256": digest(build_hashes),
        "provenance_note": "Source hashes identify executable code even when report/docs commits follow.",
    }


def environment_provenance() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("numpy", "pandas", "scikit-learn", "scipy")
        },
    }
