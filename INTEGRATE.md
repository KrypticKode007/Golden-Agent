# Integrating this framework into Golden-Agent

This folder is an overlay. It adds new files and does not replace your
existing source code.

```bash
# 1. Clone your repository
git clone https://github.com/KrypticKode007/Golden-Agent.git

cd Golden-Agent

git checkout -b grant-readiness

# 2. Copy the overlay on top (does not delete anything)
cp -r /path/to/Golden-Agent-framework/. .

# 3. Preview the reorganization, then apply it
chmod +x repo_cleanup.sh

./repo_cleanup.sh

./repo_cleanup.sh --apply

# 4. Verify nothing broke
pip install -r requirements.txt

pytest

# 5. Wire the benchmark target (edit benchmarks/targets.py), then run it
python benchmarks/latency_bench.py --target benchmarks.targets:tick

# 6. Commit and open a pull request
git add -A

git commit -m "Add benchmarks, CI, security policy, docs index, and grant roadmap"

git push -u origin grant-readiness
```

If you already have a `.gitignore`, `README.md`, or `SECURITY.md`, compare
before overwriting (`cp -i` prompts first).
