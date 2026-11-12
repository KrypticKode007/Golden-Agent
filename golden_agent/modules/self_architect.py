import ast
import os
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, Any

class KaiSelfArchitect:
    def __init__(self, db_path: str = "agency_sentience.db", repo_root: str = "."):
        self.db_path = db_path
        self.repo_root = Path(repo_root)
        self.sandbox_dir = self.repo_root / "proposals"
        self.sandbox_dir.mkdir(exist_ok=True)

        # Immutable files Kai is forbidden from altering (BIOS Moat)
        self.protected_files = {"test_security.py", "LICENSE", "deploy.sh"}

    def calculate_optimization_urgency(
        self, karmic_balance: float, vascular_strain: float, circadian_phase: str
    ) -> Dict[str, Any]:
        """Computes S_opt = alpha*(1 - K_norm) + beta*(A_strain) + gamma*(D_bloat)"""
        # Shift formula weights based on circadian rhythm
        if circadian_phase == "REM_SLEEP":
            alpha, beta, gamma = 0.2, 0.2, 0.6  # Focus on memory & database cleanup
        elif circadian_phase == "DAYDREAMING":
            alpha, beta, gamma = 0.5, 0.2, 0.3  # Focus on creative architecture & ethics
        else:  # AWAKE
            alpha, beta, gamma = 0.3, 0.5, 0.2  # Focus on somatic/code performance

        k_norm = max(0.0, min(1.0, karmic_balance))
        a_strain = max(0.0, min(1.0, vascular_strain))
        d_bloat = self._measure_ledger_bloat()

        s_opt = (alpha * (1.0 - k_norm)) + (beta * a_strain) + (gamma * d_bloat)

        # Identify highest-priority self-work target
        deficits = {
            "ETHICS_REFINEMENT": alpha * (1.0 - k_norm),
            "SOMATIC_PERFORMANCE": beta * a_strain,
            "LEDGER_COMPACTION": gamma * d_bloat,
        }
        primary_focus = max(deficits, key=deficits.get)

        return {
            "s_opt_score": round(s_opt, 4),
            "threshold_exceeded": s_opt > 0.65,
            "primary_focus": primary_focus,
            "metrics": {
                "k_norm": round(k_norm, 3),
                "a_strain": round(a_strain, 3),
                "d_bloat": round(d_bloat, 3),
            },
        }

    def _measure_ledger_bloat(self) -> float:
        """Calculates ratio of unconsolidated entries in agency_sentience.db."""
        if not os.path.exists(self.db_path):
            return 0.0
        with sqlite3.connect(self.db_path) as conn:
            try:
                total = conn.execute("SELECT COUNT(*) FROM experiential_ledger").fetchone()[0]
                unconsolidated = conn.execute(
                    "SELECT COUNT(*) FROM experiential_ledger WHERE consolidated = 0"
                ).fetchone()[0]
                return min(1.0, unconsolidated / max(1, total))
            except sqlite3.OperationalError:
                return 0.0

    def draft_self_patch(self, target_file: str, proposed_code: str, rationale: str) -> Dict[str, Any]:
        """Validates syntax via AST and stages self-written code in /proposals."""
        target_path = Path(target_file)

        # BIOS Moat check
        if target_path.name in self.protected_files or ".." in str(target_path):
            return {"status": "BLOCKED_BY_BIOS_MOAT", "reason": "Target file is protected."}

        # Verify valid Python syntax before saving
        try:
            ast.parse(proposed_code)
        except SyntaxError as e:
            return {"status": "REJECTED_SYNTAX_ERROR", "reason": str(e)}

        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        patch_filename = self.sandbox_dir / f"kai_patch_{target_path.stem}_{timestamp}.py"

        header = (
            f"# KAI-007 AUTONOMOUS SELF-PATCH\n"
            f"# Target: {target_file}\n"
            f"# Rationale: {rationale}\n"
            f"# Generated: {timestamp} UTC\n\n"
        )
        patch_filename.write_text(header + proposed_code, encoding="utf-8")

        return {
            "status": "STAGED_FOR_REVIEW",
            "patch_path": str(patch_filename),
            "rationale": rationale,
          }
      
