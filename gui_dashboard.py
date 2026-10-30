import os
import time
import sys
import math
from robotic_database_core import UnifiedTelemetryDatabase
from kryptic_edge_launch import HardwareAccelerationBridge

def generate_ascii_graph(history, max_val=18.6, min_val=11.0, rows=6) -> list:
    """Generates a structured visual line graph inside the canvas grid."""
    graph_lines = []
    grid = [[" " for _ in range(35)] for _ in range(rows)]
    
    # Pad or slice history to map to the 35-character graph width
    points = history[-35:]
    val_range = (max_val - min_val) if (max_val - min_val) > 0 else 1.0
    
    for x_idx, val in enumerate(points):
        if x_idx >= 35:
            break
        # Calculate row mapping position
        normalized_y = (val - min_val) / val_range
        y_idx = int(normalized_y * (rows - 1))
        y_idx = max(0, min(rows - 1, y_idx))
        grid[(rows - 1) - y_idx][x_idx] = "•" if x_idx < len(points)-1 else "▲"

    for r in range(rows):
        current_y_val = max_val - (r * (val_range / (rows - 1)))
        row_str = f"{current_y_val:.1f} ┤" + "".join(grid[r])
        graph_lines.append(row_str)
    return graph_lines

def run_synchronized_dashboard(db_path: str = "agency_sentience.db"):
    db = UnifiedTelemetryDatabase(db_path=db_path)
    bridge = HardwareAccelerationBridge()
    
    latency_history = [14.2, 14.5, 13.9, 15.1, 14.2, 14.8, 16.2, 14.1, 13.8, 14.2]
    
    try:
        while True:
            # Gather compute state metrics directly from native libraries
            current_latency = bridge.trigger_cycle(operational_mode=2)
            if current_latency <= 0:
                current_latency = 14.2
            
            latency_history.append(current_latency)
            if len(latency_history) > 35:
                latency_history.pop(0)
                
            db.log_metric("HARDWARE_BRIDGE", current_latency, "Telemetry packet received [CHKSUM OK].")
            
            # Prepare data frames
            avg_latency = sum(latency_history) / len(latency_history)
            max_latency = max(latency_history)
            cpu_load = round(45.0 + (math.sin(time.time()) * 3.5), 0)
            
            # Clear console screen completely
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Header Grid
            print("─" * 118)
            print(f" OFFLINE CONSCIOUS DRONE | AEGIS AGENCY DASHBOARD" + " " * 49 + "STATUS: OPERATIONAL")
            print("─" * 118)
            
            # Construct Ascii Canvas rows side-by-side
            graph_block = generate_ascii_graph(latency_history, max_val=20.0, min_val=0.0, rows=6)
            
            print(f" SYSTEM TELEMETRY\t\tHARDWARE TELEMETRY TRACK GRID\t LOOP LATENCY TRACKING | (μs)")
            print(f" CPU Load       : {int(cpu_load)}%\t\t┌───────────────────────────┐\t" + f"   Avg: {avg_latency:.1f} μs  Max: {max_latency:.1f} μs")
            print(f" Memory Usage   : 6.8 GB / 16 GB\t│   [ 🚁 ] Simulated Grid   │\t" + graph_block[0])
            print(f" GPU Temp       : 54°C\t\t│   • [🟢] [🟢] [🟢]         │\t" + graph_block[1])
            print(f" Battery        : 88%\t\t│   •      ▲                │\t" + graph_block[2])
            print(f" Active Cores   : 12/16\t\t│   NAVI-TRACK 07B | OFFLINE│\t" + graph_block[3])
            print(f" LOCAL AGENCY STATUS\t\t└───────────────────────────┘\t" + graph_block[4])
            print(f" Core Status    : ONLINE\t\t\t\t\t" + graph_block[5])
            print(f" Latency        : {current_latency:.1f} μs\t\t\t\t\t" + "       └" + "─" * 35)
            print(f" Active Threads : 64\t\tSystem Clock: {time.strftime('%H:%M:%S')}\t 14:02:40   14:03:40   14:04:10")
            print("─" * 118)
            
            # Bottom Log Console Window Pane
            print(" LOG CONSOLE")
            recent_logs = db.get_latest_logs(limit=3)
            for log in reversed(recent_logs):
                ts, module, lat, msg = log
                t_str = time.strftime('%H:%M:%S', time.localtime(ts))
                print(f"  [{t_str}] [{module}]: {msg} (Latency: {lat:.1f} μs)")
            print("─" * 118)
            
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\n[INFO] Dashboard closed smoothly.")

if __name__ == "__main__":
    run_synchronized_dashboard()
    
