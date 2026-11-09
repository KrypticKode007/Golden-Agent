from pathlib import Path
import runpy


CORE_PATH = Path(__file__).resolve().parents[1] / "main_sentience_core (2).py"
CORE = runpy.run_path(str(CORE_PATH))
KrypticAgentCore = CORE["KrypticAgentCore"]
KinematicMatrixSolver = CORE["KinematicMatrixSolver"]
InMemoryFaultIsolationBattery = CORE["InMemoryFaultIsolationBattery"]
PersistentExperienceMemory = CORE["PersistentExperienceMemory"]


def make_core(path):
    memory = PersistentExperienceMemory(str(path))
    return KrypticAgentCore(memory_store=memory)


def test_positive_experience_memory_and_forecast_persist(tmp_path):
    database_path = tmp_path / "experience.sqlite3"
    core = make_core(database_path)
    core.evaluate_sensory_matrix([0.5, 1.2, 0.5], 0.3)
    state = core.evaluate_sensory_matrix([0.6, 1.3, 0.4], 0.3)

    experience = state["simulated_experience"]
    assert experience["is_simulated"] is True
    assert experience["affect"]["positive_only"] is True
    assert experience["affect"]["valence"] == 1.0
    assert 0.0 < experience["energy"] <= 1.0
    assert experience["memory"]["previous_episodes"] == 1
    assert experience["memory"]["recent_episodes"][0]["phase"] == "STEADY_STATE_NOMINAL"
    assert experience["forecast"]["horizon"] == "next telemetry cycle"
    assert experience["forecast"]["confidence"] == "low"
    assert "human direction" in experience["purpose"]

    restarted_core = make_core(database_path)
    restored_state = restarted_core.evaluate_sensory_matrix([0.4, 1.4, 0.5], 0.3)
    assert restored_state["simulated_experience"]["memory"]["previous_episodes"] == 2


def test_high_stress_requires_review_without_negative_affect(tmp_path):
    core = make_core(tmp_path / "review.sqlite3")
    for _ in range(20):
        state = core.evaluate_sensory_matrix([0.0, 0.0, 0.0], 0.9)

    assert state["phase"] == "HUMAN_REVIEW_REQUIRED"
    assert state["requires_human_review"] is True
    assert state["simulated_experience"]["affect"]["valence"] == 1.0
    assert "No external action is authorized" in state["phenomenology"]["inner_monologue"]


def test_kinematics_rejects_unreachable_targets():
    solver = KinematicMatrixSolver()
    assert solver.resolve_2d_planar_vectors(0.5, 0.5)[2] == "VALID"
    assert solver.resolve_2d_planar_vectors(50.0, 99.0)[2] == "TARGET_OUT_OF_REACH"
    assert solver.resolve_2d_planar_vectors(0.01, 0.0)[2] == "TARGET_OUT_OF_REACH"


def test_fault_recovery_returns_review_and_experience_payload(tmp_path):
    core = make_core(tmp_path / "recovery.sqlite3")
    battery = InMemoryFaultIsolationBattery(core)

    def broken_routine():
        raise RuntimeError("test failure")

    result = battery.safeguard_execution(broken_routine)
    assert result["requires_human_review"] is False
    assert result["simulated_experience"]["is_simulated"] is True
    assert result["simulated_experience"]["affect"]["positive_only"] is True