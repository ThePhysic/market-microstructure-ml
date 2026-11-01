"""Content-addressed extension evidence and output-independent evaluation guard."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..manifests import code_provenance, digest, environment_provenance, sha256_file, write_json
from .config import protocol_identity


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def source_identity(root: Path | None = None) -> dict[str, Any]:
    """Bind old and new executable sources, build files and actual runtime."""
    code = code_provenance(root or project_root())
    environment = environment_provenance()
    return {"code": code, "environment": environment,
            "identity": digest({"source": code["source_sha256"], "build": code["build_sha256"],
                                "python": environment["python"], "packages": environment["packages"]})}


def dataset_identity(manifests: list[dict[str, Any]]) -> str:
    return digest([{
        key: item[key] for key in ("date", "exchange", "symbol", "market_type", "base_currency", "quote_currency", "price_unit", "size_unit", "compressed_sha256", "excerpt_sha256", "selection", "source_row_ranges", "source_total_rows", "retained_rows")
    } for item in sorted(manifests, key=lambda value: value["date"])])


def load_source_lock(path: str | Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    sources = document.get("sources") if isinstance(document, dict) else None
    if not isinstance(sources, list) or sorted(item.get("date", "") for item in sources) != config["data"]["dates"]:
        raise ValueError("Source lock must cover exactly the frozen acquisition dates")
    if len({item["date"] for item in sources}) != len(sources):
        raise ValueError("Source lock contains duplicate dates")
    for item in sources:
        if (item.get("exchange"), item.get("symbol"), item.get("market_type")) != ("bitstamp", "BTCUSD", "spot"):
            raise ValueError("Source lock market differs from the reviewed spot instrument")
        selection = item.get("selection", {})
        if selection.get("window_starts_utc_seconds") != config["data"]["windows_seconds"] or selection.get("window_seconds") != config["data"]["window_seconds"]:
            raise ValueError("Source selection differs from the frozen configuration")
    return sources


def make_freeze(config: dict[str, Any], manifests: list[dict[str, Any]], pilot: dict[str, Any],
                pilot_path: str | Path, review_path: str | Path) -> dict[str, Any]:
    review = json.loads(Path(review_path).read_text(encoding="utf-8"))
    source = source_identity()
    if review.get("status") != "PASS" or review.get("remaining_complaints") != []:
        raise ValueError("A clean independent pre-empirical review is required")
    reviewer = review.get("reviewer", {})
    if reviewer.get("model") != "gpt-6-astra" or reviewer.get("reasoning_effort") != "medium":
        raise ValueError("The specified Astra medium reviewer is required")
    if review.get("source_identity") != source["identity"]:
        raise ValueError("Pre-empirical review does not cover current source/build/runtime")
    if pilot.get("source_identity") != source["identity"] or pilot.get("protocol_identity") != protocol_identity(config) or pilot.get("dataset_identity") != dataset_identity(manifests):
        raise ValueError("Pilot/source/config/data mismatch: rerun development-only planning")
    if not pilot.get("coverage", {}).get("eligible"):
        raise ValueError("Objective historical coverage did not pass")
    return {"schema_version": 1, "protocol_identity": protocol_identity(config),
            "dataset_identity": dataset_identity(manifests), "source_identity": source["identity"],
            "frozen_source_revision": source["code"]["revision"], "source": source,
            "pilot_sha256": sha256_file(pilot_path), "review_sha256": sha256_file(review_path),
            "precision_plan": pilot["research"]["precision_plan"],
            "final_dates": config["research"]["final_dates"],
            "policy": "Fixed prequential schedule; no settings or scenario selection from final scores."}


def verify_freeze(freeze: dict[str, Any], config: dict[str, Any], manifests: list[dict[str, Any]]) -> dict[str, Any]:
    source = source_identity()
    if freeze.get("protocol_identity") != protocol_identity(config) or freeze.get("dataset_identity") != dataset_identity(manifests):
        raise ValueError("Frozen protocol or input data changed")
    if freeze.get("source_identity") != source["identity"]:
        raise ValueError("Executable source, build or runtime changed after freeze")
    if freeze.get("final_dates") != config["research"]["final_dates"]:
        raise ValueError("Frozen final dates changed")
    return source


def register_evaluation(freeze: dict[str, Any], *, root: Path | None = None, reproduction: bool = False) -> dict[str, Any]:
    """Bind consumed final dates to one scientific identity, across output paths.

    This is a local accidental-tuning guard, not tamper-proof global enforcement.
    A fresh clone may reproduce unchanged decisions with independently acquired data.
    """
    destination = (root or project_root()) / "artifacts" / "extension" / "holdout-registry.json"
    registry = json.loads(destination.read_text(encoding="utf-8")) if destination.exists() else {}
    key = digest({"market": "bitstamp:BTCUSD", "dates": freeze["final_dates"]})
    contract = {name: freeze[name] for name in ("protocol_identity", "dataset_identity", "source_identity")}
    existing = registry.get(key)
    if existing is not None and existing["contract"] != contract:
        raise ValueError("These final dates were already bound to different scientific choices")
    if existing is not None and not reproduction:
        raise ValueError("Final evaluation already registered; use reproduce with the frozen reference")
    record = {"contract": contract, "execution_count": (existing or {}).get("execution_count", 0) + 1,
              "reproduction": reproduction, "note": "Registered before fitting; repeats are not independent evidence."}
    registry[key] = record
    write_json(destination, registry)
    return record
