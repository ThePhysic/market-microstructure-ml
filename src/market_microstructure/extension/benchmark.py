"""Reproducible replay/simulation scaling and input-batch parity measurements."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

from ..manifests import environment_provenance, write_json


def _native_peak_rss():
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        class MemoryCounters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
        counters = MemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
            raise OSError("Native peak working-set measurement failed")
        return int(counters.PeakWorkingSetSize), "Windows GetProcessMemoryInfo PeakWorkingSetSize"
    import resource
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak*1024), "getrusage process maximum resident set"


def _worker(rows: int, mode: str):
    from .fixtures import synthetic_states
    from .simulation import SimulationConfig, simulate
    states = synthetic_states(["2021-01-01"], rows_per_date=rows)
    signals = [{"source_order": int(row.source_order), "available_time_us": int(row.receive_time_us),
                "feature_cutoff_time_us": int(row.receive_time_us), "train_label_end_time_us": int(row.receive_time_us)-1,
                "target_position": "0.001" if index % 2 == 0 else "0", "model_id": "benchmark"}
               for index, row in enumerate(states.iloc[::10].itertuples(index=False))]
    options = SimulationConfig(initial_cash="10000", max_position="0.001", quantity_step="0.00000001",
                               price_tick="0.01", fee_bps="10", slippage_bps="1", latency_us=100000,
                               max_quote_age_us=5000000, model_id="benchmark", dataset_id="synthetic-benchmark")
    observations = states if mode == "frame" else (states.iloc[start:start+257] for start in range(0, len(states), 257))
    started = time.perf_counter()
    result = simulate(observations, signals, options)
    elapsed = time.perf_counter()-started
    peak, method = _native_peak_rss()
    return {"rows": rows, "mode": mode, "wall_seconds": elapsed, "events_per_second": rows/elapsed,
            "peak_process_rss_bytes": peak, "memory_method": method,
            "input_frame_bytes": int(states.memory_usage(index=True, deep=True).sum()),
            "ledger_sha256": result["ledger_sha256"], "fill_count": result["aggregate"]["fill_count"]}


def benchmark(sizes: list[int], repeats: int, output: str | Path):
    from .provenance import source_identity
    source = source_identity()
    if not sizes or any(type(n) is not int or not 40 <= n <= 100000 for n in sizes) or len(set(sizes)) != len(sizes):
        raise ValueError("Benchmark sizes must be distinct integers in 40-100000")
    if type(repeats) is not int or not 1 <= repeats <= 10:
        raise ValueError("Benchmark repeats must be 1-10")
    records = []
    for size in sizes:
        for mode in ("frame", "batches"):
            for _ in range(repeats):
                child = subprocess.run([sys.executable, "-m", __name__, "--worker", str(size), "--mode", mode],
                                       capture_output=True, text=True, timeout=180, check=False)
                if child.returncode:
                    raise RuntimeError("Benchmark worker failed: "+child.stderr[-1500:])
                records.append(json.loads(child.stdout))
    summary = []
    for size in sizes:
        candidates = [row for row in records if row["rows"] == size]
        if len({row["ledger_sha256"] for row in candidates}) != 1:
            raise ValueError("Frame/batch/repeated simulation results differ")
        for mode in ("frame", "batches"):
            group = [row for row in candidates if row["mode"] == mode]
            summary.append({"rows": size, "mode": mode, "repeats": repeats,
                "median_wall_seconds": statistics.median(row["wall_seconds"] for row in group),
                "maximum_peak_process_rss_bytes": max(row["peak_process_rss_bytes"] for row in group),
                "ledger_sha256": group[0]["ledger_sha256"], "fill_count": group[0]["fill_count"]})
    if source_identity()["identity"] != source["identity"]:
        raise ValueError("Benchmark source changed during measurement")
    result = {"status": "PASS", "kind": "synthetic_performance_benchmark", "environment": environment_provenance(),
              "source_identity": source["identity"], "provenance": source,
              "processor": platform.processor(), "seed": 42, "summary": summary, "measurements": records,
              "limitations": ["Input generation and import time excluded from engine wall time; native peak process memory includes them.",
                              "Frame and batch modes use identical pre-generated input and produce identical ledger hashes.",
                              "Batch mode verifies the replay interface; retained signals/ledger and the input fixture still scale with event count.",
                              "This does not establish a fully out-of-core ML pipeline or exchange latency.",
                              "No C++ acceleration is claimed; optimization requires a measured justified bottleneck."]}
    target = Path(output)
    if (target / "benchmark.json").exists():
        raise ValueError("Benchmark artifact already exists; choose a fresh output")
    write_json(target / "benchmark.json", result)
    return {"status": "PASS", "artifact": str(target / "benchmark.json"), "summary": summary}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=int, required=True)
    parser.add_argument("--mode", choices=("frame", "batches"), required=True)
    args = parser.parse_args()
    print(json.dumps(_worker(args.worker, args.mode), allow_nan=False))
