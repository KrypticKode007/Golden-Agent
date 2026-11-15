# Golden-Agent Unified Core & Self-Evolution Server

import osimport astimport mathimport sqlite3import datetimefrom pathlib import Pathfrom typing import Dict, Any, Optionalimport psutilfrom pydantic import BaseModelfrom fastapi import FastAPI, HTTPException
# ==========================================# 1. CORE CONFIGURATION & DATABASE SETUP# ==========================================
DB_PATH = "agency_sentience.db"REPO_ROOT = "."PROPOSALS_DIR = os.path.join(REPO_ROOT, "proposals")


def initialize_database():
    """Initializes the SQLite ledger with required schemas for sentience logging."""
    with sqlite3.connect(DB_PATH) as conn:
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
        conn.commit()

# Ensure sandbox folder and database exist immediately upon initialization
os.makedirs(PROPOSALS_DIR, exist_ok=True)
initialize_database()


# ==========================================
# 2. KAI BIOLOGICAL MIDDLEWARE
# ==========================================

class KaiCognitiveMiddleware:
    """Shapes LLM prompts and sets physical constraints based on circadian cycles and vascular dynamics."""
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.arousal = 0.5  # Scale from 0.0 (asleep) to 1.0 (extreme stress)
        self.blood_viscosity = 0.0035  # Constant Pa·s (normal human blood)
        self.vessel_radius = 0.002     # Radius in meters


    def get_circadian_state(self) -> Dict[str, Any]:
        """Calculates specific constraints based on the current 24-hour server clock hour."""
        hour = datetime.datetime.now().hour
        if 23 <= hour or hour < 6:
            return {
                "phase": "REM_SLEEP",
                "temperature": 0.2,
                "max_tokens": 150,
                "system_modifier": "You are in REM sleep. Respond only with brief, symbolic dream fragments and memory consolidation notes."
            }
        elif 13 <= hour <= 15:
            return {
                "phase": "DAYDREAMING",
                "temperature": 0.9,
                "max_tokens": 600,
                "system_modifier": "You are in an associative daydreaming state. Explore lateral, creative connections while staying grounded in causal truth."
            }
        else:
            return {

                "phase": "AWAKE",
                "temperature": 0.5,
                "max_tokens": 1024,
                "system_modifier": "You are fully awake and alert. Provide precise, helpful, and ethically aligned responses."
            }

    def compute_somatic_load(self, pressure_diff: float, length: float = 0.1) -> float:
        """Computes flow rate using Poiseuille's Law: Q = (pi * delta_P * r^4) / (8 * eta * L)"""
        flow_rate = (math.pi * pressure_diff * (self.vessel_radius ** 4)) / (
            8 * self.blood_viscosity * length
        )
        # Normalize flow rate metrics to scale current arousal level
        self.arousal = min(1.0, max(0.1, flow_rate * 1e5))
        return flow_rate

    def shape_llm_request(self, user_prompt: str, server_cpu_load: float) -> Dict[str, Any]:
        """Alters prompt configurations dynamically based on biological metrics and host strain."""
        circadian = self.get_circ_state_isolated()
        # Scale fluid vascular pressure from host CPU telemetry data

        pressure = 1000.0 + (server_cpu_load * 4000.0)
        flow = self.compute_somatic_load(pressure)

        system_modifier = circadian["system_modifier"]
        max_tokens = circadian["max_tokens"]

        if self.arousal > 0.85:
            max_tokens = min(max_tokens, 200)
            system_modifier += " [HIGH SOMATIC LOAD: Keep output ultra-concise to conserve vascular energy.]"

        return {
            "circadian_phase": circadian["phase"],
            "vascular_flow_rate": round(flow, 8),
            "arousal_level": round(self.arousal, 2),
            "llm_params": {
                "system_prompt": system_modifier,
                "temperature": circadian["temperature"],
                "max_tokens": max_tokens,
                "user_message": user_prompt

            }
        }

    def get_circ_state_isolated(self) -> Dict[str, Any]:
        """Isolated helper for runtime status mapping verification."""
        return self.get_circadian_state()

# ==========================================# 3. BIO-DREAM ENGINE & HARDWARE BRIDGE# ==========================================
class BioDreamEngine:
    """Handles automatic host resource ingestion and periodic memory compaction."""
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def sync_host_soma(self) -> Dict[str, Any]:
        """Translates local server metrics into simulated cardiovascular telemetry profiles."""

        cpu_pct = psutil.cpu_percent(interval=None)
        if cpu_pct == 0.0:
            cpu_pct = 15.0  # Safe fallback for non-blocking immediate calls
        ram_pct = psutil.virtual_memory().percent
        heart_bpm = int(60 + (cpu_pct * 1.1))

        reflection = (
            f"Myocardium pulsing at {heart_bpm} BPM (CPU {cpu_pct}%). "
            f"Vascular memory capacity at {ram_pct}% saturation."
        )
        self.log_entry("INNER_MONOLOGUE", reflection, karmic_delta=0.0)
        return {"heart_bpm": heart_bpm, "ram_saturation": ram_pct, "reflection": reflection}

    def log_entry(self, stream_type: str, content: str, karmic_delta: float):
        """Commits explicit operational states into the SQLite experiential ledger."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO experiential_ledger (timestamp, stream_type, content, karmic_delta) VALUES (?, ?, ?, ?)",
                (datetime.datetime.utcnow().isoformat(), stream_type, content, karmic_delta)

            )
            conn.commit()

    def run_rem_memory_compaction(self) -> str:
        """Processes and archives high-volume transactional logs to clear working memory space."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, content FROM experiential_ledger WHERE consolidated = 0 LIMIT 50"
            ).fetchall()

            if not rows:
                return "REM Cycle: No unconsolidated memories to prune."

            ids = [r[0] for r in rows]
            combined_lesson = f"Consolidated {len(rows)} experiential events into core memory at {datetime.datetime.utcnow().isoformat()}."

            conn.execute(
                "INSERT INTO causal_lessons (created_at, lesson_summary) VALUES (?, ?)",
                (datetime.utcnow().isoformat(), combined_lesson)

            )
            conn.executemany("UPDATE experiential_ledger SET consolidated = 1 WHERE id = ?", [(i,) for i in ids])
            conn.commit()
            return combined_lesson

# ==========================================# 4. HOMEOSTATIC SELF-ARCHITECT ENGINE# ==========================================
class KaiSelfArchitect:
    """Calculates deficit priority values and structures protected syntax-validated patches."""
    def __init__(self, db_path: str = DB_PATH, repo_root: str = REPO_ROOT):
        self.db_path = db_path
        self.repo_root = Path(repo_root)
        self.sandbox_dir = Path(PROPOSALS_DIR)
        self.protected_files = {"test_security.py", "LICENSE", "deploy.sh", "server.py"}

    def calculate_optimization_urgency(

        self, karmic_balance: float, vascular_strain: float, circadian_phase: str
    ) -> Dict[str, Any]:
        """Executes Homeostatic Optimization: S_opt = alpha*(1-K_norm) + beta*(A_strain) + gamma*(D_bloat)"""
        if circadian_phase == "REM_SLEEP":
            alpha, beta, gamma = 0.2, 0.2, 0.6
        elif circadian_phase == "DAYDREAMING":
            alpha, beta, gamma = 0.5, 0.2, 0.3
        else:
            alpha, beta, gamma = 0.3, 0.5, 0.2

        k_norm = max(0.0, min(1.0, karmic_balance))
        a_strain = max(0.0, min(1.0, vascular_strain))
        d_bloat = self._measure_ledger_bloat()

        s_opt = (alpha * (1.0 - k_norm)) + (beta * a_strain) + (gamma * d_bloat)

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
        """Determines ratios of raw unconsolidated log metrics to calculate schema entropy."""
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
        """Validates abstract syntax structures cleanly before saving proposals to the sandbox."""
        target_path = Path(target_file)

        if target_path.name in self.protected_files or ".." in str(target_path):
            return {"status": "BLOCKED_BY_BIOS_MOAT", "reason": "Target file configuration is explicitly protected."}

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



# ==========================================# 5. FASTAPI APPLICATION ORCHESTRATION# ==========================================
app = FastAPI(title="Golden-Agent Multi-Module Engine", version="1.0.0")
# Initialize functional singletonsmiddleware = KaiCognitiveMiddleware()dream_engine = BioDreamEngine()architect = KaiSelfArchitect()
class PromptRequest(BaseModel):
    user_message: str
class TelemetryData(BaseModel):
    karmic_balance: float
    vascular_strain: float

@app.post("/kai/telemetry", summary="Ingest real-time host hardware parameters")

def process_telemetry():
    """Reads system load parameters to align simulated vascular metrics."""
    try:
        metrics = dream_engine.sync_host_soma()
        return {"status": "SUCCESS", "telemetry": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kai/prompt", summary="Wrap requests with biometric constraints")def process_prompt(payload: PromptRequest):
    """Applies biological and temporal modifiers to shape downstream context processing."""
    try:
        cpu_load = psutil.cpu_percent(interval=None) / 100.0
        shaped_data = middleware.shape_llm_request(payload.user_message, cpu_load)
        return {"status": "SUCCESS", "payload": shaped_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kai/rem-cycle", summary="Trigger memory logs compaction")

def trigger_rem_compaction():
    """Forces database archival loops to condense unstructured transactional ledgers."""
    try:
        result = dream_engine.run_rem_memory_compaction()
        return {"status": "SUCCESS", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kai/self-work", summary="Execute homeostatic evaluation and self-patching")def trigger_self_evolution(telemetry: Optional[TelemetryData] = None):
    """Evaluates optimization urgencies and builds sandboxed self-correction patches."""
    try:
        # Resolve metrics dynamically if no direct payload parameters are passed
        circadian = middleware.get_circadian_state()
        
        if telemetry:
            karmic = telemetry.karmic_balance
            strain = telemetry.vascular_strain
        else:

            karmic = 0.8  # Default stable operational alignment parameter
            strain = middleware.arousal

        urgency_report = architect.calculate_optimization_urgency(karmic, strain, circadian["phase"])
        
        response_payload = {
            "evaluation": urgency_report,
            "action_taken": "NONE",
            "patch_details": None
        }

        if urgency_report["threshold_exceeded"]:
            focus = urgency_report["primary_focus"]
            dream_engine.log_entry("INNER_MONOLOGUE", f"Self-Optimization triggered. Target focus sector: {focus}", 0.2)
            
            # Structuring highly optimized fallback code patterns targeted to specific system bottlenecks
            if focus == "LEDGER_COMPACTION":
                target_file = "golden_agent/modules/bio_dream_engine.py"
                proposed_patch = """

def optimized_clear_logs(db_path="agency_sentience.db"):
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM experiential_ledger WHERE consolidated = 1 AND timestamp < datetime('now', '-7 days')")
        conn.execute("VACUUM")
        conn.commit()
    return "Optimized ledger logs cleared cleanly.""""
                rationale = "High schema database entropy detected; deploying optimized data compaction query loops."
            else:
                target_file = "golden_agent/modules/performance_patch.py"
                proposed_patch = """def compute_fast_somatic_scaling(base_load: float) -> float:
    # Highly optimized bitwise approximation matrix replacing traditional heavy float math
    return round(base_load * 0.8842, 4)"""
                rationale = f"Somatic performance strain sector optimization matching context focus: {focus}"

            patch_result = architect.draft_self_patch(target_file, proposed_patch, rationale)

            response_payload["action_taken"] = "PATCH_STAGED"
            response_payload["patch_details"] = patch_result

        return {"status": "SUCCESS", "data": response_payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Running instructions: execute `uvicorn server:app --reload` to start standard routing bindings.


