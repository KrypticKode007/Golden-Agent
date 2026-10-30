import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  APIProvider, 
  Map, 
  useMap, 
  Marker, 
  InfoWindow 
} from '@vis.gl/react-google-maps';
import { 
  MapPin, 
  Navigation, 
  Crosshair, 
  Layers, 
  Compass, 
  Radio, 
  ShieldAlert, 
  RotateCw, 
  Play, 
  Square, 
  LocateFixed, 
  Maximize2,
  Share2,
  AlertCircle,
  Clock,
  Gauge
} from 'lucide-react';
import { telemetryDb } from '../services/telemetryStore';

interface Coordinates {
  lat: number;
  lng: number;
  altitude?: number;
  heading?: number;
  speed?: number;
  accuracy?: number;
}

// Tactical Dark Map Style for Google Maps matching Aegis Terminal UI
const TACTICAL_DARK_MAP_STYLE = [
  { elementType: 'geometry', stylers: [{ color: '#090d16' }] },
  { elementType: 'labels.text.stroke', stylers: [{ color: '#090d16' }] },
  { elementType: 'labels.text.fill', stylers: [{ color: '#7488a6' }] },
  {
    featureType: 'administrative.locality',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#38bdf8' }],
  },
  {
    featureType: 'poi',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#64748b' }],
  },
  {
    featureType: 'poi.park',
    elementType: 'geometry',
    stylers: [{ color: '#042f2e' }],
  },
  {
    featureType: 'poi.park',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#2dd4bf' }],
  },
  {
    featureType: 'road',
    elementType: 'geometry',
    stylers: [{ color: '#1e293b' }],
  },
  {
    featureType: 'road',
    elementType: 'geometry.stroke',
    stylers: [{ color: '#0f172a' }],
  },
  {
    featureType: 'road',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#94a3b8' }],
  },
  {
    featureType: 'road.highway',
    elementType: 'geometry',
    stylers: [{ color: '#0284c7' }],
  },
  {
    featureType: 'road.highway',
    elementType: 'geometry.stroke',
    stylers: [{ color: '#0369a1' }],
  },
  {
    featureType: 'road.highway',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#bae6fd' }],
  },
  {
    featureType: 'transit',
    elementType: 'geometry',
    stylers: [{ color: '#1e293b' }],
  },
  {
    featureType: 'water',
    elementType: 'geometry',
    stylers: [{ color: '#031726' }],
  },
  {
    featureType: 'water',
    elementType: 'labels.text.fill',
    stylers: [{ color: '#0284c7' }],
  },
];

// Helper to pan map smoothly
const MapController: React.FC<{ targetCoords: Coordinates; isFollowMode: boolean }> = ({ targetCoords, isFollowMode }) => {
  const map = useMap();
  useEffect(() => {
    if (map && isFollowMode) {
      map.panTo({ lat: targetCoords.lat, lng: targetCoords.lng });
    }
  }, [map, targetCoords, isFollowMode]);
  return null;
};

// Polylines & Geofence Rings Renderer
const TacticalOverlays: React.FC<{ 
  path: Coordinates[]; 
  currentCoords: Coordinates; 
  geofenceRadiusMeters: number;
  showGeofence: boolean;
}> = ({ path, currentCoords, geofenceRadiusMeters, showGeofence }) => {
  const map = useMap();
  const polylineRef = useRef<google.maps.Polyline | null>(null);
  const circleRef = useRef<google.maps.Circle | null>(null);

  // Flight Path Polyline
  useEffect(() => {
    if (!map || typeof window === 'undefined' || !window.google?.maps?.Polyline) return;

    if (!polylineRef.current) {
      polylineRef.current = new window.google.maps.Polyline({
        map,
        strokeColor: '#06b6d4',
        strokeOpacity: 0.85,
        strokeWeight: 3,
        geodesic: true,
      });
    }

    const pathCoords = path.map((p) => ({ lat: p.lat, lng: p.lng }));
    polylineRef.current.setPath(pathCoords);

    return () => {
      if (polylineRef.current) {
        polylineRef.current.setMap(null);
        polylineRef.current = null;
      }
    };
  }, [map, path]);

  // Geofence Circle
  useEffect(() => {
    if (!map || typeof window === 'undefined' || !window.google?.maps?.Circle) return;

    if (!circleRef.current) {
      circleRef.current = new window.google.maps.Circle({
        map: showGeofence ? map : null,
        center: { lat: currentCoords.lat, lng: currentCoords.lng },
        radius: geofenceRadiusMeters,
        strokeColor: '#ef4444',
        strokeOpacity: 0.7,
        strokeWeight: 1.5,
        fillColor: '#ef4444',
        fillOpacity: 0.08,
      });
    } else {
      circleRef.current.setMap(showGeofence ? map : null);
      circleRef.current.setCenter({ lat: currentCoords.lat, lng: currentCoords.lng });
      circleRef.current.setRadius(geofenceRadiusMeters);
    }

    return () => {
      if (circleRef.current) {
        circleRef.current.setMap(null);
        circleRef.current = null;
      }
    };
  }, [map, currentCoords, geofenceRadiusMeters, showGeofence]);

  return null;
};

export const GeographicalMapView: React.FC = () => {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

  // Real-time GPS State
  const [currentCoords, setCurrentCoords] = useState<Coordinates>({
    lat: 37.7749, // Default: SF Bay Area Tactical Edge Node
    lng: -122.4194,
    altitude: 142.5,
    heading: 42.0,
    speed: 18.5,
    accuracy: 3.2,
  });

  const [pathHistory, setPathHistory] = useState<Coordinates[]>([
    { lat: 37.7710, lng: -122.4240 },
    { lat: 37.7725, lng: -122.4220 },
    { lat: 37.7738, lng: -122.4205 },
    { lat: 37.7749, lng: -122.4194 },
  ]);

  const [isLiveDeviceGps, setIsLiveDeviceGps] = useState<boolean>(false);
  const [isSimulatingFlight, setIsSimulatingFlight] = useState<boolean>(true);
  const [isFollowMode, setIsFollowMode] = useState<boolean>(true);
  const [mapTypeId, setMapTypeId] = useState<'roadmap' | 'satellite' | 'hybrid' | 'terrain'>('roadmap');
  const [geofenceRadius, setGeofenceRadius] = useState<number>(1500); // meters
  const [showGeofence, setShowGeofence] = useState<boolean>(true);
  const [gpsFixQuality, setGpsFixQuality] = useState<'3D_FIX' | 'DGPS' | 'RTK_FIXED'>('RTK_FIXED');
  const [satellitesLocked, setSatellitesLocked] = useState<number>(16);

  const watchIdRef = useRef<number | null>(null);
  const simTimerRef = useRef<any>(null);

  // Real-Time Browser Geolocation Watcher
  const toggleLiveDeviceGps = useCallback(() => {
    if (isLiveDeviceGps) {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
        watchIdRef.current = null;
      }
      setIsLiveDeviceGps(false);
      telemetryDb.logMetric('GPS_PROVIDER', 1.2, 'Switched to autonomous simulated flight telemetry.');
    } else {
      if ('geolocation' in navigator) {
        setIsSimulatingFlight(false);
        setIsLiveDeviceGps(true);
        telemetryDb.logMetric('GPS_PROVIDER', 0.8, 'Acquiring physical device GPS hardware registers...');

        watchIdRef.current = navigator.geolocation.watchPosition(
          (pos) => {
            const newCoords: Coordinates = {
              lat: pos.coords.latitude,
              lng: pos.coords.longitude,
              altitude: pos.coords.altitude || 45.0,
              heading: pos.coords.heading || 0.0,
              speed: pos.coords.speed || 0.0,
              accuracy: pos.coords.accuracy,
            };
            setCurrentCoords(newCoords);
            setPathHistory((prev) => [...prev.slice(-80), newCoords]);
            setSatellitesLocked(Math.min(24, Math.max(12, Math.round(20 - (pos.coords.accuracy / 5)))));
            telemetryDb.logMetric(
              'GPS_PROVIDER',
              0.5,
              `Device GPS position locked: ${newCoords.lat.toFixed(5)}, ${newCoords.lng.toFixed(5)} (Acc: ±${pos.coords.accuracy.toFixed(1)}m)`
            );
          },
          (err) => {
            console.warn('Geolocation failed or denied, reverting to simulation:', err);
            setIsLiveDeviceGps(false);
            setIsSimulatingFlight(true);
            telemetryDb.logMetric('GPS_PROVIDER', 2.0, `Physical GPS unavailable (${err.message}). Defaulted to edge navigation simulation.`);
          },
          { enableHighAccuracy: true, timeout: 8000, maximumAge: 1000 }
        );
      } else {
        alert('Geolocation is not supported by your environment.');
      }
    }
  }, [isLiveDeviceGps]);

  // Autonomous Drone Flight Path Simulation (Real-time waypoint progression)
  useEffect(() => {
    if (!isSimulatingFlight || isLiveDeviceGps) return;

    let step = 0;
    simTimerRef.current = setInterval(() => {
      step += 0.08;
      // Figure-8 tactical surveillance flight vector around SF Bay
      const deltaLat = Math.sin(step) * 0.0035;
      const deltaLng = Math.sin(step * 2) * 0.0045;
      const baseLat = 37.7749;
      const baseLng = -122.4194;

      const newLat = baseLat + deltaLat;
      const newLng = baseLng + deltaLng;
      const heading = (Math.atan2(deltaLng, deltaLat) * 180 / Math.PI + 360) % 360;
      const alt = 140 + Math.sin(step * 1.5) * 12;
      const spd = 16 + Math.cos(step) * 3;

      const newPoint: Coordinates = {
        lat: Number(newLat.toFixed(6)),
        lng: Number(newLng.toFixed(6)),
        altitude: Number(alt.toFixed(1)),
        heading: Number(heading.toFixed(1)),
        speed: Number(spd.toFixed(1)),
        accuracy: 1.8,
      };

      setCurrentCoords(newPoint);
      setPathHistory((prev) => [...prev.slice(-90), newPoint]);

      if (Math.round(step * 10) % 25 === 0) {
        telemetryDb.logMetric(
          'FLIGHT_NAV',
          0.9,
          `Waypoint vector: Lat ${newPoint.lat.toFixed(4)}, Lng ${newPoint.lng.toFixed(4)}, Alt ${newPoint.altitude}m [OK]`
        );
      }
    }, 1500);

    return () => {
      if (simTimerRef.current) clearInterval(simTimerRef.current);
    };
  }, [isSimulatingFlight, isLiveDeviceGps]);

  // Clean up geolocation on unmount
  useEffect(() => {
    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, []);

  return (
    <div className="space-y-4">
      {/* Top Banner Notice */}
      <div className="flex flex-wrap items-center justify-between text-xs bg-slate-900/60 border border-slate-800 px-3.5 py-2 rounded">
        <div className="flex items-center space-x-2 text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>GEOGRAPHICAL MAP & REAL-TIME GPS AUTONOMOUS POSITIONING MATRIX</span>
        </div>
        <div className="flex items-center space-x-3 text-slate-400 font-mono">
          <span>GPS FIX: <strong className="text-emerald-300">{gpsFixQuality}</strong></span>
          <span>•</span>
          <span>SATELLITES: <strong className="text-cyan-300">{satellitesLocked} LOCKED</strong></span>
          <span>•</span>
          <span>ACCURACY: <strong className="text-emerald-400">±{currentCoords.accuracy?.toFixed(1) || '1.8'}m</strong></span>
        </div>
      </div>

      {/* Main Grid: Map (8 cols) + Tactical Mission Telemetry (4 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* MAP CONTAINER */}
        <div className="lg:col-span-8 bg-slate-950 border border-blue-900/70 rounded shadow-lg overflow-hidden flex flex-col justify-between relative group">
          {/* Header Map Toolbar */}
          <div className="border-b border-blue-900/60 px-4 py-2 bg-slate-900/80 backdrop-blur flex flex-wrap items-center justify-between gap-3 z-10">
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-bold tracking-wider text-slate-200 uppercase font-mono">
                Real-Time Drone Position Map
              </span>
            </div>

            {/* Map Style & Layer Selectors */}
            <div className="flex items-center space-x-2 text-xs font-mono">
              <div className="flex items-center space-x-1 bg-slate-950 p-0.5 rounded border border-slate-800 text-[11px]">
                {[
                  { id: 'roadmap', label: 'Tactical Dark' },
                  { id: 'satellite', label: 'Satellite' },
                  { id: 'hybrid', label: 'Hybrid' },
                  { id: 'terrain', label: 'Terrain' },
                ].map((m) => (
                  <button
                    key={m.id}
                    onClick={() => setMapTypeId(m.id as any)}
                    className={`px-2 py-0.5 rounded transition cursor-pointer ${
                      mapTypeId === m.id
                        ? 'bg-cyan-950 text-cyan-300 border border-cyan-500 font-bold'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {m.label}
                  </button>
                ))}
              </div>

              {/* Follow Camera Toggle */}
              <button
                onClick={() => setIsFollowMode(!isFollowMode)}
                className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] border cursor-pointer ${
                  isFollowMode
                    ? 'bg-emerald-950 border-emerald-500 text-emerald-300'
                    : 'bg-slate-900 border-slate-800 text-slate-400'
                }`}
              >
                <LocateFixed className="w-3 h-3" />
                <span>{isFollowMode ? 'Tracking' : 'Free Pan'}</span>
              </button>
            </div>
          </div>

          {/* Interactive Google Map Canvas */}
          <div className="w-full h-[480px] relative">
            <APIProvider apiKey={apiKey}>
              <Map
                center={{ lat: currentCoords.lat, lng: currentCoords.lng }}
                zoom={15}
                mapTypeId={mapTypeId}
                styles={mapTypeId === 'roadmap' ? TACTICAL_DARK_MAP_STYLE : undefined}
                disableDefaultUI={false}
                zoomControl={true}
                fullscreenControl={false}
                streetViewControl={false}
                className="w-full h-full"
              >
                {/* Auto center controller */}
                <MapController targetCoords={currentCoords} isFollowMode={isFollowMode} />

                {/* Flight path trail and geofence overlays */}
                <TacticalOverlays
                  path={pathHistory}
                  currentCoords={currentCoords}
                  geofenceRadiusMeters={geofenceRadius}
                  showGeofence={showGeofence}
                />

                {/* Drone Live Position Marker */}
                <Marker
                  position={{ lat: currentCoords.lat, lng: currentCoords.lng }}
                  title="Aegis Drone Active Vector"
                  icon={
                    typeof window !== 'undefined' && window.google?.maps?.SymbolPath
                      ? {
                          path: window.google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                          scale: 6,
                          fillColor: '#06b6d4',
                          fillOpacity: 1.0,
                          strokeColor: '#ffffff',
                          strokeWeight: 2,
                          rotation: currentCoords.heading || 0,
                        }
                      : undefined
                  }
                />
              </Map>
            </APIProvider>

            {/* In-Map HUD Telemetry Overlay */}
            <div className="absolute top-3 left-3 pointer-events-none bg-slate-950/85 backdrop-blur border border-cyan-900/60 p-2.5 rounded font-mono text-[11px] space-y-1 shadow-lg">
              <div className="text-cyan-400 font-bold flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                <span>GEO-LOCK: {currentCoords.lat.toFixed(5)}°N, {Math.abs(currentCoords.lng).toFixed(5)}°W</span>
              </div>
              <div className="text-slate-300">ALTITUDE: <strong className="text-emerald-400">{currentCoords.altitude}m MSL</strong></div>
              <div className="text-slate-300">GROUND SPEED: <strong className="text-amber-400">{currentCoords.speed} km/h</strong></div>
              <div className="text-slate-300">HEADING: <strong className="text-cyan-300">{currentCoords.heading}° T</strong></div>
            </div>

            {/* Quick Geolocation Mode Bar */}
            <div className="absolute bottom-3 right-3 flex items-center space-x-2 z-10">
              <button
                onClick={toggleLiveDeviceGps}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-mono font-semibold shadow-md transition cursor-pointer border ${
                  isLiveDeviceGps
                    ? 'bg-emerald-950 text-emerald-300 border-emerald-500 glow-green'
                    : 'bg-slate-900/90 text-slate-300 border-slate-700 hover:bg-slate-800'
                }`}
              >
                <Radio className={`w-3.5 h-3.5 ${isLiveDeviceGps ? 'animate-pulse text-emerald-400' : 'text-slate-400'}`} />
                <span>{isLiveDeviceGps ? 'Live Device GPS Active' : 'Use Device GPS'}</span>
              </button>

              <button
                onClick={() => {
                  setPathHistory([{ lat: currentCoords.lat, lng: currentCoords.lng }]);
                }}
                className="bg-slate-900/90 hover:bg-slate-800 text-slate-300 border border-slate-700 px-2.5 py-1.5 rounded text-xs font-mono cursor-pointer transition"
                title="Reset flight trajectory trail"
              >
                Clear Trail
              </button>
            </div>
          </div>

          {/* Bottom Coordinates Strip */}
          <div className="border-t border-blue-900/40 p-2.5 bg-slate-900/60 flex flex-wrap items-center justify-between text-xs font-mono text-slate-400">
            <div className="flex items-center space-x-4">
              <span>MGRS GRID: <strong className="text-slate-200">10SEG 0532 8094</strong></span>
              <span>•</span>
              <span>DATUM: <strong className="text-slate-200">WGS-84</strong></span>
              <span>•</span>
              <span>EPE: <strong className="text-emerald-400">±1.8m</strong></span>
            </div>

            <div className="text-slate-400">
              TRAJECTORY POINTS: <strong className="text-cyan-300">{pathHistory.length}</strong>
            </div>
          </div>
        </div>

        {/* RIGHT: TACTICAL FLIGHT NAVIGATION & GEOFENCE SUITE (4 cols) */}
        <div className="lg:col-span-4 bg-slate-950 border border-blue-900/70 rounded shadow-lg overflow-hidden flex flex-col justify-between">
          <div className="border-b border-blue-900/60 px-4 py-2.5 bg-slate-900/80 flex items-center justify-between">
            <span className="text-xs font-bold tracking-wider text-blue-400 uppercase flex items-center space-x-1.5 font-mono">
              <Navigation className="w-4 h-4 text-cyan-400" />
              <span>Tactical Geonav Telemetry</span>
            </span>
            <span className="text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800 px-1.5 py-0.5 rounded font-mono font-bold">
              RTK-LOCKED
            </span>
          </div>

          <div className="p-4 space-y-4 font-mono text-xs flex-1">
            {/* Real-Time Coordinate Readout Card */}
            <div className="bg-slate-900/70 p-3 rounded border border-slate-800 space-y-2">
              <div className="flex justify-between items-center text-slate-400 text-[11px] uppercase border-b border-slate-800/80 pb-1">
                <span>Spatial Coordinate Register</span>
                <span className="text-cyan-400">REAL-TIME</span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-slate-500 text-[10px] block">LATITUDE</span>
                  <span className="text-slate-200 font-bold text-sm">{currentCoords.lat.toFixed(6)}°</span>
                </div>
                <div>
                  <span className="text-slate-500 text-[10px] block">LONGITUDE</span>
                  <span className="text-slate-200 font-bold text-sm">{currentCoords.lng.toFixed(6)}°</span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 pt-1 border-t border-slate-800/60 text-[11px]">
                <div>
                  <span className="text-slate-500 text-[10px] block">ALT (MSL)</span>
                  <span className="text-emerald-400 font-bold">{currentCoords.altitude}m</span>
                </div>
                <div>
                  <span className="text-slate-500 text-[10px] block">SPEED</span>
                  <span className="text-amber-400 font-bold">{currentCoords.speed} km/h</span>
                </div>
                <div>
                  <span className="text-slate-500 text-[10px] block">HEADING</span>
                  <span className="text-cyan-400 font-bold">{currentCoords.heading}°</span>
                </div>
              </div>
            </div>

            {/* Geofence Alert Radius Ring */}
            <div className="bg-slate-900/70 p-3 rounded border border-slate-800 space-y-2.5">
              <div className="flex justify-between items-center text-slate-300">
                <span className="flex items-center space-x-1.5 text-xs font-bold text-red-400 uppercase">
                  <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
                  <span>Tactical Geofence Perimeter</span>
                </span>
                <button
                  onClick={() => setShowGeofence(!showGeofence)}
                  className={`text-[10px] px-1.5 py-0.5 rounded border cursor-pointer ${
                    showGeofence ? 'bg-red-950 text-red-300 border-red-700' : 'bg-slate-900 text-slate-500 border-slate-800'
                  }`}
                >
                  {showGeofence ? 'Active' : 'Disabled'}
                </button>
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-400">
                <span>Perimeter Radius:</span>
                <span className="text-red-400 font-bold">{geofenceRadius} meters ({(geofenceRadius / 1000).toFixed(1)} km)</span>
              </div>

              <input
                type="range"
                min="500"
                max="5000"
                step="250"
                value={geofenceRadius}
                onChange={(e) => setGeofenceRadius(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-red-500"
              />

              <div className="text-[10px] text-slate-400 leading-tight">
                Self-healing autopilot will trigger automated return-to-launch (RTL) protocol if edge drone exits perimeter radius.
              </div>
            </div>

            {/* Satellite Constellation Status */}
            <div className="bg-slate-900/70 p-3 rounded border border-slate-800 space-y-1.5">
              <div className="flex justify-between text-slate-400 text-[11px]">
                <span>GNSS Constellation:</span>
                <span className="text-emerald-400 font-bold">GPS + GLONASS + GALILEO</span>
              </div>
              <div className="flex justify-between text-slate-400 text-[11px]">
                <span>Satellites in View / Locked:</span>
                <span className="text-cyan-300 font-bold">22 / {satellitesLocked} SVs</span>
              </div>
              <div className="flex justify-between text-slate-400 text-[11px]">
                <span>DOP (Dilution of Precision):</span>
                <span className="text-emerald-400 font-bold">HDOP: 0.8 / VDOP: 1.1</span>
              </div>
            </div>
          </div>

          <div className="border-t border-blue-900/40 px-3 py-2 bg-slate-900/50 text-[10px] font-mono text-slate-400 flex justify-between items-center">
            <span>NAV ENGINE: HARDWARE REGISTER</span>
            <span className="text-emerald-400 font-bold">SYNCHRONIZED</span>
          </div>
        </div>
      </div>
    </div>
  );
};
