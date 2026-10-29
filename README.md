# Benchmarks

Reproducible latency and jitter measurements for Golden-Agent.

## Run

```bash
# 1. Sanity check the harness itself
python benchmarks/latency_bench.py --target builtin:noop

# 2. Benchmark the real loop (after wiring benchmarks/targets.py)
python benchmarks/latency_bench.py \
    --target benchmarks.targets:tick \
    --iterations 100000 \
    --warmup 5000

# 3. Measure behavior under CPU load (exercises loop throttling)
python benchmarks/latency_bench.py \
    --target benchmarks.targets:tick \
    --load-workers 4
```

Results are written to `benchmarks/results/` as JSON and Markdown.

## Reporting rules

- Publish p50, p99, and max, never only the average.
- Record the hardware and OS alongside every number.
- Copy final numbers into `docs/quantified_performance_metrics.md`.
