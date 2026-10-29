#!/usr/bin/env python3
"""
Kryptic-Agent: Real-Time Continuous Client Telemetry Streamer
Actively pumps live synthetic edge metrics to the secure backend gateway.
"""

import time
import random
import sys
import requests
from typing import Dict, Any

class RealTimeClientStreamer:
    def __init__(self, endpoint_url: str = "http://localhost:8000/api/v1/secure-stream"):
        self.endpoint_url = endpoint_url
        self.node_id = "EXTERNAL_CLIENT_NODE_SF_09"
        self.secure_token = "kryptic_token_session_prod_alpha_007"
        self.is_streaming = False

    def generate_live_frame(self) -> Dict[str, Any]:
        """Generates real-time localized variance parameters mimicking live physical hardware."""
        return {
            "node_id": self.node_id,
            "timestamp": time.time(),
            "system_state": "HOMEOSTATIC_HEALTHY",
            "matrix_compute_latency_ms": round(random.uniform(0.39, 0.45), 3),
            "security_epoch_valid": True
        }

    def start_stream(self, interval_seconds: float = 2.0):
        """Spawns an active runtime loop that continuously outputs and transmits data frames."""
        self.is_streaming = True
        print(f"[INFO] Initializing real-time telemetry pipeline for node: {self.node_id}")
        print(f"[INFO] Streaming target: {self.endpoint_url} | Interval: {interval_seconds}s")
        print("[INFO] Press CTRL+C to halt stream execution loop.\n")
        
        try:
            while self.is_streaming:
                payload = self.generate_live_frame()
                headers = {"X-Secure-Token": self.secure_token}
                
                # Timestamp formatting for human-scannable real-time logging output
                current_time = time.strftime('%H:%M:%S')
                
                try:
                    response = requests.post(self.endpoint_url, json=payload, headers=headers, timeout=2)
                    if response.status_code == 200:
                        sig = response.json().get("packet_signature", "N/A")[:16]
                        print(f"[{current_time}] [TX SUCCESS] Latency: {payload['matrix_compute_latency_ms']}ms | Signature Stub: {sig}...")
                    else:
                        print(f"[{current_time}] [TX REFUSED] Gateway dropped block with status: {response.status_code}")
                except requests.exceptions.RequestException:
                    # Non-blocking fallback tracking to keep the terminal loop live if server blips
                    print(f"[{current_time}] [TX PENDING] Waiting for core gateway link to stabilize...")
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n[INFO] Real-time data streaming execution safely intercepted by user. Exiting loop.")
            self.is_streaming = False

if __name__ == "__main__":
    streamer = RealTimeClientStreamer()
    # Fire up the live continuous pipeline execution
    streamer.start_stream(interval_seconds=1.5)
      
