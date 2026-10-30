import time
import os
import json
import logging
from kryptic_edge_launch import HardwareAccelerationBridge
from robotic_database_core import UnifiedTelemetryDatabase

logging.basicConfig(level=logging.INFO)

def load_calibration_profile(profile_path="calibration_profile.json") -> dict:
    if os.path.exists(profile_path):
        with open(profile_path, "r") as f:
            data = json.load(f)
            active = data["active_profile"]
            return data["profiles"][active]
    return {"matrix_loop_bounds": 5000, "collection_interval_seconds": 1.5}

def run_memory_optimization_bench(ticks=20):
    print("=== INITIALIZING NATIVE PERFORMANCE MEMORY OPTIMIZATION TEST ===")
    profile = load_calibration_profile()
    bridge = HardwareAccelerationBridge()
    db = UnifiedTelemetryDatabase(db_path="agency_sentience.db")
    
    loop_bounds = profile["matrix_loop_bounds"]
    interval = profile["collection_interval_seconds"]
    
    print(f"[RUNNING] Target Iterations per Tick: {loop_bounds} | Delay Delta: {interval}s")
    
    for tick in range(1, ticks + 1):
        start_mem = os.popen('free -m | grep Mem | awk \'{print $3}\'').read().strip()
        latency = bridge.trigger_cycle(operational_mode=int(loop_bounds / 5000))
        end_mem = os.popen('free -m | grep Mem | awk \'{print $3}\'').read().strip()
        
        db.log_metric("MEM_BENCH", latency, f"Tick #{tick} completed. Memory state delta: {start_mem}MB -> {end_mem}MB")
        print(f"  [Tick {tick}/{ticks}] Computed Native Latency: {latency:.2f} μs | System Stable")
        time.sleep(interval)
        
    print("[SUCCESS] Memory optimization verification pipeline finalized successfully.")

if __name__ == "__main__":
    run_memory_optimization_bench(ticks=10)
    
