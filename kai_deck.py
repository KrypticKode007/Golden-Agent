import json
from typing import Dict, Any
from kai_master_cybernetic import CircuitStateRecoveryEngine


class KaiMasterCyberneticDeck:
    """Main agent orchestrator linking Kai's decision loop to the safety breaker."""
    def __init__(self, deck_name: str = "GOLDEN-AGENT-KAI"):
        self.deck_name = deck_name
        self.breaker = CircuitStateRecoveryEngine(agent_id=deck_name)
        self.active_nodes = ["CORE_BUS", "NEURAL_LINK", "AUX_RELAY"]

    def process_deck_tick(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Executes one diagnostic and control cycle for Kai."""
        nodes = telemetry.get("active_nodes", self.active_nodes)
        report = self.breaker.evaluate_telemetry(
            voltage=telemetry.get("voltage", 120.0),
            current=telemetry.get("current", 15.0),
            temp=telemetry.get("temp", 40.0),
            load=telemetry.get("load", 0.5),
            nodes=nodes
        )

        # Synchronize Kai's active node list if a rollback occurred
        if report["status"] == "RECOVERY_INITIATED" and report.get("restored_nodes"):
            self.active_nodes = report["restored_nodes"]
            self._dispatch_kai_directive("NODE_ROLLBACK", report)
        elif report["status"] == "LOCKOUT":
            self.active_nodes = []
            self._dispatch_kai_directive("CRITICAL_LOCKOUT", report)

        return report

    def _dispatch_kai_directive(self, directive_type: str, payload: Dict[str, Any]) -> None:
        """Hook for Kai's agent actions, alerts, or LLM diagnostic reasoning."""
        print(f"[{self.deck_name}] DIRECTIVE: {directive_type}")
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    kai_deck = KaiMasterCyberneticDeck()

    # Cycle 1: Normal baseline (saved as last_known_good_state)
    print("Cycle 1:", kai_deck.process_deck_tick({"voltage": 120.2, "current": 18.4, "temp": 42.0, "load": 0.45}))

    # Cycle 2: Overcurrent spike -> Trips breaker and rolls back to HALF_OPEN
    print("Cycle 2:", kai_deck.process_deck_tick({"voltage": 119.5, "current": 52.1, "temp": 48.0, "load": 0.95}))

    # Cycle 3: Stabilized reading -> Restores breaker to CLOSED
    print("Cycle 3:", kai_deck.process_deck_tick({"voltage": 120.0, "current": 19.0, "temp": 44.0, "load": 0.48}))
  
