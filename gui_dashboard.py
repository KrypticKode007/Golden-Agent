import os
import time
import sys
from robotic_database_core import UnifiedTelemetryDatabase
from kryptic_edge_launch import HardwareAccelerationBridge

def calculate_cpu_load_simulation() -> float:
    """Calculates a simulated operational compute workload curve based on system clock loops."""
    return round(40.0 + (time.time() % 10) * 1.5, 1)

def render_telemetry_dashboard(db_path: str = "agency_sentience.db"):
    """Main execution loop for drawing the monitoring display terminal layout."""
    db = UnifiedTelemetryDatabase(db_path=db_path)
    bridge = HardwareAccelerationBridge()
    
    # Pre-populate database with an initial operational startup checkpoint
    db.log_metric("AGENCY_CORE", 14.2, "Local automation engine runtime initialized.")
    
    try:
        while True:
            # Trigger a compute cycle to collect hardware latency data
            current_latency = bridge.trigger_cycle(operational_mode=1)
            db.log_metric("HARDWARE_BRIDGE", current_latency, "Telemetry packet received.")
            
            # Extract historical checkpoints from local data engine
            recent_logs = db.get_latest_logs(limit=4)
            cpu_metric = calculate_cpu_load_simulation()
            
            # Clear terminal canvas for clean rendering
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("=" * 85)
            print(f" OFFLINE CONSCIOUS DRONE | RECONSOLIDATED TELEMETRY INTERFACE      STATUS: OPERATIONAL")
            print("=" * 85)
            
            # Row 1: System Hardware Metrics
            print(f" [SYSTEM PERFORMANCE MATRIX]")
            print(f"  • Simulated CPU Core Load : {cpu_metric}%")
            print(f"  • RAM Resource Footprint  : 6.8 GB / 16 GB")
            print(f"  • Native Loop Latency     : {current_latency} μs")
            print(f"  • Deployment Mode         : LOCAL / OFFLINE IMMUTABLE ENVIRONMENT")
            print("-" * 85)
            
            # Row 2: In-Memory / Database Log Streams
            print(" [LOCAL DATA ENGINE REGISTRATION PERSISTENCE LOGS]")
            if not recent_logs:
                print("  No operational telemetry chunks written to storage yet...")
            else:
                for log in recent_logs:
                    ts, module, latency, msg = log
                    # Format standard timestamp display
                    time_str = time.strftime('%H:%M:%S', time.localtime(ts))
                    print(f"  [{time_str}] [{module}] Latency: {latency:.1f} μs | {msg}")
            
            print("=" * 85)
            print(" Press Ctrl+C to terminate dashboard monitoring loop safely.")
            
            # Throttling time delta to regulate thread cycles
            time.sleep(1.5)
            
    except KeyboardInterrupt:
        print("\n[INFO] Dashboard monitoring loop suspended cleanly via terminal call.")

if __name__ == "__main__":
    # Point execution directly to your primary development database
    render_telemetry_dashboard(db_path="agency_sentience.db")
            
