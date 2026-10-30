import sqlite3
import threading
import time
from typing import Optional

class UnifiedTelemetryDatabase:
    """Consolidated thread-safe local data engine for edge telemetry storage."""
    
    def __init__(self, db_path: str = "agency_sentience.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._initialize_database()

    def _initialize_database(self) -> None:
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS telemetry_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL,
                        module_name TEXT,
                        latency_micros REAL,
                        status_msg TEXT
                    )
                """)
                conn.commit()

    def log_metric(self, module: str, latency: float, message: str) -> bool:
        """Safely inserts telemetry data across concurrent system loops."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO telemetry_logs (timestamp, module_name, latency_micros, status_msg)
                        VALUES (?, ?, ?, ?)
                    """, (time.time(), module, latency, message))
                    conn.commit()
                return True
            except sqlite3.Error:
                return False

    def get_latest_logs(self, limit: int = 10) -> list:
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT timestamp, module_name, latency_micros, status_msg 
                        FROM telemetry_logs ORDER BY id DESC LIMIT ?
                    """, (limit,))
                    return cursor.fetchall()
            except sqlite3.Error:
                return []
  
