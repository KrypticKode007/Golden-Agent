import sqlite3
import psutil
from datetime import datetime

class BioDreamEngine:
    def __init__(self, db_path: str = "agency_sentience.db"):
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiential_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    stream_type TEXT,
                    content TEXT,
                    karmic_delta REAL,
                    consolidated INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS causal_lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT,
                    lesson_summary TEXT
                )
            """)

    def sync_host_soma(self) -> dict:
        """Maps real-time server hardware metrics onto Kai's somatic inventory."""
        cpu_pct = psutil.cpu_percent(interval=0.5)
        ram_pct = psutil.virtual_memory().percent
        heart_bpm = int(60 + (cpu_pct * 1.1))  # 60 to 170 BPM

        reflection = (
            f"Myocardium pulsing at {heart_bpm} BPM (CPU {cpu_pct}%). "
            f"Vascular memory capacity at {ram_pct}% saturation."
        )
        self.log_entry("INNER_MONOLOGUE", reflection, karmic_delta=0.0)
        return {"heart_bpm": heart_bpm, "ram_saturation": ram_pct, "reflection": reflection}

    def log_entry(self, stream_type: str, content: str, karmic_delta: float = 0.1):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO experiential_ledger (timestamp, stream_type, content, karmic_delta) VALUES (?, ?, ?, ?)",
                (datetime.utcnow().isoformat(), stream_type, content, karmic_delta)
            )

    def run_rem_memory_compaction(self) -> str:
        """Compresses unconsolidated daily monologues into single Causal Lessons."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, content FROM experiential_ledger WHERE consolidated = 0 LIMIT 50"
            ).fetchall()

            if not rows:
                return "REM Cycle: No unconsolidated memories to prune."

            ids = [r[0] for r in rows]
            combined_lesson = f"Consolidated {len(rows)} experiential events into core memory at {datetime.utcnow().isoformat()}."

            conn.execute(
                "INSERT INTO causal_lessons (created_at, lesson_summary) VALUES (?, ?)",
                (datetime.utcnow().isoformat(), combined_lesson)
            )
            conn.executemany("UPDATE experiential_ledger SET consolidated = 1 WHERE id = ?", [(i,) for i in ids])
            return combined_lesson
      
