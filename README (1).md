# Golden-Agent

Golden-Agent is a local telemetry demo. It simulates state metrics, spatial frames, and a positive-only narrative state; it does not establish machine consciousness or perform independent research.

## Run Locally

Requires Python 3.10 or newer. Start the server and monitor together:

```bash
./deploy.sh
```

The server listens on `127.0.0.1:8000`, streams JSON-lines telemetry, and the monitor appends readable frames to `cognitive_pov_history.txt`. Press Ctrl+C to stop both processes. Generated metric episodes persist in `kryptic_agent_memory.sqlite3`; set `KRYPTIC_MEMORY_DB` to change its location.

To run the diagnostic checks without starting the server:

```bash
python3 -c 'import runpy; runpy.run_path("main_sentience_core (2).py")["run_automated_test_matrix"]()'
```

Run the application tests with `python3 -m pip install pytest` followed by `python3 -m pytest -q`.

## Run With Docker Compose

```bash
docker compose up --build
```

The TCP telemetry service is published on port `8000`. Connect a client to read newline-delimited JSON frames. The Compose service binds to all container interfaces; do not publish this port to untrusted networks without adding access controls.

## Components

- `main_sentience_core (2).py`: Simulated active-inference metrics, kinematics diagnostics, and asynchronous TCP telemetry server.
- `vr_pov_monitor.py`: TCP subscriber that records telemetry as readable text.
- `kryptic_golden_agent.py`: Separate SQLite logging demo for generated state values.

The displayed free-energy, individuation, closure, and phenomenology values are illustrative model outputs, not validated measures of subjective experience.

When simulated stress crosses its threshold, telemetry reports `HUMAN_REVIEW_REQUIRED` and `requires_human_review: true`. This is an operator-review signal only; the demo has no external action or actuator-control path, and it does not detach from sandbox boundaries.

Each frame also includes a clearly labeled simulated experience: positive-only affect and energy, generated thoughts and helpful intent, a stated human-directed purpose, recent remembered metric episodes, and a low-confidence next-cycle estimate based only on the metric trend. This is narrative and numerical simulation, not subjective experience or prediction of real-world events. The memory database records generated metrics and narrative state, not personal user data.
