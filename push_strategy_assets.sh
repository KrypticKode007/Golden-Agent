#!/usr/bin/env bash
# ==============================================================================
# NAME: push_strategy_assets.sh
# PURPOSE: Automated staging, tracking verification, and secure remote push
#          macro for newly updated commercial funding assets.
# ==============================================================================

set -euo pipefail

TARGET_BRANCH="commercial/strategy-funding"

print_status() {
    echo -e "\033[1;32m[+]\033[0m $1"
}

print_warn() {
    echo -e "\033[1;33m[!]\033[0m $1"
}

# 1. Traversal & Repository Validation
if [ ! -d ".github" ] && [ ! -f "requirements.txt" ]; then
    echo "[-] Error: Distribution macro must be executed from the root layout of the repository." >&2
    exit 1
fi

# Ensure branch alignment is structurally accurate
current_branch=$(git branch --show-current 2>/dev/null || echo "detached")
if [ "$current_branch" != "$TARGET_BRANCH" ]; then
    print_warn "Current active path is '$current_branch'. Realigning local context to '$TARGET_BRANCH'..."
    git checkout "$TARGET_BRANCH"
fi

# 2. Local File Presence Verification (Updated Asset Matrix)
print_status "Validating strategic funding assets tracking status..."
declare -a core_assets=(
    "requirements.txt"
    "commercial/strategy/dual_use_commercialization_plan.md"
    "commercial/strategy/quantified_performance_metrics.md"
    "commercial/strategy/phase_i_technical_milestones.md"
    "commercial/strategy/project_abstract.md"
    "commercial/strategy/budget_calculator.py"
    "commercial/strategy/generate_grant_proposal.py"
    "generate_abstract.py"
    "scripts/audit_environment.py"
    "tests/test_grant_milestones.py"
    ".github/workflows/grant_ci.yml"
)

for asset in "${core_assets[@]}"; do
    if [ -f "$asset" ]; then
        print_status "    Found compiled asset: $asset"
        git add "$asset"
    else
        print_warn "    Missing optional target file: $asset (skipping staging step)"
    fi
done

# 3. Code Quality Interception (Pre-Commit Cleanliness Check)
print_status "Running standard compilation checks on core automation python engines..."
if [ -f "commercial/strategy/budget_calculator.py" ]; then
    python3 -m py_compile commercial/strategy/budget_calculator.py
fi
if [ -f "commercial/strategy/generate_grant_proposal.py" ]; then
    python3 -m py_compile commercial/strategy/generate_grant_proposal.py
fi
if [ -f "generate_abstract.py" ]; then
    python3 -m py_compile generate_abstract.py
fi
if [ -f "scripts/audit_environment.py" ]; then
    python3 -m py_compile scripts/audit_environment.py
fi

# 4. Commit and Distribution Isolation
if git diff --cached --quiet; then
    print_warn "No modified strategy files detected in staging area. Execution complete."
    exit 0
fi

print_status "Staging signed commit snapshot..."
git commit -m "feat(commercial): integrate core requirements manifest, diagnostic audit tools, and project abstract tracking matrices"

print_status "Pushing synchronized assets securely to remote tracking origin: $TARGET_BRANCH"
git push origin "$TARGET_BRANCH"

print_status "Distribution sequence completed successfully. All strategy metrics are now live on GitHub."
