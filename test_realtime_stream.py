#!/usr/bin/env python3
"""
Kryptic-Agent: Real-Time Stream Layer Integrity Checks
"""

import pytest
import time
from stream_client_telemetry import RealTimeClientStreamer

def test_stream_frame_generation_cadence():
    """Verify that successive live metric generations dynamically update timestamps."""
    streamer = RealTimeClientStreamer()
    
    frame_one = streamer.generate_live_frame()
    time.sleep(0.01)
    frame_two = streamer.generate_live_frame()
    
    assert frame_one["timestamp"] != frame_two["timestamp"]
    assert frame_one["matrix_compute_latency_ms"] != frame_two["matrix_compute_latency_ms"]

def test_streamer_initialization_state():
    """Confirm the continuous streaming runtime starts in a clean homeostatic inactive state."""
    streamer = RealTimeClientStreamer()
    assert streamer.is_streaming is False
  
