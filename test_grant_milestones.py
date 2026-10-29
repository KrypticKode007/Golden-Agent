#!/usr/bin/env python3
import os
import time
import pytest
from unittest.mock import patch, mock_open

# Import targets from the core framework matrix
from os_telemetry_provider import LinuxHardwareTelemetryProvider
from kryptic_agent_core import AutonomousAgentCore

class TestPhaseIMilestoneValidation:
    """
    Automated pytest validation suite tracking compliance for 
    Phase I technical milestones and performance bounds.
    """

    # --- MILESTONE 1: CORE PIPELINE LATENCY & TELEMETRY ---
    
    def test_orchestration_loop_latency_threshold(self):
        """
        Validates Milestone 1: Assures local loop iteration execution remains 
        within the strict sub-millisecond threshold (< 1.0 ms) under clean execution.
        """
        agent = AutonomousAgentCore()
        
        start_time = time.perf_counter()
        # Execute single high-speed orchestration mapping pass
        execution_status = agent.execute_single_loop_pass()
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        
        assert execution_status is True
        assert latency_ms < 1.0, f"Latency verification failed: {latency_ms:.3f}ms exceeds 1.0ms limit"

    @patch("builtins.open", new_callable=mock_open, read_data="25000\n")
    @patch("os.path.exists", return_value=True)
    def test_sys_class_hardware_telemetry_parsing(self, mock_exists, mock_file):
        """
        Validates Milestone 1: Verifies continuous direct hardware telemetry 
        parsing via /sys/class registers operates without throwing exceptions.
        """
        provider = LinuxHardwareTelemetryProvider()
        metrics = provider.read_thermal_registers()
        
        assert "thermal_zone0" in metrics
        assert metrics["thermal_zone0"] == 25000  # Raw milli-celsius verification

    # --- MILESTONE 2: FAULT-ISOLATION & STATE PERSISTENCE ---

    def test_resilient_persistence_on_mock_operational_shock(self):
        """
        Validates Milestone 2: Enforces that underlying encrypted memory states 
        survive mid-loop infrastructure faults or invalid execution inputs.
        """
        agent = AutonomousAgentCore()
        
        # Load critical operational token payload into state memory
        agent.set_memory_register("grant_secure_anchor", "FAR_COMPLIANT_VAL")
        
        # Inject deliberate operational shock / malformed token
        with pytest.raises(ValueError):
            agent.process_secured_command_broadcast(malformed_payload=True)
            
        # Verify persistence layer retained historical anchor state post-crash
        retained_state = agent.get_memory_register("grant_secure_anchor")
        assert retained_state == "FAR_COMPLIANT_VAL"
      
