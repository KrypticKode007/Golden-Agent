# Golden-Agent Aegis Telemetry Dashboard

Autonomous offline edge agent runtime and Aegis mission control telemetry dashboard rewritten as a React application with TypeScript and Tailwind CSS.

## Overview

Golden-Agent is engineered for self-healing edge autonomy in contested, disconnected environments with zero cloud reliance. It provides real-time hardware telemetry monitoring, dynamic power-based loop throttling, sub-millisecond native execution latency tracking, and continuous client telemetry streaming.

## Core Features & Architecture

1. **Unified Drone Flight Display (`src/components/UnifiedFlightDeck.tsx`)**:
   - Integrates real-time 3D drone flight perspectives, procedural geospatial terrain, 3D urban infrastructures, live gimbal camera footage, 360° all-around panoramic views, and 5D spatial array into one glass cockpit.
   - **Real-Time Drone Perspective (1st Person POV)**: Camera mounted directly at the drone's forward sensor gimbal navigating through 3D skyscrapers, suspension bridge, and runway with aerodynamic banking.
   - **All-Around 360° Camera View**: Complete $360^\circ$ panoramic omnidirectional view around the drone with interactive mouse drag-look and auto-spin rotation ($0.5\times, 1.0\times, 2.0\times$).
   - **5D Spatial POV**: Visualizes the 5D perception array (LiDAR/RF point cloud, range rings, temporal trajectory) overlaid on the 3D terrain.
   - **Multi-Cam Directional Surround (Quad-Cam)**: Instant switching between Forward (Nose $0^\circ$), Starboard ($90^\circ$), Aft ($180^\circ$), and Port ($270^\circ$).
   - **Live Gimbal Camera Footage & PIP**: Real-time video canvas with switchable EO Optical, FLIR Thermal, Night Vision (NVG Green), and LiDAR Depth, showing exact coordinates, altitude, heading, laser rangefinder, and building locks.
   - **Camera Slide Focus & Zoom**: Smooth continuous zoom slider ($1.0\times$ to $8.0\times$).

2. **Aegis Agency Telemetry Dashboard (`src/components/TelemetryView.tsx`)**:
   - Replicates the terminal / curses mission-control layout (`gui_dashboard.py`).
   - Live system telemetry: CPU Load (% oscillating curve), Memory Usage (6.8 GB / 16 GB), GPU Temp (°C), and Battery status with power source registers.
   - Loop Latency Tracking with high-resolution microsecond (μs) timing, sparklines, and vector stream tracking (Avg, Max, Min).
   - Local Agency Status with thread-safe execution rings and self-healing diagnostics.
   - Persistent Telemetry Log Console backed by a local storage database engine (`src/services/telemetryStore.ts`).

2. **Tactical Geographical Map & Real-Time Geolocation (`src/components/GeographicalMapView.tsx`)**:
   - Google Maps Platform integration powered by `@vis.gl/react-google-maps`.
   - Real-time GPS tracking with dual mode: physical device geolocation (`navigator.geolocation.watchPosition`) or autonomous flight surveillance vector simulation.
   - Live directional drone marker with heading vector orientation and continuous flight trajectory trail polyline.
   - Dynamic tactical geofence perimeter ring with adjustable radius slider (500m to 5,000m) and automated RTL boundary triggers.
   - Map layers: Tactical Cybernetic Dark (custom Night styling), Satellite imagery, Hybrid, and Terrain.
   - In-map HUD showing real-time latitude/longitude, altitude MSL, ground speed, heading, MGRS grid coordinates, and GNSS satellite constellation lock (RTK/3D Fix).

3. **5D Spatial Array All-Around POV, 3D Terrain & Live Infrastructure Footage (`src/components/Spatial5DViewer.tsx`)**:
   - Real-time 3D geospatial terrain environment with rolling mountain ranges, river valley, highway networks, airport runway, and Google Maps / Earth aesthetic.
   - Procedural 3D urban infrastructure: downtown skyscrapers with illuminated window facades, communication relay masts with blinking red FAA strobes, geodesic radar domes, and bridges.
   - 5D first-person cockpit POV flight mode putting the camera directly at the drone's forward gimbal lens as it navigates through the 3D urban canyons and topography with dynamic banking.
   - Real-time flight controls: interactive airspeed slider (20 to 120 knots), flight altitude slider (50m to 400m MSL), and fullscreen flight camera toggle.
   - Live synchronized multi-spectrum gimbal sensor stream (EO Optical, FLIR Thermal, Night Vision Green, LiDAR Point Depth) with artificial horizon pitch ladders, compass heading tapes, and building target locks.

4. **Native Performance & Memory Benchmarking (`src/components/BenchmarkView.tsx`)**:
   - High-precision numerical hardware loop calculations modeled after the C++17 accelerator (`src/services/hardwareAccelerator.ts`).
   - Replicates `latency_bench.py` and `test_telemetry_edge.py` memory leak assertions (&lt; 15 MB ceiling variance delta).
   - Profile switching: `STANDARD` (5,000 bounds) vs. `STRESS_TESTING` (250,000 bounds).

5. **Real-Time Client Telemetry Streamer (`src/components/StreamingGatewayView.tsx`)**:
   - Replicates `stream_client_telemetry.py` with continuous edge telemetry transmission, secure session tokens (`kryptic_token_session_prod_alpha_007`), SHA256 signature generation, and status validation.

6. **Hardware Configuration & Calibration (`src/components/SettingsConfigView.tsx`)**:
   - Live parameter management for deployment modes, loop throttle intervals, and persistence settings matching `config.json` and `calibration_profile.json`.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server on port 3000
npm run dev

# Build production bundle
npm run build
```

## Hotkeys

- `[1 - 4]`: Navigate across dashboard views (Mission Control, Benchmarks, Streamer, Configuration)
- `[Space]`: Trigger single hardware acceleration cycle
- `[Q]`: Pause or resume real-time background loop
