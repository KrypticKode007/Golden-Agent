#!/usr/bin/env bash
#
# Golden-Agent repo cleanup.
#
# Moves documentation and grant/business files into docs/ and grants/,
# untracks the binary zip, and updates .gitignore.
#
# SAFETY:
#   - Dry-run by default. Pass --apply to actually move files.
#   - Python files that are imported or referenced elsewhere are SKIPPED,
#     so tests and launchers do not break.
#   - Core runtime code stays at the repo root.
#
# Usage:
#   ./repo_cleanup.sh            # preview only
#   ./repo_cleanup.sh --apply    # perform the moves

set -euo pipefail

APPLY=0

if [[ "${1:-}" == "--apply" ]]; then
  APPLY=1
fi

run() {
  if [[ $APPLY -eq 1 ]]; then
    "$@"
  else
    echo "[dry-run] $*"
  fi
}

# Documentation -> docs/
DOC_FILES=(
  "DOCS_COMMERCIALIZATION.md"
  "DOCS_GRANT_STRATEGY.md"
  "DOCS_GRANT_BUDGET.md"
  "dual_use_commercialization_plan.md"
  "phase_i_technical_milestones.md"
  "quantified_performance_metrics.md"
  "project_abstract.pdf"
)

# Grant and business tooling -> grants/
GRANT_FILES=(
  "budget_calculator.py"
  "generate_grant_proposal.py"
  "generate_llc12_manifest.py"
  "kryptic_pitch_deck_generator.py"
  "integrated_staging_playbook.py"
  "sync_grant_assets.sh"
  "push_strategy_assets.sh"
)

# Is this file referenced by any other tracked file (by name or module name)?
is_referenced() {
  local file="$1"
  local module="${file%.*}"

  git grep -lE "(^|[^A-Za-z0-9_])(${module}|${file})([^A-Za-z0-9_]|$)" \
    -- ':!*.md' ':!*.pdf' ':!*.zip' 2>/dev/null \
    | grep -vx "$file" >/dev/null
}

move_file() {
  local file="$1"
  local dest="$2"

  if [[ ! -e "$file" ]]; then
    echo "[skip] $file (not found)"
    return
  fi

  if [[ "$file" == *.py || "$file" == *.sh ]]; then
    if is_referenced "$file"; then
      echo "[skip] $file (referenced by other files; move manually after updating imports)"
      return
    fi
  fi

  mkdir -p "$dest"

  run git mv "$file" "$dest/$file"
}

echo "== Moving documentation to docs/ =="

for f in "${DOC_FILES[@]}"; do
  move_file "$f" "docs"
done

echo
echo "== Moving grant tooling to grants/ =="

for f in "${GRANT_FILES[@]}"; do
  move_file "$f" "grants"
done

echo
echo "== Untracking binary archives =="

while IFS= read -r zipfile; do
  [[ -z "$zipfile" ]] && continue

  run git rm --cached "$zipfile"
done < <(git ls-files '*.zip')

echo
echo "== Updating .gitignore =="

IGNORE_LINES=(
  "*.zip"
  "benchmarks/results/"
  ".venv/"
  "__pycache__/"
  "*.pyc"
  ".env"
)

for line in "${IGNORE_LINES[@]}"; do
  if ! grep -qxF "$line" .gitignore 2>/dev/null; then
    if [[ $APPLY -eq 1 ]]; then
      echo "$line" >> .gitignore
    else
      echo "[dry-run] add '$line' to .gitignore"
    fi
  fi
done

echo
if [[ $APPLY -eq 1 ]]; then
  echo "Done. Next steps:"
  echo "  1. Update README links that pointed at moved files (now under docs/ and grants/)."
  echo "  2. Run: pytest"
  echo "  3. Commit: git commit -m 'Reorganize docs and grant tooling'"
else
  echo "Preview complete. Re-run with --apply to perform these changes."
fi
