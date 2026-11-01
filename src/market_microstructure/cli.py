"""Explicit, offline-first CLI. Network acquisition is a separate opt-in command."""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import sys
from typing import Any

from .config import ResearchConfig, config_from_dict, load_config
from .manifests import canonical_bytes, code_provenance, digest, environment_provenance, frame_digest, sha256_file, write_json


def _data_contract(config: ResearchConfig) -> dict[str, Any]:
    return {
        "exchange": config.exchange, "symbol": config.symbol, "data_type": config.data_type,
        "dates": list(config.dates), "rows_per_date": config.rows_per_date,
        "max_compressed_bytes_per_date": config.max_compressed_bytes_per_date,
    }


def _check_source_lock(config: ResearchConfig, manifests: list[dict[str, Any]], path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"Missing source lock {path}; run the explicit fetch command first")
    lock = json.loads(path.read_text(encoding="utf-8"))
    if lock.get("schema_version") != 1 or lock.get("data_contract") != _data_contract(config):
        raise ValueError("Source lock does not match the declared data acquisition contract")
    fields = ("date", "path", "sha256", "excerpt_sha256", "compressed_sha256", "retained_rows", "synthetic")
    identity = lambda entries: [
        {key: item.get(key) for key in fields}
        for item in sorted(entries, key=lambda item: item["date"])
    ]
    if identity(lock.get("sources", [])) != identity(manifests):
        raise ValueError("Downloaded source content differs from the pinned source lock")


def load_sources(
    raw_dir: str | Path, config: ResearchConfig, *, source_lock: str | Path | None,
) -> tuple[list[Path], list[dict[str, Any]]]:
    raw = Path(raw_dir).resolve()
    combined = raw / "manifest.json"
    if not combined.is_file():
        raise ValueError(f"No source manifest in {raw}; use fetch or demo first")
    manifests = json.loads(combined.read_text(encoding="utf-8"))
    if not isinstance(manifests, list) or not all(isinstance(item, dict) for item in manifests):
        raise ValueError("Source manifest must be a list of source objects")
    if sorted(item.get("date", "") for item in manifests) != list(config.dates):
        raise ValueError("Manifest dates must exactly match the research configuration")
    paths = []
    for manifest in manifests:
        for key, checksum in (("path", "sha256"), ("prefix_path", "compressed_sha256")):
            name = manifest.get(key)
            if name is None and key == "prefix_path":
                continue
            if not isinstance(name, str) or "/" in name or "\\" in name or Path(name).name != name:
                raise ValueError("Source paths must be safe relative basenames")
            path = (raw / name).resolve()
            if path.parent != raw or not path.is_file():
                raise ValueError(f"Source file missing or outside raw directory: {name}")
            expected = manifest.get(checksum)
            if not isinstance(expected, str) or sha256_file(path) != expected:
                raise ValueError(f"Source checksum verification failed: {name}")
            if key == "path":
                paths.append(path)
    if source_lock is not None:
        _check_source_lock(config, manifests, Path(source_lock))
    return paths, manifests


def _fetch(args: argparse.Namespace, config: ResearchConfig) -> dict[str, Any]:
    from .acquisition import download_many
    source_lock = Path(args.source_lock)
    if source_lock.exists():
        lock = json.loads(source_lock.read_text(encoding="utf-8"))
        if lock.get("data_contract") != _data_contract(config):
            raise ValueError("Existing source lock uses different acquisition settings; refusing to replace it")
    manifests = download_many(
        config.dates, args.raw_dir, exchange=config.exchange, symbol=config.symbol,
        max_compressed_bytes=config.max_compressed_bytes_per_date,
        max_rows=config.rows_per_date, max_total_compressed_bytes=config.max_total_transfer_bytes,
    )
    write_json(Path(args.raw_dir) / "manifest.json", manifests)
    if source_lock.exists():
        _check_source_lock(config, manifests, source_lock)
    else:
        write_json(source_lock, {
            "schema_version": 1, "data_contract": _data_contract(config), "sources": manifests,
            "licence": "Raw/processed rows and trained models remain local. Only non-reconstructible aggregates are shared.",
        })
    return {
        "status": "verified", "source_dates": len(manifests),
        "retained_rows": sum(item["retained_rows"] for item in manifests),
        "bytes_in_local_prefixes": sum(item["bytes_received"] for item in manifests),
        "source_lock": str(source_lock),
    }


def _ingest(args: argparse.Namespace, config: ResearchConfig):
    from .data import ingest_files
    paths, manifests = load_sources(args.raw_dir, config, source_lock=args.source_lock)
    states, quality = ingest_files(
        paths, exchange=config.exchange, symbol=config.symbol, gap_seconds=config.gap_seconds,
        manifests=manifests,
    )
    return states, quality, manifests


def _verify(reference_path: str | Path, raw_dir: str | Path) -> dict[str, Any]:
    from .data import ingest_files
    from .features import build_samples
    from .splits import walk_forward
    reference = json.loads(Path(reference_path).read_text(encoding="utf-8"))
    config = config_from_dict(reference["config"])
    paths, manifests = load_sources(raw_dir, config, source_lock=None)
    from .experiment import _raw_identity
    if digest(_raw_identity(manifests)) != reference["fingerprints"]["raw_sources"]:
        raise ValueError("Raw sources do not match the reference")
    code = code_provenance(Path(__file__).resolve().parents[2])
    if code["source_sha256"] != reference["code"]["source_sha256"]:
        raise ValueError("Executable source differs from the reference; do not claim exact reproduction")
    if code["build_sha256"] != reference["code"]["build_sha256"]:
        raise ValueError("Dependency lock or build configuration differs from the reference")
    environment = environment_provenance()
    for key in ("python", "implementation", "packages"):
        if environment[key] != reference["environment"][key]:
            raise ValueError(f"Reference environment mismatch: {key}")
    states, _ = ingest_files(paths, gap_seconds=config.gap_seconds, manifests=manifests)
    samples, features, _ = build_samples(
        states, horizon_events=config.horizon_events, threshold_ticks=config.threshold_ticks,
        tick_size=config.tick_size, trailing_window=config.trailing_window,
    )
    folds, holdout, _ = walk_forward(
        samples, min_train_dates=config.min_train_dates, holdout_dates=config.holdout_dates,
    )
    actual = {
        "normalized_states": frame_digest(states), "samples": frame_digest(samples),
        "feature_columns": digest(features),
        "split_assignments": digest({"development": [fold.audit for fold in folds], "holdout": holdout.audit}),
    }
    for key, value in actual.items():
        if value != reference["fingerprints"][key]:
            raise ValueError(f"Reference {key} fingerprint mismatch")
    return {"status": "verified", "experiment_id": reference["experiment_id"],
            "platform_match": environment["platform"] == reference["environment"]["platform"], "checks": [
        "source checksums", "executable source", "locked dependencies", "runtime versions",
        "normalized states", "samples", "features", "split assignments",
    ]}


def _metric_projection(result: dict[str, Any]) -> dict[str, Any]:
    sections = {}
    for name, section in {"primary": result["development"], **result["robustness"]}.items():
        sections[name] = {
            "summary": section["summary"], "paired_comparisons": section["paired_comparisons"],
            "fold_metrics": [fold["models"] for fold in section["folds"]],
        }
    return {
        "development_and_robustness": sections, "holdout": result["holdout"]["models"],
        "holdout_by_date": result["holdout"]["by_date"], "conclusion": result["conclusion"],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="microstructure",
        description="Auditable historical order-book research. Use demo offline; fetch is the only network command.",
    )
    parser.add_argument("--version", action="version", version="microstructure 0.1.0")
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("fetch", "ingest", "run"):
        command = subcommands.add_parser(name)
        command.add_argument("--config", default="configs/research.json")
        command.add_argument("--raw-dir", default="data/raw")
        command.add_argument("--source-lock", default="data/sources.lock.json")
        if name != "fetch":
            command.add_argument("--output", default="data/processed" if name == "ingest" else "reports/runs")
    for name in ("verify", "reproduce"):
        command = subcommands.add_parser(name)
        command.add_argument("--reference", required=True)
        command.add_argument("--raw-dir", default="data/raw")
        if name == "reproduce":
            command.add_argument("--output", default="artifacts/reproduction")
    demo = subcommands.add_parser("demo", help="Train/test actual estimators on explicitly synthetic offline data")
    demo.add_argument("--output", default="artifacts/demo")
    demo.add_argument("--rows-per-date", type=int, default=300)
    report = subcommands.add_parser("report")
    report.add_argument("--reference", required=True)
    report.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(variable, "1")
    args = _parser().parse_args(argv)
    try:
        if args.command == "fetch":
            result = _fetch(args, load_config(args.config))
        elif args.command in {"run", "ingest"}:
            config = load_config(args.config)
            states, quality, manifests = _ingest(args, config)
            if args.command == "ingest":
                target = Path(args.output)
                target.mkdir(parents=True, exist_ok=True)
                states.to_csv(target / "normalized-states.csv.gz", index=False, compression="gzip")
                write_json(target / "quality.json", quality)
                result = {"status": "ingested", "retained_states": len(states), "output": str(target)}
            else:
                from .experiment import run_experiment
                result = run_experiment(
                    states, config=config, source_manifests=manifests, ingestion_quality=quality,
                    output_dir=args.output, progress=lambda text: print(text, file=sys.stderr),
                )
                result = {"status": "complete", "experiment_id": result["experiment_id"],
                          "report": str(Path(args.output) / result["experiment_id"] / "report.html"),
                          "conclusion": result["conclusion"]}
        elif args.command == "demo":
            from .data import ingest_files
            from .experiment import run_experiment
            from .synthetic import generate_fixture
            config = ResearchConfig(
                dates=tuple(f"2020-{month:02d}-01" for month in range(1, 9)),
                rows_per_date=args.rows_per_date,
            )
            raw = Path(args.output) / "synthetic-raw"
            manifests = generate_fixture(raw, dates=config.dates, rows_per_date=config.rows_per_date, seed=config.seed)
            states, quality = ingest_files([raw / item["path"] for item in manifests], manifests=manifests)
            result = run_experiment(
                states, config=config, source_manifests=manifests, ingestion_quality=quality,
                output_dir=Path(args.output) / "runs", progress=lambda text: print(text, file=sys.stderr),
            )
            result = {"status": "synthetic-demo-complete", "experiment_id": result["experiment_id"],
                      "report": str(Path(args.output) / "runs" / result["experiment_id"] / "report.html")}
        elif args.command == "verify":
            result = _verify(args.reference, args.raw_dir)
        elif args.command == "reproduce":
            _verify(args.reference, args.raw_dir)
            reference = json.loads(Path(args.reference).read_text(encoding="utf-8"))
            config = config_from_dict(reference["config"])
            from .data import ingest_files
            from .experiment import run_experiment
            paths, manifests = load_sources(args.raw_dir, config, source_lock=None)
            states, quality = ingest_files(paths, gap_seconds=config.gap_seconds, manifests=manifests)
            repeated = run_experiment(
                states, config=config, source_manifests=manifests, ingestion_quality=quality,
                output_dir=args.output, force_reproduction=True,
                progress=lambda text: print(text, file=sys.stderr),
            )
            if canonical_bytes(_metric_projection(repeated)) != canonical_bytes(_metric_projection(reference)):
                raise ValueError("Frozen reproduction did not exactly match reference metrics")
            result = {"status": "reproduced", "experiment_id": repeated["experiment_id"],
                      "metric_comparison": "exact match", "reference": args.reference}
        elif args.command == "report":
            from .reporting import write_reports
            reference = json.loads(Path(args.reference).read_text(encoding="utf-8"))
            target = Path(args.output)
            if target.exists() and any(target.iterdir()):
                raise ValueError("Report output must be empty to avoid overwriting existing evidence")
            result = {"status": "rendered", "files": write_reports(reference, target)}
        else:
            raise AssertionError("Unhandled command")
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
