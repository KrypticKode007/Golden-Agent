"""
Benchmark targets for Golden-Agent.

The harness (latency_bench.py) calls a zero-argument function once per
iteration. Wire `tick` below to ONE iteration of your real agent loop.

    python benchmarks/latency_bench.py --target benchmarks.targets:tick

Build expensive objects once at import time, not inside `tick`, so the
benchmark measures the loop step and not the setup.
"""

from __future__ import annotations


# TODO: import and construct your agent once, for example:
#
#     from unified_conscious_agent import <AgentClass>
#     _agent = <AgentClass>()


def tick() -> None:
    """Run exactly one iteration of the agent control loop."""
    raise NotImplementedError(
        "Wire benchmarks/targets.py:tick to one iteration of the agent loop."
    )
