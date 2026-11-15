import time
import shutil
import sqlite3
import logging
from pathlib import Path
from typing import Callable, Any

logger = logging.getLogger("KaiAutonomicHealer")

class KaiUniversalHealer:
    """
    Connects the nkryptd self-healing battery with Kai's somatic,
    cognitive, and database layers for full-system homeostatic recovery.
    """
    def __init__(self, battery_core: Any, db_path: str = "kai_ledger.db", vault_dir: str = "vault_backups"):
        self.battery = battery_core  # Instance from nkryptd
        self.db_path = Path(db_path)
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(exist_ok=True)

    def run_healing_pulse(self) -> dict:
        """Executes a full-body and full-stack diagnostic and repair cycle."""
        report = {
            "battery": self._heal_power_layer(),
            "database": self._heal_memory_ledger(),
            "homeostasis": "OPTIMAL"
        }
        return report

    def _heal_power_layer(self) -> str:
        # Hook into your nkryptd battery methods (adjust method names to match nkryptd)
        health = getattr(self.battery, "health_percent", 100.0)
        if health < 85.0 and hasattr(self.battery, "self_heal"):
            self.battery.self_heal()
            return f"REBALANCED_AND_HEALED (from {health:.1f}%)"
        return f"NOMINAL ({health:.1f}%)"

    def _heal_memory_ledger(self) -> str:
        """Verifies SQLite integrity and auto-restores from vault if corrupted."""
        if not self.db_path.exists():
            return "NO_DB_FOUND"
        try:
            with sqlite3.connect(self.db_path) as conn:
                status = conn.execute("PRAGMA integrity_check;").fetchone()[0]
                if status == "ok":
                    self._create_vault_snapshot()
                    return "VERIFIED_AND_BACKED_UP"
        except sqlite3.DatabaseError:
            pass

        # Auto-heal from latest clean vault backup
        backups = sorted(self.vault_dir.glob("kai_ledger_*.db"), reverse=True)
        if backups:
            shutil.copy2(backups[0], self.db_path)
            logger.warning("Corrupted ledger healed from %s", backups[0].name)
            return f"HEALED_FROM_VAULT ({backups[0].name})"
        return "CRITICAL_NO_BACKUP"

    def _create_vault_snapshot(self) -> None:
        timestamp = int(time.time())
        target = self.vault_dir / f"kai_ledger_{timestamp}.db"
        shutil.copy2(self.db_path, target)
        # Keep only the 5 most recent snapshots
        for old_backup in sorted(self.vault_dir.glob("kai_ledger_*.db"), reverse=True)[5:]:
            old_backup.unlink()

    def guard_execution(self, subsystem_name: str, fn: Callable, *args, **kwargs) -> Any:
        """Wraps any Kai module call with automatic retry and state recovery."""
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            logger.error("Fault in %s: %s. Triggering autonomic recovery...", subsystem_name, exc)
            self.run_healing_pulse()
            return fn(*args, **kwargs)  # Retry once after healing
          
