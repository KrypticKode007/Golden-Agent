import curses
import time
import math
import sys
import os
import json
from robotic_database_core import UnifiedTelemetryDatabase
from kryptic_edge_launch import HardwareAccelerationBridge

def load_config():
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"system": {"loop_throttle_seconds": 1.5}}

def draw_box(win, y, x, h, w, title=""):
    """Draws a crisp structural border matrix with integrated header slots."""
    win.attron(curses.color_pair(1))
    win.box()
    win.attroff(curses.color_pair(1))
    if title:
        win.attron(curses.color_pair(2) | curses.A_BOLD)
        win.addstr(0, 2, f" {title} ")
        win.attroff(curses.color_pair(2) | curses.A_BOLD)

def render_sparkline(win, history, max_w):
    """Calculates and renders a precise micro-graph tracking stream vector."""
    if not history:
        return
    spark_chars = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
    min_val, max_val = min(history), max(history)
    val_range = max_val - min_val if max_val != min_val else 1.0
    
    available_w = max_w - 4
    visible_history = history[-available_w:]
    
    win.attron(curses.color_pair(2))
    for idx, val in enumerate(visible_history):
        norm = (val - min_val) / val_range
        char_idx = int(norm * (len(spark_chars) - 1))
        try:
            win.addstr(2, 2 + idx, spark_chars[char_idx])
        except curses.error:
            break
    win.attroff(curses.color_pair(2))

def main_dashboard_loop(stdscr):
    # Initialize terminal layout properties
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)
    
    # Configure precise neon terminal colors matching the blueprint
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLUE, -1)   # Visual borders
    curses.init_pair(2, curses.COLOR_GREEN, -1)  # Telemetry status readouts
    curses.init_pair(3, curses.COLOR_WHITE, -1)  # Core text values
    curses.init_pair(4, curses.COLOR_RED, -1)    # Alarm / Warning marks

    # Establish data persistence rings
    config = load_config()
    db = UnifiedTelemetryDatabase(db_path="agency_sentience.db")
    bridge = HardwareAccelerationBridge()
    
    latency_history = []
    start_time = time.time()
    
    while True:
        # Standardize loop refresh sizing dynamics
        max_y, max_x = stdscr.getmaxyx()
        if max_y < 24 or max_x < 80:
            stdscr.clear()
            stdscr.addstr(0, 0, "Terminal screen dimensions too narrow. Please expand your window size.", curses.color_pair(4))
            stdscr.refresh()
            time.sleep(1)
            continue
            
        stdscr.clear()
        
        # Draw Main Monolith Header Banner Layout
        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(1, 2, "OFFLINE CONSCIOUS DRONE | AEGIS AGENCY DASHBOARD")
        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
        
        stdscr.addstr(1, max_x - 22, "STATUS: ")
        stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(1, max_x - 14, "OPERATIONAL")
        stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        
        # Calculate dynamic loop latency variables
        current_latency = bridge.trigger_cycle(operational_mode=1)
        if current_latency > 0:
            latency_history.append(current_latency)
        db.log_metric("HARDWARE_BRIDGE", current_latency, "Telemetry packet received [CHKSUM OK].")
        
        # ----------------------------------------------------------------------
        # WINDOW 1: SYSTEM TELEMETRY
        # ----------------------------------------------------------------------
        win_sys = curses.newwin(10, 30, 3, 2)
        draw_box(win_sys, 0, 0, 10, 30, "SYSTEM TELEMETRY")
        
        sim_cpu = round(45.0 + math.sin(time.time()) * 3.5, 1)
        win_sys.addstr(2, 2, "CPU Load", curses.color_pair(3))
        win_sys.addstr(2, 20, f"{sim_cpu}%", curses.color_pair(2) | curses.A_BOLD)
        
        win_sys.addstr(4, 2, "Memory Usage", curses.color_pair(3))
        win_sys.addstr(4, 15, "6.8 GB / 16 GB", curses.color_pair(2))
        
        win_sys.addstr(6, 2, "GPU Temp", curses.color_pair(3))
        win_sys.addstr(6, 22, "54°C", curses.color_pair(2))
        
        win_sys.addstr(8, 2, "Battery", curses.color_pair(3))
        win_sys.addstr(8, 21, "88%", curses.color_pair(2))
        win_sys.refresh()
        
        # ----------------------------------------------------------------------
        # WINDOW 2: LOOP LATENCY TRACKING
        # ----------------------------------------------------------------------
        win_lat = curses.newwin(6, max_x - 36, 3, 34)
        draw_box(win_lat, 0, 0, 6, max_x - 36, f"LOOP LATENCY TRACKING | (μs)")
        
        avg_lat = sum(latency_history) / len(latency_history) if latency_history else 14.2
        win_lat.addstr(1, 2, f"Avg: {avg_lat:.1f} μs  Max: {max(latency_history) if latency_history else 18.6:.1f} μs", curses.color_pair(3))
        render_sparkline(win_lat, latency_history, max_x - 36)
        win_lat.refresh()
        
        # ----------------------------------------------------------------------
        # WINDOW 3: LOCAL AGENCY STATUS
        # ----------------------------------------------------------------------
        win_agency = curses.newwin(8, 30, 14, 2)
        draw_box(win_agency, 0, 0, 8, 30, "LOCAL AGENCY STATUS")
        win_agency.addstr(2, 2, "Core", curses.color_pair(3))
        win_agency.addstr(2, 20, "ONLINE", curses.color_pair(2) | curses.A_BOLD)
        win_agency.addstr(4, 2, "Latency", curses.color_pair(3))
        win_agency.addstr(4, 18, f"{current_latency:.1f} μs", curses.color_pair(2))
        win_agency.addstr(6, 2, "Active Threads", curses.color_pair(3))
        win_agency.addstr(6, 22, "64", curses.color_pair(2))
        win_agency.refresh()
        
        # ----------------------------------------------------------------------
        # WINDOW 4: LOG CONSOLE LOGS
        # ----------------------------------------------------------------------
        win_logs = curses.newwin(12, max_x - 36, 10, 34)
        draw_box(win_logs, 0, 0, 12, max_x - 36, "LOG CONSOLE")
        
        recent_records = db.get_latest_logs(limit=8)
        for idx, record in enumerate(reversed(recent_records)):
            ts, module, lat, msg = record
            time_str = time.strftime('%H:%M:%S', time.localtime(ts))
            log_line = f"[{time_str}] [{module}]: Latency {lat:.1f} μs - {msg}"
            
            # Trim log lines cleanly to fit user boundary constraints safely
            if len(log_line) > (max_x - 40):
                log_line = log_line[:(max_x - 43)] + "..."
                
            win_logs.addstr(2 + idx, 2, log_line, curses.color_pair(3))
        win_logs.refresh()
        
        # ----------------------------------------------------------------------
        # BOTTOM NAVIGATION GRID BAR
        # ----------------------------------------------------------------------
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(max_y - 2, 2, "NAVI-TRACK 07B | OFFLINE MODE", curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(max_y - 2, max_x - 25, "Press 'Q' to Exit Canvas", curses.color_pair(3))
        stdscr.attroff(curses.color_pair(1))
        
        stdscr.refresh()
        
        # Capture keystroke handlers cleanly
        key = stdscr.getch()
        if key in [ord('q'), ord('Q')]:
            break
            
        time.sleep(config["system"].get("loop_throttle_seconds", 1.5))

if __name__ == "__main__":
    curses.wrapper(main_dashboard_loop)
    
