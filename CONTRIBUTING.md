# Contributing to Golden-Agent

Thanks for helping make edge-native multi-agent orchestration faster and lighter!

## Development Setup
```bash
git clone https://github.com
cd Golden-Agent
pip install -e .
pytest
```

## Contribution Guidelines
1. Keep core dependencies lightweight so Golden-Agent continues running cleanly on **ARM64 / Termux** and low-RAM Linux systems.
2. Add unit tests under `tests/unit/` for any new router, AST parser, or sandbox feature.
3. Ensure `pytest` passes completely before opening a Pull Request.
