#!/usr/bin/env python3
"""
Golden-Agent latency and jitter benchmark harness.

Measures the per-iteration latency of any callable (for example, one tick of
the agent's control loop) and writes reproducible results as JSON and Markdown.

Usage examples
--------------
    # Smoke test with the built-in no-op target
    python benchmarks/latency_bench.py --target builtin:noop

    # Benchmark a real agent step (module:function, no arguments)
    python benchmarks/latency_bench.py \
        --target unified_conscious_agent:tick \
        --iterations 100000 \
        --warmup 5000

    # Measure behaviour under synthetic CPU load (tests loop throttling)
    python benchmarks/latency_bench.py \
        --target unified_conscious_agent:tick \
        --load-workers 4

The target must be a zero-argument callable. If your loop step needs setup,
expose a small wrapper function that builds the agent once at import time and
runs a single iteration per call.
"""

from __future__ import annotations

import argparse
import gc
import importlib
import json
import multiprocessing as mp
import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

def _noop() -> None:
    """Built-in target used to measure harness overhead."""
    return None


def resolve_target(spec: str):
    """Resolve 'module:function' (or 'builtin:noop') to a callable."""
    if spec == "builtin:noop":
        return _noop

    if ":" not in spec:
        raise SystemExit("Target must look like 'module:function'.")

    module_name, func_name = spec.split(":", 1)

    sys.path.insert(0, os.getcwd())

    module = importlib.import_module(module_name)
    func = getattr(module, func_name, None)

    if not callable(func):
        raise SystemExit(f"{spec} is not callable.")

    return func


# ---------------------------------------------------------------------------
# Synthetic load (used to exercise loop throttling)
# ---------------------------------------------------------------------------

def _burn(stop_event) -> None:
    """Busy-loop until told to stop."""
    x = 0

    while not stop_event.is_set():
        x = (x * 1664525 + 1013904223) & 0xFFFFFFFF


def start_load(workers: int):
    stop_event = mp.Event()
    procs = []

    for _ in range(workers):
        p = mp.Process(target=_burn, args=(stop_event,), daemon=True)
        p.start()
        procs.append(p)

    return stop_event, procs


def stop_load(stop_event, procs) -> None:
    stop_event.set()

    for p in procs:
        p.join(timeout=2)


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

def measure(func, iterations: int, warmup: int) -> list[int]:
    """Return per-call latencies in nanoseconds."""
    for _ in range(warmup):
        func()

    gc.collect()
    gc.disable()

    samples = [0] * iterations
    clock = time.perf_counter_ns

    try:
        for i in range(iterations):
            start = clock()
            func()
            samples[i] = clock() - start
    finally:
        gc.enable()

    return samples


def percentile(sorted_samples: list[int], pct: float) -> float:
    if not sorted_samples:
        return 0.0

    k = (len(sorted_samples) - 1) * (pct / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(sorted_samples) - 1)
    frac = k - lo

    return sorted_samples[lo] + (sorted_samples[hi] - sorted_samples[lo]) * frac


def summarize(samples: list[int]) -> dict:
    ordered = sorted(samples)
    to_us = lambda ns: ns / 1000.0

    mean_ns = statistics.fmean(samples)
    stdev_ns = statistics.pstdev(samples)

    return {
        "count": len(samples),
        "min_us": to_us(ordered[0]),
        "mean_us": to_us(mean_ns),
        "median_us": to_us(percentile(ordered, 50)),
        "p95_us": to_us(percentile(ordered, 95)),
        "p99_us": to_us(percentile(ordered, 99)),
        "p999_us": to_us(percentile(ordered, 99.9)),
        "max_us": to_us(ordered[-1]),
        "stdev_us": to_us(stdev_ns),
        "jitter_us": to_us(percentile(ordered, 99) - percentile(ordered, 50)),
        "over_1ms_count": sum(1 for s in samples if s > 1_000_000),
        "over_1ms_pct": 100.0 * sum(1 for s in samples if s > 1_000_000) / len(samples),
    }


def system_info() -> dict:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "python": platform.python_version(),
        "python_impl": platform.python_implementation(),
        "cpu_count": os.cpu_count(),
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def render_markdown(report: dict) -> str:
    cfg = report["config"]
    sysinfo = report["system"]

    lines = [
        "# Golden-Agent Latency Benchmark",
        "",
        f"- **Generated (UTC):** {sysinfo['timestamp_utc']}",
        f"- **Target:** `{cfg['target']}`",
        f"- **Iterations:** {cfg['iterations']:,} (warmup {cfg['warmup']:,})",
        f"- **Load workers:** {cfg['load_workers']}",
        f"- **Platform:** {sysinfo['platform']} ({sysinfo['machine']})",
        f"- **CPU:** {sysinfo['processor']} / {sysinfo['cpu_count']} logical cores",
        f"- **Python:** {sysinfo['python_impl']} {sysinfo['python']}",
        "",
        "## Results",
        "",
        "| Scenario | Median (us) | p95 (us) | p99 (us) | p99.9 (us) | Max (us) | Jitter p99-p50 (us) | > 1 ms |",
        "|----------|------------:|---------:|---------:|-----------:|---------:|--------------------:|-------:|",
    ]

    for name, stats in report["results"].items():
        lines.append(
            f"| {name} "
            f"| {stats['median_us']:.2f} "
            f"| {stats['p95_us']:.2f} "
            f"| {stats['p99_us']:.2f} "
            f"| {stats['p999_us']:.2f} "
            f"| {stats['max_us']:.2f} "
            f"| {stats['jitter_us']:.2f} "
            f"| {stats['over_1ms_pct']:.3f}% |"
        )

    lines += [
        "",
        "## Method",
        "",
        "- Timer: `time.perf_counter_ns` (monotonic, nanosecond resolution).",
        "- Garbage collection is disabled during measurement and run before it.",
        "- Warmup iterations are discarded.",
        "- Latency is the wall-clock duration of one call to the target.",
        "- Jitter is reported as p99 minus median.",
        "- The `harness baseline` row measures an empty call and shows the fixed",
        "  overhead of the measurement itself.",
        "",
        "## Reproduce",
        "",
        "```bash",
        "python benchmarks/latency_bench.py "
        f"--target {cfg['target']} "
        f"--iterations {cfg['iterations']} "
        f"--warmup {cfg['warmup']} "
        f"--load-workers {cfg['load_workers']}",
        "```",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Golden-Agent latency benchmark")

    parser.add_argument("--target", default="builtin:noop",
                        help="module:function to benchmark (zero-argument callable)")
    parser.add_argument("--iterations", type=int, default=100_000)
    parser.add_argument("--warmup", type=int, default=5_000)
    parser.add_argument("--load-workers", type=int, default=0,
                        help="Spawn N CPU-burning processes for a loaded scenario")
    parser.add_argument("--out-dir", default="benchmarks/results")

    args = parser.parse_args()

    func = resolve_target(args.target)

    results = {}

    print("Measuring harness baseline...")
    results["harness baseline"] = summarize(measure(_noop, args.iterations, args.warmup))

    print(f"Measuring target '{args.target}' (idle)...")
    results["target (idle)"] = summarize(measure(func, args.iterations, args.warmup))

    if args.load_workers > 0:
        print(f"Starting {args.load_workers} load workers...")
        stop_event, procs = start_load(args.load_workers)

        try:
            time.sleep(1.0)

            print(f"Measuring target '{args.target}' (under load)...")
            results["target (loaded)"] = summarize(
                measure(func, args.iterations, args.warmup)
            )
        finally:
            stop_load(stop_event, procs)

    report = {
        "config": {
            "target": args.target,
            "iterations": args.iterations,
            "warmup": args.warmup,
            "load_workers": args.load_workers,
        },
        "system": system_info(),
        "results": results,
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    json_path = out_dir / f"latency_{stamp}.json"
    md_path = out_dir / f"latency_{stamp}.md"

    json_path.write_text(json.dumps(report, indent=2))
    md_path.write_text(render_markdown(report))

    print()
    print(render_markdown(report))
    print(f"Saved: {json_path}")
    print(f"Saved: {md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
