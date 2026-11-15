import sqlite3
from types import SimpleNamespace
import pytest
from golden_agent.runtime.autonomic_healer import KaiUniversalHealer

def test_healer_battery_and_db_lifecycle(tmp_path):
    db_file = tmp_path / "kai_ledger.db"
    vault = tmp_path / "vault_backups"
    battery = SimpleNamespace(health_percent=72.0, healed=False)
    battery.self_heal = lambda: setattr(battery, "healed", True) or setattr(battery, "health_percent", 98.0)

    healer = KaiUniversalHealer(battery_core=battery, db_path=str(db_file), vault_dir=str(vault))
    assert healer._heal_memory_ledger() == "NO_DB_FOUND"

    with sqlite3.connect(db_file) as conn:
        conn.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO events (name) VALUES ('boot')")

    report = healer.run_healing_pulse()
    assert "REBALANCED_AND_HEALED" in report["battery"]
    assert battery.healed is True
    assert report["database"] == "VERIFIED_AND_BACKED_UP"
    assert report["homeostasis"] == "OPTIMAL"

    # Simulate DB corruption and verify auto-restore from vault
    db_file.write_bytes(b"corrupted-header-bytes")
    restored = healer._heal_memory_ledger()
    assert restored.startswith("HEALED_FROM_VAULT")

    with sqlite3.connect(db_file) as conn:
        assert conn.execute("SELECT name FROM events").fetchone()[0] == "boot"

def test_healer_guard_execution_retry(tmp_path):
    battery = SimpleNamespace(health_percent=99.0)
    healer = KaiUniversalHealer(battery_core=battery, db_path=str(tmp_path / "none.db"), vault_dir=str(tmp_path / "v"))
    attempts = []

    def flaky_task(val):
        attempts.append(val)
        if len(attempts) == 1:
            raise RuntimeError("transient glitch")
        return f"recovered:{val}"

    assert healer.guard_execution("somatic_core", flaky_task, "ok") == "recovered:ok"
    assert len(attempts) == 2
