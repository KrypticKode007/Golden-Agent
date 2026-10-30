import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';
import { 
  Camera, 
  RotateCw, 
  ZoomIn, 
  ZoomOut, 
  Eye, 
  Crosshair, 
  Layers, 
  Maximize2, 
  Minimize2, 
  Sliders, 
  Compass, 
  Target, 
  Radio, 
  ShieldAlert,
  Play,
  Pause,
  RefreshCcw,
  Sparkles,
  Building,
  Navigation,
  Plane,
  Gauge,
  MapPin,
  Grid,
  Video,
  RadioTower,
  CornerDownRight
} from 'lucide-react';

interface UnifiedFlightDeckProps {
  currentLatencyMicros?: number;
  batteryPct?: number;
}

// Procedural Canvas Texture Generator for Satellite Terrain (Google Maps / Earth 3D aesthetic)
const createSatelliteTerrainTexture = (): THREE.CanvasTexture => {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d')!;

  ctx.fillStyle = '#0a101d';
  ctx.fillRect(0, 0, 1024, 1024);

  // Topo terrain elevation contours & biome patches
  for (let i = 0; i < 60; i++) {
    const rx = Math.random() * 1024;
    const ry = Math.random() * 1024;
    const rad = 60 + Math.random() * 140;
    const grad = ctx.createRadialGradient(rx, ry, 10, rx, ry, rad);
    grad.addColorStop(0, '#111d2e');
    grad.addColorStop(0.5, '#0d1827');
    grad.addColorStop(1, '#080d18');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(rx, ry, rad, 0, Math.PI * 2);
    ctx.fill();
  }

  // Winding River / Water Body
  ctx.strokeStyle = '#0284c7';
  ctx.lineWidth = 42;
  ctx.beginPath();
  ctx.moveTo(0, 320);
  ctx.bezierCurveTo(340, 480, 680, 240, 1024, 450);
  ctx.stroke();

  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 12;
  ctx.beginPath();
  ctx.moveTo(0, 320);
  ctx.bezierCurveTo(340, 480, 680, 240, 1024, 450);
  ctx.stroke();

  // Urban Road Network & Highway
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 10;
  ctx.beginPath();
  ctx.moveTo(512, 0); ctx.lineTo(512, 1024);
  ctx.moveTo(0, 640); ctx.lineTo(1024, 640);
  ctx.moveTo(100, 100); ctx.lineTo(900, 900);
  ctx.stroke();

  ctx.strokeStyle = '#f59e0b';
  ctx.lineWidth = 1.5;
  ctx.setLineDash([8, 8]);
  ctx.beginPath();
  ctx.moveTo(512, 0); ctx.lineTo(512, 1024);
  ctx.moveTo(0, 640); ctx.lineTo(1024, 640);
  ctx.stroke();
  ctx.setLineDash([]);

  // Airport Runway 28L
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(440, 680, 144, 300);
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 2;
  ctx.strokeRect(440, 680, 144, 300);

  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 3;
  ctx.setLineDash([16, 16]);
  ctx.beginPath();
  ctx.moveTo(512, 690); ctx.lineTo(512, 970);
  ctx.stroke();
  ctx.setLineDash([]);

  // MGRS Coordinate Grid Lines
  ctx.strokeStyle = 'rgba(6, 182, 212, 0.12)';
  ctx.lineWidth = 1;
  for (let x = 0; x < 1024; x += 128) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 1024); ctx.stroke();
  }
  for (let y = 0; y < 1024; y += 128) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(1024, y); ctx.stroke();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  return texture;
};

// Procedural Building Window Texture
const createBuildingFacadeTexture = (): THREE.CanvasTexture => {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 512;
  const ctx = canvas.getContext('2d')!;

  ctx.fillStyle = '#090d16';
  ctx.fillRect(0, 0, 256, 512);

  const cols = 8;
  const rows = 24;
  const w = 256 / cols;
  const h = 512 / rows;

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const isLit = Math.random() > 0.45;
      if (isLit) {
        const tone = Math.random();
        ctx.fillStyle = tone > 0.7 ? '#38bdf8' : tone > 0.3 ? '#fef08a' : '#0284c7';
      } else {
        ctx.fillStyle = '#0f172a';
      }
      ctx.fillRect(c * w + 4, r * h + 4, w - 8, h - 8);
    }
  }

  return new THREE.CanvasTexture(canvas);
};

export const UnifiedFlightDeck: React.FC<UnifiedFlightDeckProps> = ({
  currentLatencyMicros = 14.2,
  batteryPct = 88,
}) => {
  // DOM Refs
  const mountRef = useRef<HTMLDivElement>(null);
  const videoCanvasRef = useRef<HTMLCanvasElement>(null);

  // Integrated Flight Display Modes
  // 1. DRONE_POV (Realtime Drone Perspective Cockpit)
  // 2. AROUND_360 (All Around 360° Camera View)
  // 3. SPATIAL_5D (Spatial 5D Perception Array)
  // 4. QUAD_CAM (4-Way Multi-Cam Surround Surveillance)
  const [activeDeckMode, setActiveDeckMode] = useState<'DRONE_POV' | 'AROUND_360' | 'SPATIAL_5D' | 'QUAD_CAM'>('DRONE_POV');

  // Camera Slide In/Out Focus & Zoom
  const [zoomFactor, setZoomFactor] = useState<number>(2.0); // 1.0x to 10.0x
  const [cameraDistance, setCameraDistance] = useState<number>(14.0); // Orbit radius

  // 360 Spin View Controls
  const [isAutoSpinning, setIsAutoSpinning] = useState<boolean>(false);
  const [spinSpeed, setSpinSpeed] = useState<number>(1.0);

  // Multi-Cam Direction in AROUND_360 / QUAD_CAM
  const [selectedCamAngle, setSelectedCamAngle] = useState<'NOSE_0' | 'RIGHT_90' | 'AFT_180' | 'LEFT_270'>('NOSE_0');

  // Live Camera Sensor Spectrum
  const [footageSpectrum, setFootageSpectrum] = useState<'EO_COLOR' | 'FLIR_THERMAL' | 'NIGHT_VISION' | 'LIDAR_DEPTH'>('EO_COLOR');

  // Flight Controls
  const [flightSpeedKnots, setFlightSpeedKnots] = useState<number>(68);
  const [flightAltitudeMeters, setFlightAltitudeMeters] = useState<number>(195);
  const [showLivePip, setShowLivePip] = useState<boolean>(true);
  const [showHudOverlay, setShowHudOverlay] = useState<boolean>(true);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  // Live Telemetry Readouts
  const [liveGeoCoords, setLiveGeoCoords] = useState<{ lat: number; lng: number; alt: number }>({
    lat: 37.7749,
    lng: -122.4194,
    alt: 195,
  });
  const [currentHeadingDeg, setCurrentHeadingDeg] = useState<number>(42);
  const [lockedTargetName, setLockedTargetName] = useState<string>('SKYTOWER-01 (DOWNTOWN)');
  const [targetRangeMeters, setTargetRangeMeters] = useState<number>(268);
  const [timecodeStr, setTimecodeStr] = useState<string>('00:00:00:00');

  // Three.js Scene References
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const droneGroupRef = useRef<THREE.Group | null>(null);
  const rotorBladesRef = useRef<THREE.Mesh[]>([]);
  const spatialPointsRef = useRef<THREE.Points | null>(null);
  const beaconLightsRef = useRef<THREE.PointLight[]>([]);

  // Orbit Interaction
  const isDraggingRef = useRef<boolean>(false);
  const prevMousePosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const sphericalRef = useRef<{ theta: number; phi: number; radius: number }>({
    theta: 0.3,
    phi: 1.15,
    radius: 14.0,
  });

  useEffect(() => {
    sphericalRef.current.radius = cameraDistance;
  }, [cameraDistance]);

  // Setup 3D Geospatial World in Three.js
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // 1. Scene & Environment Fog
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    scene.background = new THREE.Color(0x030712); // Deep night sky
    scene.fog = new THREE.FogExp2(0x030712, 0.010);

    // 2. Camera
    const aspect = container.clientWidth / container.clientHeight;
    const camera = new THREE.PerspectiveCamera(55, aspect, 0.5, 600);
    cameraRef.current = camera;
    camera.position.set(0, 20, 25);

    // 3. WebGL Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    rendererRef.current = renderer;
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.35;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // 4. Lighting Rig
    const ambientLight = new THREE.AmbientLight(0x0c4a6e, 1.5);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x38bdf8, 2.8);
    dirLight.position.set(60, 90, 50);
    scene.add(dirLight);

    const rimLight = new THREE.DirectionalLight(0x10b981, 1.2);
    rimLight.position.set(-50, 30, -50);
    scene.add(rimLight);

    // 5. GEOSPATIAL 3D TERRAIN MESH
    const terrainSize = 240;
    const terrainSegments = 72;
    const terrainGeo = new THREE.PlaneGeometry(terrainSize, terrainSize, terrainSegments, terrainSegments);
    terrainGeo.rotateX(-Math.PI / 2);

    const posAttr = terrainGeo.attributes.position;
    for (let i = 0; i < posAttr.count; i++) {
      const vx = posAttr.getX(i);
      const vz = posAttr.getZ(i);
      const dist = Math.sqrt(vx * vx + vz * vz);
      let height = 0;
      if (dist > 45) {
        height = Math.sin(vx * 0.05) * Math.cos(vz * 0.05) * 18 + (dist - 45) * 0.22;
      } else {
        height = Math.sin(vx * 0.08) * Math.cos(vz * 0.08) * 1.8;
      }
      posAttr.setY(i, Math.max(-0.5, height));
    }
    terrainGeo.computeVertexNormals();

    const terrainTexture = createSatelliteTerrainTexture();
    const terrainMat = new THREE.MeshStandardMaterial({
      map: terrainTexture,
      roughness: 0.72,
      metalness: 0.18,
      flatShading: true,
    });
    const terrainMesh = new THREE.Mesh(terrainGeo, terrainMat);
    terrainMesh.position.y = -2;
    scene.add(terrainMesh);

    // 6. URBAN INFRASTRUCTURE CLUSTERS (Buildings, Towers, Bridges, Radars)
    const infrastructureGroup = new THREE.Group();
    const buildingMat = new THREE.MeshStandardMaterial({
      map: createBuildingFacadeTexture(),
      roughness: 0.35,
      metalness: 0.75,
    });
    const roofMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
    const beaconLights: THREE.PointLight[] = [];

    const buildingDefs = [
      { x: -18, z: -12, w: 7, h: 32, d: 7, label: 'SKYTOWER-01' },
      { x: -8, z: -16, w: 6, h: 42, d: 6, label: 'TITAN-TOWER' },
      { x: 2, z: -18, w: 8, h: 26, d: 8, label: 'FINANCE-HUB' },
      { x: 14, z: -14, w: 7, h: 35, d: 7, label: 'AERO-CAMPUS' },
      { x: -15, z: 4, w: 6, h: 20, d: 6, label: 'CIVIC-PLAZA' },
      { x: -26, z: -2, w: 8, h: 28, d: 8, label: 'TELECOM-HQ' },
      { x: 20, z: -2, w: 7, h: 27, d: 7, label: 'METRO-CORE' },
      { x: 10, z: 6, w: 6, h: 18, d: 6, label: 'LOGISTICS-01' },
      { x: -6, z: 12, w: 5, h: 16, d: 5, label: 'POWER-SUBSTATION' },
      { x: 24, z: 14, w: 8, h: 22, d: 8, label: 'DEPOT-ALPHA' },
      { x: -30, z: 18, w: 7, h: 18, d: 7, label: 'ENERGY-GRID' },
      { x: 16, z: 24, w: 6, h: 20, d: 6, label: 'CARGO-TERMINAL' },
    ];

    buildingDefs.forEach((b) => {
      const bldgGeo = new THREE.BoxGeometry(b.w, b.h, b.d);
      const bldg = new THREE.Mesh(bldgGeo, buildingMat);
      bldg.position.set(b.x, b.h / 2 - 2, b.z);
      infrastructureGroup.add(bldg);

      // Helipad roof
      const roofGeo = new THREE.BoxGeometry(b.w * 0.75, 1.2, b.d * 0.75);
      const roof = new THREE.Mesh(roofGeo, roofMat);
      roof.position.set(b.x, b.h - 1.4, b.z);
      infrastructureGroup.add(roof);

      // Red flashing beacon
      const strobe = new THREE.PointLight(0xef4444, 2.0, 14);
      strobe.position.set(b.x, b.h - 0.4, b.z);
      infrastructureGroup.add(strobe);
      beaconLights.push(strobe);
    });

    // Communication Mast Tower
    const towerGeo = new THREE.CylinderGeometry(0.2, 2.0, 42, 6);
    const towerMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.9, roughness: 0.2 });
    const tower = new THREE.Mesh(towerGeo, towerMat);
    tower.position.set(-38, 19, -28);
    infrastructureGroup.add(tower);

    const towerStrobe = new THREE.PointLight(0xef4444, 3.5, 25);
    towerStrobe.position.set(-38, 40, -28);
    infrastructureGroup.add(towerStrobe);
    beaconLights.push(towerStrobe);

    // Radar Dome
    const domeGeo = new THREE.SphereGeometry(5.0, 18, 14, 0, Math.PI * 2, 0, Math.PI / 2);
    const domeMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.3 });
    const dome = new THREE.Mesh(domeGeo, domeMat);
    dome.position.set(34, -2, -34);
    infrastructureGroup.add(dome);

    // Bridge over River
    const bridgeGeo = new THREE.BoxGeometry(6, 0.8, 65);
    const bridgeMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.8 });
    const bridge = new THREE.Mesh(bridgeGeo, bridgeMat);
    bridge.position.set(0, 1.5, -42);
    infrastructureGroup.add(bridge);

    scene.add(infrastructureGroup);
    beaconLightsRef.current = beaconLights;

    // 7. AEGIS AUTONOMOUS DRONE 3D MODEL
    const droneGroup = new THREE.Group();
    droneGroupRef.current = droneGroup;

    // Main Carbon Fuselage
    const fuselageGeo = new THREE.BoxGeometry(1.6, 0.45, 2.4);
    const carbonMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.35, metalness: 0.85 });
    const fuselage = new THREE.Mesh(fuselageGeo, carbonMat);
    droneGroup.add(fuselage);

    // Canopy
    const canopyGeo = new THREE.ConeGeometry(0.7, 1.4, 5);
    const canopyMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.2, metalness: 0.9 });
    const canopy = new THREE.Mesh(canopyGeo, canopyMat);
    canopy.rotation.x = Math.PI / 2;
    canopy.position.set(0, 0.3, 0.2);
    droneGroup.add(canopy);

    // Rotor Arms
    const armGeo = new THREE.CylinderGeometry(0.06, 0.06, 2.4, 8);
    const armMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.7, roughness: 0.4 });
    const arm1 = new THREE.Mesh(armGeo, armMat);
    arm1.rotation.z = Math.PI / 2; arm1.rotation.y = Math.PI / 4;
    droneGroup.add(arm1);

    const arm2 = new THREE.Mesh(armGeo, armMat);
    arm2.rotation.z = Math.PI / 2; arm2.rotation.y = -Math.PI / 4;
    droneGroup.add(arm2);

    // Rotor Blades
    const rotorBladeMeshes: THREE.Mesh[] = [];
    const bladeGeo = new THREE.BoxGeometry(1.5, 0.02, 0.12);
    const bladeMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.4 });

    [
      [0.85, 0.1, 0.85],
      [-0.85, 0.1, 0.85],
      [0.85, 0.1, -0.85],
      [-0.85, 0.1, -0.85],
    ].forEach(([x, y, z]) => {
      const blade = new THREE.Mesh(bladeGeo, bladeMat);
      blade.position.set(x, y + 0.15, z);
      droneGroup.add(blade);
      rotorBladeMeshes.push(blade);
    });
    rotorBladesRef.current = rotorBladeMeshes;

    // Gimbal Camera Eye
    const gimbalGeo = new THREE.SphereGeometry(0.32, 16, 16);
    const gimbalMat = new THREE.MeshStandardMaterial({ color: 0x000000, metalness: 0.95 });
    const gimbal = new THREE.Mesh(gimbalGeo, gimbalMat);
    gimbal.position.set(0, -0.28, 1.0);
    droneGroup.add(gimbal);

    // Green Sensor Lens
    const lensGeo = new THREE.CylinderGeometry(0.14, 0.14, 0.1, 16);
    const lensMat = new THREE.MeshBasicMaterial({ color: 0x22c55e });
    const lens = new THREE.Mesh(lensGeo, lensMat);
    lens.rotation.x = Math.PI / 2;
    lens.position.set(0, -0.28, 1.25);
    droneGroup.add(lens);

    scene.add(droneGroup);

    // 8. 5D SPATIAL PERCEPTION MATRIX & RANGE RINGS
    const pointsCount = 420;
    const pointsGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(pointsCount * 3);
    const colors = new Float32Array(pointsCount * 3);

    for (let i = 0; i < pointsCount; i++) {
      const px = (Math.random() - 0.5) * 90;
      const py = 2 + Math.random() * 30;
      const pz = (Math.random() - 0.5) * 90;

      positions[i * 3] = px;
      positions[i * 3 + 1] = py;
      positions[i * 3 + 2] = pz;

      const tCol = i % 3;
      if (tCol === 0) {
        colors[i * 3] = 0.05; colors[i * 3 + 1] = 0.75; colors[i * 3 + 2] = 0.95; // LiDAR
      } else if (tCol === 1) {
        colors[i * 3] = 0.95; colors[i * 3 + 1] = 0.65; colors[i * 3 + 2] = 0.1; // RF
      } else {
        colors[i * 3] = 0.1; colors[i * 3 + 1] = 0.85; colors[i * 3 + 2] = 0.35; // Corridor
      }
    }
    pointsGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    pointsGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const pointsMat = new THREE.PointsMaterial({ size: 0.38, vertexColors: true, transparent: true, opacity: 0.8 });
    const spatialPoints = new THREE.Points(pointsGeo, pointsMat);
    spatialPointsRef.current = spatialPoints;
    scene.add(spatialPoints);

    // 5D Azimuth Range Rings
    [8, 16, 24].forEach((r) => {
      const ringGeo = new THREE.RingGeometry(r - 0.06, r, 64);
      const ringMat = new THREE.MeshBasicMaterial({ color: 0x0ea5e9, side: THREE.DoubleSide, transparent: true, opacity: 0.25 });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2;
      ring.position.y = -1.9;
      scene.add(ring);
    });

    // 9. ANIMATION LOOP & PERSPECTIVE CAMERA CONTROL
    const clock = new THREE.Clock();

    const animate = () => {
      const elapsedTime = clock.getElapsedTime();

      // Spin blades
      rotorBladeMeshes.forEach((blade, idx) => {
        blade.rotation.y += (idx % 2 === 0 ? 0.6 : -0.6);
      });

      // Beacon lights pulse
      const strobe = (Math.floor(elapsedTime * 2.5) % 2) === 0;
      beaconLights.forEach((l) => (l.intensity = strobe ? 2.5 : 0.2));

      // Drone flight kinematics
      const speedNorm = flightSpeedKnots / 60;
      const tFlight = elapsedTime * 0.32 * speedNorm;

      const droneX = Math.sin(tFlight) * 34;
      const droneZ = Math.cos(tFlight * 0.8) * 30;
      const droneY = (flightAltitudeMeters / 15) + Math.sin(tFlight * 2) * 1.5;

      const tangentX = Math.cos(tFlight) * 34;
      const tangentZ = -Math.sin(tFlight * 0.8) * 30 * 0.8;
      const droneHeading = Math.atan2(tangentX, tangentZ);

      if (droneGroupRef.current) {
        droneGroupRef.current.position.set(droneX, droneY, droneZ);
        droneGroupRef.current.rotation.y = droneHeading;
        droneGroupRef.current.rotation.z = Math.sin(tFlight) * -0.25; // banking
        droneGroupRef.current.rotation.x = Math.sin(tFlight * 2) * 0.08;
      }

      // Update real-time geo-coordinates matching flight
      const baseLat = 37.7749;
      const baseLng = -122.4194;
      const currLat = baseLat + (droneZ / 10000);
      const currLng = baseLng + (droneX / 10000);
      const headingDeg = Math.round((droneHeading * 180 / Math.PI + 360) % 360);

      setLiveGeoCoords({ lat: currLat, lng: currLng, alt: Math.round(flightAltitudeMeters) });
      setCurrentHeadingDeg(headingDeg);

      // Distance to Skytower-01
      const distToTower = Math.round(Math.sqrt(Math.pow(droneX - (-18), 2) + Math.pow(droneZ - (-12), 2)) * 8);
      setTargetRangeMeters(distToTower);

      // Camera Positioning according to activeDeckMode
      if (cameraRef.current) {
        if (activeDeckMode === 'DRONE_POV') {
          // REAL-TIME DRONE PERSPECTIVE (First-Person Cockpit Gimbal)
          // Camera placed right at the drone nose gimbal looking forward over the 3D terrain
          const eyeX = droneX + Math.sin(droneHeading) * 1.4;
          const eyeZ = droneZ + Math.cos(droneHeading) * 1.4;
          const eyeY = droneY + 0.15;

          cameraRef.current.position.set(eyeX, eyeY, eyeZ);

          // Apply zoom factor by narrowing FOV or looking further
          const lookDist = 45 * zoomFactor;
          const lookAtX = eyeX + Math.sin(droneHeading) * lookDist;
          const lookAtZ = eyeZ + Math.cos(droneHeading) * lookDist;
          const lookAtY = eyeY - (5.0 / zoomFactor);
          cameraRef.current.lookAt(lookAtX, lookAtY, lookAtZ);
        } else if (activeDeckMode === 'AROUND_360') {
          // ALL AROUND CAMERA VIEW 360°
          if (isAutoSpinning && !isDraggingRef.current) {
            sphericalRef.current.theta += 0.008 * spinSpeed;
          }

          // Camera orbit around drone center
          const { radius, theta, phi } = sphericalRef.current;
          const adjustedRadius = Math.max(3, radius / (zoomFactor * 0.6));
          cameraRef.current.position.x = droneX + adjustedRadius * Math.sin(phi) * Math.sin(theta);
          cameraRef.current.position.y = droneY + adjustedRadius * Math.cos(phi);
          cameraRef.current.position.z = droneZ + adjustedRadius * Math.sin(phi) * Math.cos(theta);
          cameraRef.current.lookAt(droneX, droneY, droneZ);
        } else if (activeDeckMode === 'SPATIAL_5D') {
          // 5D SPATIAL PERCEPTION PERSPECTIVE
          // Elevated isometric 5D sensor perspective showing perception dome, terrain, and radar clusters
          const dist = 28 / (zoomFactor * 0.6);
          cameraRef.current.position.set(droneX - dist * 0.6, droneY + dist * 0.8, droneZ + dist * 0.8);
          cameraRef.current.lookAt(droneX, droneY - 2, droneZ);
        } else if (activeDeckMode === 'QUAD_CAM') {
          // Multi-camera directional switch
          let camAngleOffset = 0;
          if (selectedCamAngle === 'RIGHT_90') camAngleOffset = Math.PI / 2;
          if (selectedCamAngle === 'AFT_180') camAngleOffset = Math.PI;
          if (selectedCamAngle === 'LEFT_270') camAngleOffset = -Math.PI / 2;

          const lookAngle = droneHeading + camAngleOffset;
          const eyeX = droneX + Math.sin(lookAngle) * 1.5;
          const eyeZ = droneZ + Math.cos(lookAngle) * 1.5;
          const eyeY = droneY + 0.15;

          cameraRef.current.position.set(eyeX, eyeY, eyeZ);
          cameraRef.current.lookAt(eyeX + Math.sin(lookAngle) * 40, eyeY - 4, eyeZ + Math.cos(lookAngle) * 40);
        }
      }

      renderer.render(scene, camera);
      animFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    const handleResize = () => {
      if (!container || !cameraRef.current || !rendererRef.current) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      cameraRef.current.aspect = w / h;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      renderer.dispose();
      terrainGeo.dispose();
      terrainTexture.dispose();
    };
  }, [activeDeckMode, zoomFactor, flightSpeedKnots, flightAltitudeMeters, isAutoSpinning, spinSpeed, selectedCamAngle]);

  // Pointer interactions for 360 Spin / Orbit
  const handlePointerDown = (e: React.PointerEvent) => {
    isDraggingRef.current = true;
    prevMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isDraggingRef.current) return;
    const deltaX = e.clientX - prevMousePosRef.current.x;
    const deltaY = e.clientY - prevMousePosRef.current.y;

    sphericalRef.current.theta -= deltaX * 0.008;
    sphericalRef.current.phi = Math.max(0.1, Math.min(Math.PI - 0.1, sphericalRef.current.phi - deltaY * 0.008));
    prevMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handlePointerUp = () => {
    isDraggingRef.current = false;
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    setZoomFactor((prev) => {
      const next = Math.max(1.0, Math.min(8.0, prev - e.deltaY * 0.005));
      return Number(next.toFixed(1));
    });
  };

  // Live Real-Time First-Person Camera Feed Rendering with Tactical HUD
  useEffect(() => {
    const canvas = videoCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;

    const renderLiveFeed = () => {
      const w = canvas.width;
      const h = canvas.height;
      const t = Date.now() / 1000;

      // Update timecode
      const hrs = String(Math.floor(t / 3600) % 24).padStart(2, '0');
      const mins = String(Math.floor(t / 60) % 60).padStart(2, '0');
      const secs = String(Math.floor(t) % 60).padStart(2, '0');
      const ms = String(Math.floor((t % 1) * 100)).padStart(2, '0');
      setTimecodeStr(`${hrs}:${mins}:${secs}:${ms}`);

      // Render terrain & environment in live video feed based on spectrum mode
      if (footageSpectrum === 'FLIR_THERMAL') {
        ctx.fillStyle = '#06080e';
        ctx.fillRect(0, 0, w, h);

        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, h * 0.52);
        ctx.lineTo(w, h * 0.52);
        ctx.stroke();

        // Building Heat signatures
        for (let i = 0; i < 6; i++) {
          const bx = ((w / 6) * i + (Math.sin(t * 0.4 + i) * 15)) % w;
          const bh = 45 + (i * 12) % 60;
          ctx.fillStyle = i % 2 === 0 ? '#fef08a' : '#f97316';
          ctx.fillRect(bx, h * 0.52 - bh, 28, bh);
        }
      } else if (footageSpectrum === 'NIGHT_VISION') {
        ctx.fillStyle = '#011508';
        ctx.fillRect(0, 0, w, h);

        ctx.fillStyle = 'rgba(34, 197, 94, 0.2)';
        for (let i = 0; i < 85; i++) {
          ctx.fillRect(Math.random() * w, Math.random() * h, 1.5, 1.5);
        }

        ctx.fillStyle = '#052e16';
        for (let i = 0; i < 7; i++) {
          const bx = (i * 55) % w;
          const bh = 35 + (i * 15) % 55;
          ctx.fillRect(bx, h * 0.52 - bh, 35, bh);
        }
      } else if (footageSpectrum === 'LIDAR_DEPTH') {
        ctx.fillStyle = '#020617';
        ctx.fillRect(0, 0, w, h);

        for (let i = 0; i < 180; i++) {
          const px = (i * 19) % w;
          const py = (h * 0.35) + ((i * 29) % (h * 0.55));
          const depth = Math.sin(px * 0.03 + t) * 0.5 + 0.5;
          ctx.fillStyle = depth > 0.6 ? '#06b6d4' : depth > 0.3 ? '#a855f7' : '#ec4899';
          ctx.fillRect(px, py, 2.5, 2.5);
        }
      } else {
        // EO Daylight Optical
        const skyGrad = ctx.createLinearGradient(0, 0, 0, h);
        skyGrad.addColorStop(0, '#0284c7');
        skyGrad.addColorStop(0.52, '#38bdf8');
        skyGrad.addColorStop(0.53, '#0f172a');
        skyGrad.addColorStop(1, '#020617');
        ctx.fillStyle = skyGrad;
        ctx.fillRect(0, 0, w, h);

        // Mountain Horizon
        ctx.fillStyle = '#03456c';
        ctx.beginPath();
        ctx.moveTo(0, h * 0.52);
        ctx.lineTo(w * 0.3, h * 0.38);
        ctx.lineTo(w * 0.65, h * 0.46);
        ctx.lineTo(w, h * 0.40);
        ctx.lineTo(w, h * 0.52);
        ctx.fill();

        // City skyline buildings in live feed
        for (let i = 0; i < 7; i++) {
          const bx = (i * 52 + Math.sin(t * 0.3 + i) * 10) % w;
          const bh = 40 + (i * 14) % 65;
          ctx.fillStyle = i % 2 === 0 ? '#1e293b' : '#0f172a';
          ctx.fillRect(bx, h * 0.52 - bh, 36, bh);
          ctx.fillStyle = '#fef08a';
          for (let wy = h * 0.52 - bh + 6; wy < h * 0.52 - 6; wy += 8) {
            ctx.fillRect(bx + 6, wy, 4, 4);
            ctx.fillRect(bx + 16, wy, 4, 4);
          }
        }
      }

      // Tactical HUD Overlay on live video
      if (showHudOverlay) {
        const cx = w / 2;
        const cy = h / 2;

        ctx.strokeStyle = footageSpectrum === 'NIGHT_VISION' ? '#4ade80' : '#38bdf8';
        ctx.lineWidth = 1.2;
        ctx.font = '9px monospace';
        ctx.fillStyle = ctx.strokeStyle;

        // Artificial Horizon Pitch Ladder
        ctx.beginPath();
        ctx.moveTo(cx - 30, cy); ctx.lineTo(cx - 15, cy);
        ctx.moveTo(cx + 15, cy); ctx.lineTo(cx + 30, cy);
        ctx.moveTo(cx, cy - 25); ctx.lineTo(cx, cy - 15);
        ctx.moveTo(cx, cy + 15); ctx.lineTo(cx, cy + 25);
        ctx.stroke();

        ctx.strokeRect(cx - 5, cy - 5, 10, 10);

        // Target Acquisition Box
        const targetX = cx + Math.sin(t * 0.8) * 45;
        const targetY = cy - 20 + Math.cos(t * 0.6) * 15;
        ctx.strokeStyle = '#ef4444';
        ctx.strokeRect(targetX - 18, targetY - 18, 36, 36);
        ctx.fillStyle = '#ef4444';
        ctx.fillText('TARGET: SKYTOWER-01', targetX - 25, targetY - 22);
        ctx.fillText(`RNG: ${targetRangeMeters}m | ELEV: +12°`, targetX - 25, targetY + 28);

        // Compass Heading Tape
        ctx.fillStyle = 'rgba(15, 23, 42, 0.75)';
        ctx.fillRect(cx - 75, 8, 150, 18);
        ctx.strokeStyle = '#0284c7';
        ctx.strokeRect(cx - 75, 8, 150, 18);
        ctx.fillStyle = '#38bdf8';
        ctx.textAlign = 'center';
        ctx.fillText(`HDG: ${String(currentHeadingDeg).padStart(3, '0')}°  [POV TRACK]`, cx, 20);

        // Telemetry Overlays
        ctx.textAlign = 'left';
        ctx.fillText(`ALT: ${flightAltitudeMeters}m MSL`, 10, cy - 18);
        ctx.fillText(`SPD: ${flightSpeedKnots} KTS`, 10, cy);
        ctx.fillText(`LAT: ${currentLatencyMicros.toFixed(1)} μs`, 10, cy + 18);

        ctx.textAlign = 'right';
        ctx.fillText(`ZOOM: ${zoomFactor.toFixed(1)}X`, w - 10, cy - 18);
        ctx.fillText(`5D TENSOR: ACTIVE`, w - 10, cy);
        ctx.fillText(`BATT: ${batteryPct}%`, w - 10, cy + 18);

        // Scanlines
        ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        for (let y = 0; y < h; y += 4) {
          ctx.fillRect(0, y, w, 1.2);
        }
      }

      animId = requestAnimationFrame(renderLiveFeed);
    };

    renderLiveFeed();

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [footageSpectrum, showHudOverlay, zoomFactor, flightSpeedKnots, flightAltitudeMeters, currentLatencyMicros, batteryPct, currentHeadingDeg, targetRangeMeters]);

  return (
    <div className="space-y-4">
      {/* Top Banner Notice */}
      <div className="flex flex-wrap items-center justify-between text-xs bg-slate-900/60 border border-slate-800 px-3.5 py-2 rounded">
        <div className="flex items-center space-x-2 text-slate-300">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span className="font-bold">UNIFIED DRONE FLIGHT DECK • 5D SPATIAL PERCEPTION & LIVE FOOTAGE</span>
        </div>
        <div className="flex items-center space-x-4 text-slate-400 font-mono text-[11px]">
          <span>EXACT POSITION: <strong className="text-emerald-300">{liveGeoCoords.lat.toFixed(5)}°N, {Math.abs(liveGeoCoords.lng).toFixed(5)}°W</strong></span>
          <span>•</span>
          <span>ALTITUDE: <strong className="text-cyan-300">{liveGeoCoords.alt}m MSL</strong></span>
          <span>•</span>
          <span>AIRSPEED: <strong className="text-amber-300">{flightSpeedKnots} KTS</strong></span>
        </div>
      </div>

      {/* Main Integrated Display Screen */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* CENTER / PRIMARY VIEWPORT (8 cols, or 12 cols if fullscreen) */}
        <div className={`${isFullscreen ? 'lg:col-span-12 h-[680px]' : 'lg:col-span-8 h-[540px]'} bg-slate-950 border border-blue-900/70 rounded shadow-lg overflow-hidden flex flex-col justify-between relative group`}>
          {/* Top Integrated Control & Camera Mode Bar */}
          <div className="border-b border-blue-900/60 px-4 py-2 bg-slate-900/80 backdrop-blur flex flex-wrap items-center justify-between gap-2 z-10">
            <div className="flex items-center space-x-2">
              <Crosshair className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-bold tracking-wider text-blue-400 uppercase font-mono">
                {activeDeckMode === 'DRONE_POV' && 'Realtime Drone Perspective (1st Person POV)'}
                {activeDeckMode === 'AROUND_360' && 'All-Around Camera View 360°'}
                {activeDeckMode === 'SPATIAL_5D' && '5D Spatial Perception Matrix'}
                {activeDeckMode === 'QUAD_CAM' && `Multi-Cam Directional [${selectedCamAngle}]`}
              </span>
            </div>

            {/* View & Camera Mode Selector Buttons */}
            <div className="flex items-center space-x-1 bg-slate-950 p-0.5 rounded border border-slate-800 text-[11px] font-mono">
              {[
                { id: 'DRONE_POV', label: 'Drone POV' },
                { id: 'AROUND_360', label: '360° All-Around' },
                { id: 'SPATIAL_5D', label: '5D Spatial POV' },
                { id: 'QUAD_CAM', label: 'Directional Cam' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveDeckMode(tab.id as any)}
                  className={`px-2 py-0.5 rounded transition cursor-pointer ${
                    activeDeckMode === tab.id
                      ? 'bg-cyan-950 text-cyan-300 border border-cyan-500 font-bold'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {tab.label}
                </button>
              ))}

              {/* Fullscreen Toggle */}
              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-1 ml-1 text-slate-400 hover:text-cyan-300 cursor-pointer"
                title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
              >
                {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          {/* Interactive 3D Canvas Viewport */}
          <div
            ref={mountRef}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onWheel={handleWheel}
            className="w-full flex-1 cursor-grab active:cursor-grabbing relative select-none"
          >
            {/* Real-Time On-Screen Flight Instrument HUD */}
            <div className="absolute inset-0 pointer-events-none p-3.5 flex flex-col justify-between font-mono">
              {/* Top Left: Navigation & Coordinates Readout */}
              <div className="flex justify-between items-start">
                <div className="bg-slate-950/80 backdrop-blur p-2.5 rounded border border-cyan-900/60 text-[11px] space-y-1 shadow-lg">
                  <div className="text-cyan-400 font-bold flex items-center space-x-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                    <span>REALTIME DRONE POSITION: ACTIVE</span>
                  </div>
                  <div className="text-slate-200">LAT: <strong className="text-emerald-400">{liveGeoCoords.lat.toFixed(6)}°</strong> | LNG: <strong className="text-emerald-400">{liveGeoCoords.lng.toFixed(6)}°</strong></div>
                  <div className="text-slate-300">ALTITUDE: <strong className="text-cyan-300">{liveGeoCoords.alt}m MSL</strong> | SPEED: <strong className="text-amber-400">{flightSpeedKnots} kts</strong></div>
                  <div className="text-slate-300">HEADING: <strong className="text-cyan-300">{currentHeadingDeg}° T</strong> | DATUM: <strong className="text-slate-400">WGS-84</strong></div>
                </div>

                {/* Top Right: Infrastructure Target Lock */}
                <div className="bg-slate-950/80 backdrop-blur p-2.5 rounded border border-cyan-900/60 text-[11px] text-right space-y-1 shadow-lg">
                  <div className="text-amber-400 font-bold">SENSOR TARGET LOCK</div>
                  <div className="text-slate-200 font-bold">{lockedTargetName}</div>
                  <div className="text-emerald-400">RANGEFINDER: {targetRangeMeters}m</div>
                  <div className="text-slate-400">LATENCY: <span className="text-emerald-400 font-bold">{currentLatencyMicros.toFixed(1)} μs</span></div>
                </div>
              </div>

              {/* Center Reticle / Pitch Ladder in DRONE_POV mode */}
              {activeDeckMode === 'DRONE_POV' && (
                <div className="self-center flex flex-col items-center">
                  <div className="w-12 h-12 border border-cyan-400/60 rounded-full flex items-center justify-center">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
                  </div>
                  <span className="text-[9px] text-cyan-300 bg-slate-950/80 px-1 rounded mt-1 border border-cyan-900">
                    GIMBAL NOSE CAM
                  </span>
                </div>
              )}

              {/* Mini Picture-in-Picture (PiP) Live Camera Inset on 3D Viewport */}
              {showLivePip && (
                <div className="absolute bottom-14 right-3 w-48 aspect-video rounded overflow-hidden border border-cyan-500/80 bg-black/90 shadow-2xl pointer-events-auto">
                  <canvas
                    ref={videoCanvasRef}
                    width={240}
                    height={135}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-1 left-1.5 text-[9px] font-mono text-cyan-300 bg-black/70 px-1 py-0.2 rounded">
                    LIVE ● {timecodeStr.split(':').slice(1).join(':')}
                  </div>
                  <div className="absolute top-1 right-1.5 text-[9px] font-mono text-emerald-400 bg-black/70 px-1 py-0.2 rounded border border-emerald-900">
                    {footageSpectrum}
                  </div>
                </div>
              )}

              {/* Bottom Instructions Badge */}
              <div className="flex justify-between items-end text-[10px] text-slate-400">
                <span className="bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
                  Drag to rotate • Scroll wheel to slide in/out zoom focus
                </span>
                <span className="bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
                  5D Terrain + Infrastructure Matrix
                </span>
              </div>
            </div>
          </div>

          {/* Bottom Integrated Flight Deck Toolbar */}
          <div className="border-t border-blue-900/40 p-3 bg-slate-900/60 flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
            {/* Camera Slide In & Out Zoom / Focus Slider */}
            <div className="flex items-center space-x-2 flex-1 min-w-[200px]">
              <span className="text-slate-400 flex items-center space-x-1 whitespace-nowrap text-[11px]">
                <ZoomIn className="w-3.5 h-3.5 text-cyan-400" />
                <span>Slide Zoom Focus:</span>
              </span>
              <input
                type="range"
                min="1.0"
                max="8.0"
                step="0.2"
                value={zoomFactor}
                onChange={(e) => setZoomFactor(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
              <span className="text-cyan-300 font-bold w-12 text-right text-[11px]">
                {zoomFactor.toFixed(1)}x
              </span>
            </div>

            {/* 360 Spin View Controls (When in 360 mode or Spatial) */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsAutoSpinning(!isAutoSpinning)}
                className={`flex items-center space-x-1 px-2.5 py-1 rounded text-[11px] font-semibold border transition cursor-pointer ${
                  isAutoSpinning
                    ? 'bg-cyan-950 border-cyan-500 text-cyan-300'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <RotateCw className={`w-3.5 h-3.5 ${isAutoSpinning ? 'animate-spin' : ''}`} />
                <span>{isAutoSpinning ? '360° Spin Active' : 'Spin View 360°'}</span>
              </button>

              {isAutoSpinning && (
                <div className="flex items-center space-x-1 text-[10px]">
                  {[0.5, 1.0, 2.0].map((s) => (
                    <button
                      key={s}
                      onClick={() => setSpinSpeed(s)}
                      className={`px-1.5 py-0.5 rounded border cursor-pointer ${
                        spinSpeed === s
                          ? 'bg-cyan-900 border-cyan-500 text-cyan-200 font-bold'
                          : 'border-slate-800 text-slate-400'
                      }`}
                    >
                      {s}x
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* PiP Inset Toggle */}
            <button
              onClick={() => setShowLivePip(!showLivePip)}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded text-[11px] border cursor-pointer ${
                showLivePip
                  ? 'bg-emerald-950 border-emerald-500 text-emerald-300'
                  : 'bg-slate-900 border-slate-800 text-slate-400'
              }`}
            >
              <Video className="w-3.5 h-3.5" />
              <span>{showLivePip ? 'PiP Camera On' : 'PiP Camera Off'}</span>
            </button>
          </div>
        </div>

        {/* RIGHT: TACTICAL FLIGHT INSTRUMENTATION & SENSOR CONTROLS (4 cols, hidden if fullscreen) */}
        {!isFullscreen && (
          <div className="lg:col-span-4 bg-slate-950 border border-blue-900/70 rounded shadow-lg overflow-hidden flex flex-col justify-between">
            <div className="border-b border-blue-900/60 px-4 py-2.5 bg-slate-900/80 flex items-center justify-between">
              <span className="text-xs font-bold tracking-wider text-blue-400 uppercase flex items-center space-x-1.5 font-mono">
                <Navigation className="w-4 h-4 text-cyan-400" />
                <span>Flight Deck Control Panel</span>
              </span>
              <span className="text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800 px-1.5 py-0.5 rounded font-mono font-bold">
                AUTOPILOT ONLINE
              </span>
            </div>

            <div className="p-4 space-y-4 font-mono text-xs flex-1">
              {/* Flight Dynamics Sliders */}
              <div className="bg-slate-900/70 p-3 rounded border border-slate-800 space-y-3">
                <div className="text-[11px] text-slate-400 uppercase font-bold border-b border-slate-800 pb-1 flex justify-between">
                  <span>Flight Control Actuators</span>
                  <span className="text-cyan-400">60 FPS</span>
                </div>

                {/* Airspeed Slider */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] text-slate-300">
                    <span className="text-slate-400 flex items-center space-x-1">
                      <Gauge className="w-3 h-3 text-cyan-400" />
                      <span>Cruise Airspeed:</span>
                    </span>
                    <span className="text-cyan-300 font-bold">{flightSpeedKnots} kts</span>
                  </div>
                  <input
                    type="range"
                    min="20"
                    max="120"
                    step="5"
                    value={flightSpeedKnots}
                    onChange={(e) => setFlightSpeedKnots(Number(e.target.value))}
                    className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                  />
                </div>

                {/* Altitude Slider */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] text-slate-300">
                    <span className="text-slate-400 flex items-center space-x-1">
                      <Plane className="w-3 h-3 text-emerald-400" />
                      <span>Operating Altitude:</span>
                    </span>
                    <span className="text-emerald-300 font-bold">{flightAltitudeMeters} m MSL</span>
                  </div>
                  <input
                    type="range"
                    min="50"
                    max="400"
                    step="10"
                    value={flightAltitudeMeters}
                    onChange={(e) => setFlightAltitudeMeters(Number(e.target.value))}
                    className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-emerald-400"
                  />
                </div>
              </div>

              {/* Multi-Spectrum Sensor Selector */}
              <div className="bg-slate-900/70 p-3 rounded border border-slate-800 space-y-2">
                <span className="text-[11px] text-slate-400 uppercase font-bold block border-b border-slate-800 pb-1">
                  Camera Sensor Spectrum
                </span>
                <div className="grid grid-cols-2 gap-1.5">
                  {[
                    { id: 'EO_COLOR', label: 'EO Optical' },
                    { id: 'FLIR_THERMAL', label: 'FLIR Thermal' },
                    { id: 'NIGHT_VISION', label: 'NVG Green' },
                    { id: 'LIDAR_DEPTH', label: 'LiDAR Depth' },
                  ].map((m) => (
                    <button
                      key={m.id}
                      onClick={() => setFootageSpectrum(m.id as any)}
                      className={`py-1.5 px-2 rounded border text-[11px] transition cursor-pointer text-center ${
                        footageSpectrum === m.id
                          ? 'bg-cyan-950 text-cyan-300 border-cyan-500 font-bold'
                          : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                      }`}
                    >
                      {m.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Multi-Directional Quad Cam Switcher (For All-Around Viewing) */}
              <div className="bg-slate-900/70 p-3 rounded border border-slate-800 space-y-2">
                <span className="text-[11px] text-slate-400 uppercase font-bold block border-b border-slate-800 pb-1">
                  360° Multi-Angle Surround Selector
                </span>
                <div className="grid grid-cols-4 gap-1 text-[11px]">
                  {[
                    { id: 'NOSE_0', label: 'Forward' },
                    { id: 'RIGHT_90', label: 'Starboard' },
                    { id: 'AFT_180', label: 'Aft' },
                    { id: 'LEFT_270', label: 'Port' },
                  ].map((ang) => (
                    <button
                      key={ang.id}
                      onClick={() => {
                        setSelectedCamAngle(ang.id as any);
                        setActiveDeckMode('QUAD_CAM');
                      }}
                      className={`py-1 rounded border text-center transition cursor-pointer ${
                        selectedCamAngle === ang.id && activeDeckMode === 'QUAD_CAM'
                          ? 'bg-emerald-950 text-emerald-300 border-emerald-500 font-bold'
                          : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                      }`}
                    >
                      {ang.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Real-Time Exact Coordinate Status Card */}
              <div className="bg-slate-900/70 p-3 rounded border border-slate-800 space-y-1.5 text-[11px]">
                <div className="flex justify-between text-slate-400">
                  <span>Current Target:</span>
                  <span className="text-red-400 font-bold">{lockedTargetName}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Target Range:</span>
                  <span className="text-emerald-400 font-bold">{targetRangeMeters} meters</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>GNSS Lock:</span>
                  <span className="text-cyan-300 font-bold">RTK FIXED (±1.8m)</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Telemetry Loop Latency:</span>
                  <span className="text-emerald-400 font-bold">{currentLatencyMicros.toFixed(1)} μs</span>
                </div>
              </div>
            </div>

            <div className="border-t border-blue-900/40 px-3 py-2 bg-slate-900/50 text-[10px] font-mono text-slate-400 flex justify-between items-center">
              <span>UNIFIED COCKPIT: SYNCED</span>
              <span className="text-emerald-400 font-bold">ALL SYSTEMS NOMINAL</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
