"""Explicit acquisition, planning, frozen evaluation and offline reproduction."""
from __future__ import annotations

import argparse
from copy import deepcopy
import gzip
import json
import os
from pathlib import Path
import sys
from typing import Any

from ..manifests import canonical_bytes, digest, frame_digest, write_json
from .config import load_config, protocol_identity
from .provenance import (dataset_identity, load_source_lock, make_freeze, register_evaluation,
                         source_identity, verify_freeze)

LIMITATIONS = [
    "This is hypothetical execution under declared assumptions, not observed fills or a profitability claim.",
    "Eight selected 15-minute windows on each first-of-month date are not continuous four-year market coverage.",
    "Date blocks and adjacent months are not proven independent or exchangeable; bootstrap conclusions are conditional on the stated dependence model.",
    "Sessions start with equal cash independently. Segment-end inventory is marked at observed bid, not liquidated through unseen data.",
    "Fees/slippage/delays are scenario assumptions, not historical account-specific rates or measured trading-system latency.",
    "Top-five reconstructed snapshots cannot establish queue priority, hidden liquidity, market impact or exchange-realistic fills.",
    "Predictive comparison, hypothetical execution outcome and software acceptance are reported separately.",
    "Historical event data, signals, detailed ledgers and fitted model assets stay local under provider terms.",
]


def _inputs(args, config):
    from .coverage import summarize_coverage
    from .storage import load_states
    sources = load_source_lock(args.source_lock, config)
    states, quality = load_states(sources, args.raw_dir, gap_seconds=config["data"]["gap_seconds"])
    data = config["data"]
    coverage = summarize_coverage(states, sources, windows=data["windows_seconds"], window_seconds=data["window_seconds"],
        min_window_rows=data["minimum_window_states"], min_window_span_seconds=data["minimum_window_span_seconds"],
        max_edge_gap_seconds=data["maximum_window_edge_gap_seconds"], max_excluded_fraction=data["maximum_excluded_fraction"])
    if not coverage["eligible"]:
        raise ValueError("Predeclared date/window coverage failed; no fitting is permitted")
    return states, sources, coverage, quality


def _research_config(config, freeze=None):
    research = deepcopy(config["research"])
    research["protocol_sha256"] = protocol_identity(config)
    research["frozen_source_revision"] = (freeze or {}).get("frozen_source_revision") or source_identity()["code"]["revision"]
    research["stage"] = "final" if freeze else "pilot"
    research["final_scoring_authorized"] = freeze is not None
    if freeze:
        precision = freeze["precision_plan"]
        adequate = precision.get("adequate", precision.get("status") == "adequate")
        research["precision_gate_status"] = "adequate" if adequate else "exploratory_only_acknowledged"
    return research


def _safe_quality(quality):
    return {name: quality.get(name) for name in ("total_rows", "retained_rows", "excluded_rows", "counts", "exclusion_counts", "segments", "price_unit", "size_unit")}


def _local_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", compresslevel=5, mtime=0) as stream:
            stream.write(canonical_bytes(value))


def _execute(config, states, sources, coverage, quality, freeze, output, *, reproduction=False, synthetic=False):
    from .simulation import SimulationConfig, simulate
    from .study import run_study
    from .reporting import write_report
    source = source_identity()
    if not synthetic:
        verify_freeze(freeze, config, sources)
    experiment_id = "ext-" + digest({"protocol": protocol_identity(config), "dataset": dataset_identity(sources) if sources else frame_digest(states), "source": source["identity"], "synthetic": synthetic})[:16]
    destination = Path(output) / experiment_id
    if destination.exists():
        raise ValueError("Immutable experiment already exists; choose a fresh reproduction output")
    if not synthetic:
        usage = register_evaluation(freeze, reproduction=reproduction)
    else:
        usage = {"synthetic": True, "note": "No historical holdout is consumed by this fixture."}
    print("Running fixed chronological research comparisons", file=sys.stderr, flush=True)
    study = run_study(states, _research_config(config, freeze))
    final_states = states.loc[states["session_date"].isin(config["research"]["final_dates"])].reset_index(drop=True)
    final_orders = set(final_states["source_order"])
    local = destination / "local"
    local.mkdir(parents=True, exist_ok=False)
    _local_json(local / "signals.json.gz", study["signals"])
    simulations = {}
    for scenario in config["scenarios"]:
        simulations[scenario["name"]] = {}
        for model, signals in {"no_trade": [], **study["signals"]}.items():
            print(f"Simulating {scenario['name']} / {model}", file=sys.stderr, flush=True)
            options = {**config["simulation"], **{k: scenario[k] for k in ("fee_bps", "slippage_bps", "latency_us")},
                       "dataset_id": dataset_identity(sources) if sources else "synthetic-fixture",
                       "model_id": model, "scenario_id": scenario["name"]}
            # Study returns both development and final signals; execution evaluates
            # only the explicitly reserved final observations.
            orders = [row for row in signals if row["source_order"] in final_orders]
            simulated = simulate(final_states, orders, SimulationConfig(**options))
            _local_json(local / f"{scenario['name']}-{model}.json.gz", simulated)
            simulations[scenario["name"]][model] = {
                "aggregate": simulated["aggregate"], "ledger_sha256": simulated["ledger_sha256"],
                "simulation_sha256": simulated["simulation_sha256"],
                "assumptions": simulated["assumptions"],
                "segments": len(simulated["segments"]),
            }
    result = {"schema_version": 2, "kind": "synthetic_fixture" if synthetic else "real_historical",
              "experiment_id": experiment_id, "config": config, "protocol_identity": protocol_identity(config),
              "dataset_identity": dataset_identity(sources) if sources else frame_digest(states),
              "states_sha256": frame_digest(states), "source_identity": source["identity"],
              "provenance": source, "freeze": freeze, "coverage": coverage, "quality": _safe_quality(quality),
              "research": study["aggregate"], "simulations": simulations,
              "signals_sha256": digest(study["signals"]),
              "replication": {}, "limitations": LIMITATIONS,
              "holdout_usage": usage}
    from .replication import adapt_queue_imbalance
    result["replication"] = adapt_queue_imbalance(states, _research_config(config))
    if source_identity()["identity"] != source["identity"]:
        raise ValueError("Executable sources changed during evaluation; results cannot be finalized")
    write_report(result, destination)
    return result, destination


def metric_projection(document):
    """Exclude operator paths/reproduction count, retain every scientific output."""
    return {key: document[key] for key in ("research", "simulations", "replication", "states_sha256", "signals_sha256", "protocol_identity", "dataset_identity", "source_identity")}


def _parser():
    parser = argparse.ArgumentParser(description="Causal spot research and hypothetical execution. demo is offline; only fetch uses the network.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("fetch", "coverage", "pilot", "freeze", "run", "verify", "reproduce", "demo", "report", "benchmark"):
        command = subcommands.add_parser(name)
        command.add_argument("--config", default="configs/research-extension.json")
        command.add_argument("--raw-dir", default="data/extension/raw")
        command.add_argument("--source-lock", default="data/extension-sources.lock.json")
        if name in {"pilot", "run", "reproduce", "demo", "report", "benchmark"}:
            command.add_argument("--output", default=f"artifacts/extension/{name}")
        if name in {"run"}:
            command.add_argument("--freeze", required=True)
        if name == "freeze":
            command.add_argument("--pilot", required=True)
            command.add_argument("--review", required=True)
            command.add_argument("--output", default="artifacts/extension/freeze.json")
        if name in {"verify", "reproduce", "report"}:
            command.add_argument("--reference", required=True)
        if name == "demo":
            command.add_argument("--rows-per-date", type=int, default=100)
        if name == "benchmark":
            command.add_argument("--sizes", default="1000,10000")
            command.add_argument("--repeats", type=int, default=3)
    return parser


def main(argv=None):
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(key, "1")
    args = _parser().parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "fetch":
            from .acquisition import download_days
            data = config["data"]
            sources = download_days(data["dates"], args.raw_dir, windows=data["windows_seconds"], window_seconds=data["window_seconds"],
                max_total_compressed_bytes=data["max_total_compressed_bytes"], max_disk_bytes=data["max_disk_bytes"], max_wall_seconds=data["max_wall_seconds"],
                max_compressed_bytes=data["max_compressed_bytes_per_date"], max_decompressed_bytes=data["max_decompressed_bytes_per_date"])
            lock_path = Path(args.source_lock)
            if lock_path.exists():
                if dataset_identity(load_source_lock(lock_path, config)) != dataset_identity(sources):
                    raise ValueError("Fetched sources differ from the immutable source lock")
            else:
                write_json(lock_path, {"schema_version": 1, "sources": sources})
            result = {"status": "verified", "dates": len(sources), "source_lock": args.source_lock}
        elif args.command == "freeze":
            pilot = json.loads(Path(args.pilot).read_text(encoding="utf-8"))
            sources = load_source_lock(args.source_lock, config)
            freeze = make_freeze(config, sources, pilot, args.pilot, args.review)
            if Path(args.output).exists():
                raise ValueError("Refusing to overwrite an existing research freeze")
            write_json(args.output, freeze)
            result = {"status": "frozen", "freeze": args.output, "source_identity": freeze["source_identity"]}
        elif args.command == "report":
            from .reporting import write_report
            document = json.loads(Path(args.reference).read_text(encoding="utf-8"))
            if Path(args.output).exists() and any(Path(args.output).iterdir()):
                raise ValueError("Report output must be empty")
            result = {"status": "rendered", **write_report(document, args.output)}
        elif args.command == "benchmark":
            from .benchmark import benchmark
            result = benchmark([int(x) for x in args.sizes.split(",")], args.repeats, args.output)
        elif args.command == "demo":
            from .fixtures import synthetic_states
            states = synthetic_states(config["data"]["dates"], args.rows_per_date)
            freeze = {"frozen_source_revision": source_identity()["code"]["revision"],
                      "precision_plan": {"status": "exploratory", "adequate": False}, "synthetic": True}
            document, path = _execute(config, states, [], {"synthetic": True, "eligible": True}, {}, freeze, args.output, synthetic=True)
            result = {"status": "synthetic-demo-complete", "experiment_id": document["experiment_id"], "report": str(path / "report.html")}
        else:
            states, sources, coverage, quality = _inputs(args, config)
            if args.command == "coverage":
                result = {"status": "eligible", **coverage}
            elif args.command == "pilot":
                from .study import run_study
                from .reporting import write_report
                source = source_identity()
                study = run_study(states, _research_config(config))
                result = {"schema_version": 2, "kind": "real_historical", "stage": "development-only", "experiment_id": "pilot-"+digest({"protocol": protocol_identity(config), "source": source["identity"], "data": dataset_identity(sources)})[:16],
                          "protocol_identity": protocol_identity(config), "dataset_identity": dataset_identity(sources),
                          "source_identity": source["identity"], "provenance": source, "coverage": coverage,
                          "research": study["aggregate"], "config": config, "limitations": LIMITATIONS}
                target = Path(args.output) / result["experiment_id"]
                if target.exists():
                    raise ValueError("Pilot artifact exists; choose a fresh output")
                write_report(result, target)
                result = {"status": "pilot-complete", "artifact": str(target / "experiment.json"), "precision_plan": study["aggregate"]["precision_plan"]}
            elif args.command in {"verify", "reproduce"}:
                reference = json.loads(Path(args.reference).read_text(encoding="utf-8"))
                verify_freeze(reference["freeze"], config, sources)
                if reference["states_sha256"] != frame_digest(states):
                    raise ValueError("Normalized observations differ from the reference")
                if args.command == "verify":
                    result = {"status": "verified", "experiment_id": reference["experiment_id"], "checks": ["raw checksums", "selection", "coverage", "normalized states", "source/build/runtime", "protocol"]}
                else:
                    repeated, destination = _execute(config, states, sources, coverage, quality, reference["freeze"], args.output, reproduction=True)
                    if canonical_bytes(metric_projection(repeated)) != canonical_bytes(metric_projection(reference)):
                        raise ValueError("Frozen numerical/ledger reproduction did not exactly match")
                    result = {"status": "reproduced", "comparison": "exact canonical match", "report": str(destination / "report.html")}
            elif args.command == "run":
                freeze = json.loads(Path(args.freeze).read_text(encoding="utf-8"))
                document, target = _execute(config, states, sources, coverage, quality, freeze, args.output)
                result = {"status": "complete", "experiment_id": document["experiment_id"], "report": str(target / "report.html")}
            else:
                raise AssertionError("Unhandled command")
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, RuntimeError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
