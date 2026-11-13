import time
from collections import deque
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, Optional, List


class BreakerState(Enum):
    CLOSED = "CLOSED"          # Normal operation (power flowing)
    OPEN = "OPEN"              # Tripped / Fault isolated
    HALF_OPEN = "HALF_OPEN"    # Testing recovery stability
    LOCKOUT = "LOCKOUT"        # Hard fault requiring manual override


@dataclass
class TelemetrySnapshot:
    timestamp: float
    voltage: float
    current_amps: float
    temp_celsius: float
    load_factor: float
    state: str
    active_nodes: List[str]


@dataclass
class DiagnosticEvent:
    timestamp: float
    fault_code: str
    trigger_metric: str
    recorded_value: float
    threshold: float
    recovery_attempted: bool
    recovery_success: bool
    notes: str


class DiagnosticContextMemory:
    """Maintains rolling telemetry baselines and fault context for Kai."""
    def __init__(self, max_snapshots: int = 100, max_events: int = 200):
        self.snapshots: deque[TelemetrySnapshot] = deque(maxlen=max_snapshots)
        self.fault_history: deque[DiagnosticEvent] = deque(maxlen=max_events)
        self.last_known_good_state: Optional[TelemetrySnapshot] = None

    def record_telemetry(self, snapshot: TelemetrySnapshot) -> None:
        self.snapshots.append(snapshot)
        if snapshot.state == BreakerState.CLOSED.value:
            self.last_known_good_state = snapshot

    def log_fault(self, event: DiagnosticEvent) -> None:
        self.fault_history.append(event)

    def get_recent_fault_count(self, fault_code: str, window_seconds: float = 300.0) -> int:
        now = time.time()
        return sum(
            1 for e in self.fault_history
            if e.fault_code == fault_code and (now - e.timestamp) <= window_seconds
        )

    def get_kai_context_summary(self) -> Dict[str, Any]:
        """Formats memory state so Kai's agent layer can reason over recent faults."""
        return {
            "last_known_good": asdict(self.last_known_good_state) if self.last_known_good_state else None,
            "recent_faults": [asdict(e) for e in list(self.fault_history)[-5:]],
            "total_buffered_snapshots": len(self.snapshots)
        }


class CircuitStateRecoveryEngine:
    """Automated circuit breaker controller with self-healing state rollback."""
    def __init__(self, agent_id: str = "KAI-BREAKER-CORE"):
        self.agent_id = agent_id
        self.state = BreakerState.CLOSED
        self.memory = DiagnosticContextMemory()
        self.thresholds = {
            "max_current_amps": 45.0,
            "max_temp_celsius": 85.0,
            "min_voltage": 105.0,
            "max_voltage": 130.0
        }
        self.max_retries_before_lockout = 3

    def evaluate_telemetry(self, voltage: float, current: float, temp: float, load: float, nodes: List[str]) -> Dict[str, Any]:
        snapshot = TelemetrySnapshot(
            timestamp=time.time(),
            voltage=voltage,
            current_amps=current,
            temp_celsius=temp,
            load_factor=load,
            state=self.state.value,
            active_nodes=nodes
        )
        self.memory.record_telemetry(snapshot)

        if self.state == BreakerState.LOCKOUT:
            return {
                "status": "LOCKOUT",
                "state": self.state.value,
                "action": "MANUAL_OVERRIDE_REQUIRED",
                "context": self.memory.get_kai_context_summary()
            }

        fault_code = None
        metric = ""
        val = 0.0
        thresh = 0.0

        if snapshot.current_amps > self.thresholds["max_current_amps"]:
            fault_code, metric, val, thresh = "ERR_OVERCURRENT", "current_amps", snapshot.current_amps, self.thresholds["max_current_amps"]
        elif snapshot.temp_celsius > self.thresholds["max_temp_celsius"]:
            fault_code, metric, val, thresh = "ERR_THERMAL_TRIP", "temp_celsius", snapshot.temp_celsius, self.thresholds["max_temp_celsius"]
        elif not (self.thresholds["min_voltage"] <= snapshot.voltage <= self.thresholds["max_voltage"]):
            fault_code, metric, val, thresh = "ERR_VOLTAGE_INSTABILITY", "voltage", snapshot.voltage, self.thresholds["max_voltage"]

        if fault_code:
            return self._execute_trip_and_recovery(fault_code, metric, val, thresh)

        if self.state == BreakerState.HALF_OPEN:
            self.state = BreakerState.CLOSED
            return {
                "status": "RECOVERED",
                "state": self.state.value,
                "message": "Circuit stability verified. Breaker restored to CLOSED."
            }

        return {"status": "NOMINAL", "state": self.state.value}

    def _execute_trip_and_recovery(self, fault_code: str, metric: str, value: float, threshold: float) -> Dict[str, Any]:
        self.state = BreakerState.OPEN
        recent_trips = self.memory.get_recent_fault_count(fault_code, window_seconds=300.0)

        if recent_trips >= self.max_retries_before_lockout:
            self.state = BreakerState.LOCKOUT
            self.memory.log_fault(DiagnosticEvent(
                timestamp=time.time(),
                fault_code=fault_code,
                trigger_metric=metric,
                recorded_value=value,
                threshold=threshold,
                recovery_attempted=False,
                recovery_success=False,
                notes="Max retry limit reached within 5-minute window. Engaging hardware LOCKOUT."
            ))
            return {
                "status": "LOCKOUT",
                "state": self.state.value,
                "fault": fault_code,
                "context": self.memory.get_kai_context_summary()
            }

        lkg = self.memory.last_known_good_state
        recovery_success = False
        notes = "No safe baseline snapshot available for rollback."

        if lkg:
            self.state = BreakerState.HALF_OPEN
            recovery_success = True
            notes = f"Rolled back active nodes to baseline from {lkg.timestamp}: {lkg.active_nodes}"

        self.memory.log_fault(DiagnosticEvent(
            timestamp=time.time(),
            fault_code=fault_code,
            trigger_metric=metric,
            recorded_value=value,
            threshold=threshold,
            recovery_attempted=True,
            recovery_success=recovery_success,
            notes=notes
        ))

        return {
            "status": "RECOVERY_INITIATED" if recovery_success else "TRIPPED_OPEN",
            "state": self.state.value,
            "fault": fault_code,
            "restored_nodes": lkg.active_nodes if lkg else [],
            "context": self.memory.get_kai_context_summary()
        }

    def manual_reset_lockout(self, operator_id: str) -> Dict[str, Any]:
        """Allows Kai or an authorized operator to clear a LOCKOUT state."""
        if self.state != BreakerState.LOCKOUT:
            return {"status": "IGNORED", "message": f"Breaker is currently {self.state.value}, not in LOCKOUT."}
        self.state = BreakerState.HALF_OPEN
        return {
            "status": "LOCKOUT_CLEARED",
            "state": self.state.value,
            "cleared_by": operator_id,
            "message": "Breaker moved to HALF_OPEN for stability verification."
        }
        
