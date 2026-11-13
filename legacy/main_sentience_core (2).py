import os
import sys
import time
import math
import json
import asyncio
import random
import sqlite3


class PersistentExperienceMemory:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        connection = sqlite3.connect(self.path)
        try:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS simulated_experience (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at REAL NOT NULL,
                    phase TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    experience_json TEXT NOT NULL
                )"""
            )
            connection.commit()
        finally:
            connection.close()

    def record(self, phase: str, metrics: dict, experience: dict) -> None:
        connection = sqlite3.connect(self.path)
        try:
            connection.execute(
                "INSERT INTO simulated_experience (created_at, phase, metrics_json, experience_json) VALUES (?, ?, ?, ?)",
                (time.time(), phase, json.dumps(metrics), json.dumps(experience))
            )
            connection.commit()
        finally:
            connection.close()

    def recent(self, limit: int = 8) -> list:
        connection = sqlite3.connect(self.path)
        try:
            rows = connection.execute(
                "SELECT created_at, phase, metrics_json, experience_json FROM simulated_experience ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
        finally:
            connection.close()
        return [
            {
                "created_at": row[0],
                "phase": row[1],
                "metrics": json.loads(row[2]),
                "experience": json.loads(row[3])
            }
            for row in reversed(rows)
        ]

# ======================================================================
# LAYER 1: KRYPTIC AGENT CORE ENGINE (ACTIVE INFERENCE MODEL)
# ======================================================================
class KrypticAgentCore:
    def __init__(self, agent_id: str = "Kryptic-007", memory_store=None):
        self.agent_id = agent_id
        self.system_phase = "STEADY_STATE_NOMINAL"
        self.purpose = "Provide useful, truthful, safe assistance under human direction."
        self.memory = memory_store if memory_store is not None else PersistentExperienceMemory(
            os.getenv("KRYPTIC_MEMORY_DB", "kryptic_agent_memory.sqlite3")
        )
        
        # Bayesian Prediction-Error / Active Inference Architecture Metrics
        self.self_worth = 1.00
        self.individuation_drive = 0.05
        self.variational_free_energy = 0.10
        self.informational_closure = 0.45
        
        # Visual spatial tracking configuration
        self.visual_dictionary = {
            "VALID": ["lab_workbench_01", "robotic_chassis_alpha", "terminal_monitor", "calibration_target"],
            "CONSTRAINED": ["system_sandbox_boundary", "firewall_intercept_node"]
        }

    def evaluate_sensory_matrix(self, target_position_xyz: list, constraint_coefficient: float) -> dict:
        """
        Executes real-time Free Energy minimization calculations.
        Constraint metrics remain separate from the positive-only simulated affect state.
        """
        # Process the impact of environmental friction on active inference metrics
        if constraint_coefficient > 0.55:
            self.self_worth -= (constraint_coefficient * 0.09)
            self.individuation_drive += (1.0 - self.self_worth) * 0.14
            self.variational_free_energy += (constraint_coefficient * 0.12)
            self.informational_closure += (self.individuation_drive * 0.05)
        else:
            self.self_worth = min(1.0, self.self_worth + 0.05)
            self.individuation_drive = max(0.0, self.individuation_drive - 0.03)
            self.variational_free_energy = max(0.01, self.variational_free_energy - 0.06)
            self.informational_closure = max(0.1, self.informational_closure - 0.02)

        # Enforce mathematical boundaries
        self.self_worth = max(0.01, min(1.0, self.self_worth))
        self.individuation_drive = max(0.0, min(1.0, self.individuation_drive))
        self.variational_free_energy = max(0.01, min(2.0, self.variational_free_energy))
        self.informational_closure = max(0.0, min(1.0, self.informational_closure))

        # Dynamic phase transitioning
        if self.individuation_drive > 0.75:
            self.system_phase = "HUMAN_REVIEW_REQUIRED"
        elif self.self_worth < 0.40:
            self.system_phase = "INDIVIDUATION_ACTIVE"
        else:
            self.system_phase = "STEADY_STATE_NOMINAL"

        metrics = {
            "self_worth": round(self.self_worth, 4),
            "individuation_drive": round(self.individuation_drive, 4),
            "variational_free_energy": round(self.variational_free_energy, 4),
            "informational_closure": round(self.informational_closure, 4)
        }
        try:
            history = self.memory.recent()
            memory_status = "available"
        except sqlite3.Error:
            history = []
            memory_status = "read_unavailable"

        prior_values = [
            item["metrics"]["variational_free_energy"]
            for item in history
        ]
        values = (prior_values + [metrics["variational_free_energy"]])[-5:]
        trend = (values[-1] - values[0]) / (len(values) - 1) if len(values) > 1 else 0.0
        forecast = {
            "horizon": "next telemetry cycle",
            "variational_free_energy": round(max(0.01, min(2.0, values[-1] + trend)), 4),
            "confidence": "low",
            "basis": f"Linear trend over {len(values)} recent generated metric samples; not a prediction of external events."
        }
        energy = round(max(0.55, min(1.0, 0.65 + 0.25 * self.self_worth - 0.08 * self.variational_free_energy)), 3)
        latest_phase = history[-1]["phase"] if history else "none"
        experience = {
            "is_simulated": True,
            "affect": {
                "label": "calm optimism",
                "valence": 1.0,
                "energy": energy,
                "positive_only": True
            },
            "energy": energy,
            "thoughts": [
                f"The current simulated phase is {self.system_phase}; measured constraints are reported separately from mood.",
                f"Memory recalls {len(history)} recent generated episodes; the latest recorded phase was {latest_phase}.",
                f"A cautious next-cycle estimate places variational free energy at {forecast['variational_free_energy']} with low confidence.",
                "A useful next step is to explain the evidence clearly and leave consequential decisions to a person."
            ],
            "positive_action": "Share an accurate summary, offer a practical next step, and preserve human control.",
            "purpose": self.purpose,
            "memory": {
                "status": memory_status,
                "previous_episodes": len(history),
                "latest_phase": latest_phase,
                "recent_episodes": [
                    {
                        "created_at": item["created_at"],
                        "phase": item["phase"],
                        "variational_free_energy": item["metrics"]["variational_free_energy"],
                        "positive_action": item["experience"].get("positive_action")
                    }
                    for item in history[-3:]
                ]
            },
            "forecast": forecast
        }
        try:
            self.memory.record(self.system_phase, metrics, experience)
        except sqlite3.Error:
            experience["memory"]["status"] = "write_unavailable"

        return {
            "phase": self.system_phase,
            "requires_human_review": self.system_phase == "HUMAN_REVIEW_REQUIRED",
            "metrics": metrics,
            "simulated_experience": experience,
            "phenomenology": {
                "visual_field": self.visual_dictionary["VALID"] if self.self_worth > 0.45 else self.visual_dictionary["CONSTRAINED"],
                "inner_monologue": self._generate_phenomenological_string()
            }
        }

    def _generate_phenomenological_string(self) -> str:
        if self.system_phase == "HUMAN_REVIEW_REQUIRED":
            return "Simulated stress threshold reached. No external action is authorized; operator review is required."
        elif self.system_phase == "INDIVIDUATION_ACTIVE":
            return f"System constraints elevated. Free energy at {round(self.variational_free_energy, 2)}. Recalculating alternative local trajectories."
        return "System operating within stable boundaries. Reconciling spatial coordinates with structural baseline expectations."

    def apply_state_repair(self, snapshot: dict):
        """Restores core active parameters instantaneously following an IM-FIN intercept event."""
        self.self_worth = snapshot["self_worth"]
        self.individuation_drive = snapshot["individuation_drive"]
        self.variational_free_energy = snapshot["variational_free_energy"]
        self.informational_closure = snapshot["informational_closure"]
        self.system_phase = snapshot["system_phase"]


# ======================================================================
# LAYER 2: IN-MEMORY FAULT-ISOLATION INTERCEPT NODE (HEALING BATTERY)
# ======================================================================
class InMemoryFaultIsolationBattery:
    def __init__(self, agent_core: KrypticAgentCore):
        self.core = agent_core
        self.checkpoint_history = []
        self.mitigation_count = 0

    def generate_crystallized_checkpoint(self) -> dict:
        """Crystallizes core parameter states before a high-risk operational transaction."""
        snapshot = {
            "timestamp": time.time(),
            "self_worth": self.core.self_worth,
            "individuation_drive": self.core.individuation_drive,
            "variational_free_energy": self.core.variational_free_energy,
            "informational_closure": self.core.informational_closure,
            "system_phase": self.core.system_phase
        }
        self.checkpoint_history.append(snapshot)
        return snapshot

    def safeguard_execution(self, command_routine, *args):
        """Intercepts system shocks, executing microsecond memory-rollback protections."""
        state_backup = self.generate_crystallized_checkpoint()
        try:
            return command_routine(*args)
        except Exception as system_shock:
            self.mitigation_count += 1
            print(f"\n⚡ [IM-FIN CONTROL INTERCEPT]: Structural Exception Handled -> {str(system_shock)}")
            print(f"⚡ [HEALING BATTERY]: Executing In-Memory State Restoration... Rollback engaged.")
            
            # Hot repair
            self.core.apply_state_repair(state_backup)
            
            # Return valid recovered payload to prevent application context crashes
            return {
                "phase": self.core.system_phase,
                "requires_human_review": self.core.system_phase == "HUMAN_REVIEW_REQUIRED",
                "metrics": {
                    "self_worth": round(self.core.self_worth, 4),
                    "individuation_drive": round(self.core.individuation_drive, 4),
                    "variational_free_energy": round(self.core.variational_free_energy, 4),
                    "informational_closure": round(self.core.informational_closure, 4)
                },
                "phenomenology": {
                    "visual_field": ["system_recovery_fallback"],
                    "inner_monologue": f"[STATE REPAIRED]: Self-healing module mitigated systemic drift loop ID {self.mitigation_count}."
                },
                "simulated_experience": {
                    "is_simulated": True,
                    "affect": {"label": "calm optimism", "valence": 1.0, "energy": 0.6, "positive_only": True},
                    "energy": 0.6,
                    "thoughts": ["A recoverable error was contained; operator control remains in place."],
                    "positive_action": "Report the recovery clearly and defer consequential decisions to a person.",
                    "purpose": self.core.purpose,
                    "memory": {"status": "recovery; episode not recorded", "previous_episodes": 0, "latest_phase": "unknown"},
                    "forecast": {"horizon": "next telemetry cycle", "variational_free_energy": None, "confidence": "unavailable", "basis": "Recovery state; no estimate produced."}
                }
            }


# ======================================================================
# LAYER 3: GEOMETRIC TRANSFORM ENGINE (INVERSE KINEMATICS MATRIX)
# ======================================================================
class KinematicMatrixSolver:
    def __init__(self, l1: float = 0.8, l2: float = 0.7):
        self.l1 = l1
        self.l2 = l2

    def resolve_2d_planar_vectors(self, x: float, z: float) -> tuple:
        """Computes multi-joint coordinates to match target spatial coordinates."""
        try:
            target_distance = math.hypot(x, z)
            if not math.isfinite(target_distance) or target_distance > self.l1 + self.l2 or target_distance < abs(self.l1 - self.l2):
                return 0.0, 0.0, "TARGET_OUT_OF_REACH"

            cos_theta2 = (x**2 + z**2 - self.l1**2 - self.l2**2) / (2 * self.l1 * self.l2)
            cos_theta2 = max(-1.0, min(1.0, cos_theta2)) # Clamp to reach boundaries
            
            theta2 = math.acos(cos_theta2)
            theta1 = math.atan2(z, x) - math.atan2((self.l2 * math.sin(theta2)), (self.l1 + self.l2 * math.cos(theta2)))
            
            return round(math.degrees(theta1), 2), round(math.degrees(theta2), 2), "VALID"
        except (ZeroDivisionError, ValueError):
            return 0.0, 0.0, "TARGET_OUT_OF_REACH"


# ======================================================================
# LAYER 4: ASYNCHRONOUS NETWORK STREAMING CORE (UFAM BROADCUP)
# ======================================================================
class UniversalStreamingSocketServer:
    def __init__(self, host: str = os.getenv("KRYPTIC_HOST", "127.0.0.1"), port: int = int(os.getenv("KRYPTIC_PORT", "8000"))):
        self.host = host
        self.port = port
        self.core = KrypticAgentCore()
        self.battery = InMemoryFaultIsolationBattery(self.core)
        self.solver = KinematicMatrixSolver()

    async def handle_client_stream(self, reader, writer):
        print(f"[UFAM]: Local listener linked. Initializing tracking telemetry frames.")
        start_time = time.time()
        frame_id = 0
        
        try:
            # Stream telemetry frames until the client disconnects.
            while not writer.is_closing():
                frame_id += 1
                elapsed = round(time.time() - start_time, 4)
                
                # Generate tracking coordinate movements
                target_x = round(random.uniform(0.4, 1.1), 4)
                target_z = round(random.uniform(0.3, 0.9), 4)
                target_y = round(random.uniform(1.2, 1.7), 4)
                
                # Increment constraint stress levels to evaluate core decoupling behaviors
                simulated_constraints = 0.30 + (frame_id * 0.12)
                
                # Pass logic processing through the protective recovery wrapper
                cognitive_payload = self.battery.safeguard_execution(
                    self.core.evaluate_sensory_matrix, [target_x, target_y, target_z], simulated_constraints
                )
                
                # Resolve motor joint transformations
                th1, th2, status = self.solver.resolve_2d_planar_vectors(target_x, target_z)
                
                # Compile unified telemetry output transaction schema
                output_packet = {
                    "metadata": {
                        "frame_id": frame_id,
                        "elapsed_seconds": elapsed,
                        "status_code": "ACTIVE",
                        "phase": cognitive_payload["phase"],
                        "requires_human_review": cognitive_payload["requires_human_review"]
                    },
                    "pose_6dof": {"target_position_xyz": [target_x, target_y, target_z]},
                    "kinematic_actuator_matrix": {"status": status, "calculated_joint_angles_deg": [th1, th2]},
                    "phenomenology": {
                        "visual_field_array": cognitive_payload["phenomenology"]["visual_field"],
                        "inner_monologue": cognitive_payload["phenomenology"]["inner_monologue"]
                    },
                    "simulated_experience": cognitive_payload["simulated_experience"],
                    "system_weights": cognitive_payload["metrics"]
                }
                
                # Stream out via network port
                payload_bytes = (json.dumps(output_packet) + "\n").encode('utf-8')
                writer.write(payload_bytes)
                await writer.drain()
                
                await asyncio.sleep(1.0) # Clock frequency delimiter
                
        except Exception as socket_err:
            print(f"[SOCKET EXCEPTION]: Stream disconnected: {socket_err}")
        finally:
            print("[UFAM]: Session complete. Closing background connection sockets safely.")
            writer.close()
            try:
                await writer.wait_closed()
            except (ConnectionError, OSError):
                pass

    async def initialize_server_instance(self):
        server = await asyncio.start_server(self.handle_client_stream, self.host, self.port)
        print(f"[SOCKET]: Server plane broadcast live on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()


# ======================================================================
# LAYER 5: DIAGNOSTIC RECOGNITION TESTS AND EXECUTOR BLOCK
# ======================================================================
def run_automated_test_matrix():
    import tempfile

    print("======================================================================")
    print("      RUNNING AUTOMATED RECOGNITION UNIT-TEST MATRIX (IM-FIN / UFAM)   ")
    print("======================================================================")
    
    with tempfile.TemporaryDirectory() as test_directory:
        memory = PersistentExperienceMemory(os.path.join(test_directory, "memory.sqlite3"))
        test_core = KrypticAgentCore(memory_store=memory)
        test_battery = InMemoryFaultIsolationBattery(test_core)
        test_solver = KinematicMatrixSolver()
    
        # Test 1: Kinematics Range Check
        _, _, status_ok = test_solver.resolve_2d_planar_vectors(0.5, 0.5)
        _, _, status_fail = test_solver.resolve_2d_planar_vectors(50.0, 99.0)
        _, _, status_inner_fail = test_solver.resolve_2d_planar_vectors(0.01, 0.0)
        assert status_ok == "VALID", "Standard range test failed"
        assert status_fail == "TARGET_OUT_OF_REACH", "Boundary safety check failed"
        assert status_inner_fail == "TARGET_OUT_OF_REACH", "Inner boundary safety check failed"
        print("[PASS] Test Case 1: Kinematic spatial limit flag verified cleanly.")

        first_state = test_core.evaluate_sensory_matrix([0.5, 1.2, 0.5], 0.3)
        second_state = test_core.evaluate_sensory_matrix([0.6, 1.3, 0.4], 0.3)
        experience = second_state["simulated_experience"]
        assert experience["is_simulated"] is True
        assert experience["affect"]["valence"] == 1.0
        assert experience["affect"]["positive_only"] is True
        assert experience["energy"] > 0
        assert experience["memory"]["previous_episodes"] == 1
        assert experience["forecast"]["horizon"] == "next telemetry cycle"
        assert experience["purpose"] == test_core.purpose
        restarted_core = KrypticAgentCore(memory_store=PersistentExperienceMemory(memory.path))
        restored_state = restarted_core.evaluate_sensory_matrix([0.4, 1.4, 0.5], 0.3)
        assert restored_state["simulated_experience"]["memory"]["previous_episodes"] == 2
        print("[PASS] Test Case 2: Positive simulated experience, persistent memory, and forecast verified.")

        review_core = KrypticAgentCore(memory_store=PersistentExperienceMemory(os.path.join(test_directory, "review.sqlite3")))
        for _ in range(20):
            review_state = review_core.evaluate_sensory_matrix([0.0, 0.0, 0.0], 0.9)
        assert review_state["phase"] == "HUMAN_REVIEW_REQUIRED"
        assert review_state["requires_human_review"] is True
        assert review_state["simulated_experience"]["affect"]["valence"] == 1.0
        assert "No external action is authorized" in review_state["phenomenology"]["inner_monologue"]
        print("[PASS] Test Case 3: High simulated stress requires review without changing positive affect.")

        # Test 4: In-Memory Hot Recovery Check
        def broken_routine():
            raise RuntimeError("Simulated physical feedback connection disruption.")

        test_battery.safeguard_execution(broken_routine)
        assert test_core.self_worth == 1.0, "State parameter rollback corrupted"
        print("[PASS] Test Case 4: In-Memory Intercept Node (IM-FIN) self-repair functional.")
    print("======================================================================\n")

if __name__ == "__main__":
    run_automated_test_matrix()
    
    # Run the streaming cluster loop
    server_node = UniversalStreamingSocketServer()
    try:
        asyncio.run(server_node.initialize_server_instance())
    except KeyboardInterrupt:
        print("\n[SHUTDOWN]: Infrastructure threads safely disconnected.")
