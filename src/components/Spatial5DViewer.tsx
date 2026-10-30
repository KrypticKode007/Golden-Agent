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
  Sun,
  Moon,
  Plane,
  Gauge
} from 'lucide-react';

interface Spatial5DViewerProps {
  currentLatencyMicros?: number;
  batteryPct?: number;
}

// Procedural Canvas Texture Generators for Realistic Google Maps / Satellite 3D aesthetic
const createSatelliteTerrainTexture = (): THREE.CanvasTexture => {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d')!;

  // Base satellite earth tone
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

  // Winding River / Water Body (Google Maps dark blue style)
  ctx.strokeStyle = '#0284c7';
  ctx.lineWidth = 42;
  ctx.beginPath();
  ctx.moveTo(0, 320);
  ctx.bezierCurveTo(340, 480, 680, 240, 1024, 450);
  ctx.stroke();

  // Water specular inner line
  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 12;
  ctx.beginPath();
  ctx.moveTo(0, 320);
  ctx.bezierCurveTo(340, 480, 680, 240, 1024, 450);
  ctx.stroke();

  // Urban Road & Highway Network (Google Maps style arterial roads)
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 10;
  ctx.beginPath();
  // Main highway
  ctx.moveTo(512, 0); ctx.lineTo(512, 1024);
  ctx.moveTo(0, 640); ctx.lineTo(1024, 640);
  // Diagonal ring road
  ctx.moveTo(100, 100); ctx.lineTo(900, 900);
  ctx.stroke();

  // Yellow highway median lines
  ctx.strokeStyle = '#f59e0b';
  ctx.lineWidth = 1.5;
  ctx.setLineDash([8, 8]);
  ctx.beginPath();
  ctx.moveTo(512, 0); ctx.lineTo(512, 1024);
  ctx.moveTo(0, 640); ctx.lineTo(1024, 640);
  ctx.stroke();
  ctx.setLineDash([]);

  // Airport Runway / Tactical Tarmac
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(440, 680, 144, 300);
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 2;
  ctx.strokeRect(440, 680, 144, 300);

  // Runway Centerline & Numbers
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 3;
  ctx.setLineDash([16, 16]);
  ctx.beginPath();
  ctx.moveTo(512, 690); ctx.lineTo(512, 970);
  ctx.stroke();
  ctx.setLineDash([]);

  // MGRS Coordinate Grid Lines (Tactical Map overlay)
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

// Procedural Building Window Texture (Skyscraper facade)
const createBuildingFacadeTexture = (): THREE.CanvasTexture => {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 512;
  const ctx = canvas.getContext('2d')!;

  ctx.fillStyle = '#090d16';
  ctx.fillRect(0, 0, 256, 512);

  // Windows grid
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

export const Spatial5DViewer: React.FC<Spatial5DViewerProps> = ({
  currentLatencyMicros = 14.2,
  batteryPct = 88,
}) => {
  // DOM Refs
  const mountRef = useRef<HTMLDivElement>(null);
  const videoCanvasRef = useRef<HTMLCanvasElement>(null);

  // View & Camera Controls State
  const [viewMode, setViewMode] = useState<'COCKPIT_POV' | 'ORBIT' | 'FLYOVER_RECON' | 'TOP_DOWN'>('COCKPIT_POV');
  const [cameraDistance, setCameraDistance] = useState<number>(10.0);
  const [flightSpeedKnots, setFlightSpeedKnots] = useState<number>(65);
  const [flightAltitudeMeters, setFlightAltitudeMeters] = useState<number>(185);
  const [footageMode, setFootageMode] = useState<'EO_COLOR' | 'FLIR_THERMAL' | 'NIGHT_VISION' | 'LIDAR_DEPTH'>('EO_COLOR');
  const [footageZoom, setFootageZoom] = useState<number>(1.5);
  const [showFootageOverlay, setShowFootageOverlay] = useState<boolean>(true);
  const [isFullscreenPOV, setIsFullscreenPOV] = useState<boolean>(false);
  const [isAutoSpinning, setIsAutoSpinning] = useState<boolean>(false);
  const [telemetryTimecode, setTelemetryTimecode] = useState<string>('00:00:00:00');

  // Flight Telemetry live values
  const [currentCoords3D, setCurrentCoords3D] = useState<{ x: number; y: number; z: number }>({ x: 0, y: 15, z: 0 });
  const [nearestTarget, setNearestTarget] = useState<string>('BLDG-TOWER-ALPHA (142m)');

  // Three.js References
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const droneGroupRef = useRef<THREE.Group | null>(null);
  const rotorBladesRef = useRef<THREE.Mesh[]>([]);
  const spatialPointsRef = useRef<THREE.Points | null>(null);
  const beaconLightsRef = useRef<THREE.PointLight[]>([]);

  // Interaction tracking for Orbit
  const isDraggingRef = useRef<boolean>(false);
  const previousMousePositionRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const sphericalRef = useRef<{ theta: number; phi: number; radius: number }>({
    theta: 0.2,
    phi: 1.2,
    radius: 12.0,
  });

  // Keep camera distance state synced with spherical radius
  useEffect(() => {
    sphericalRef.current.radius = cameraDistance;
  }, [cameraDistance]);

  // Main Three.js Scene Setup (3D Geospatial Terrain + Urban Infrastructure + Drone)
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // 1. Scene & Atmospheric Fog
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    scene.background = new THREE.Color(0x040814); // Deep night sky
    scene.fog = new THREE.FogExp2(0x040814, 0.012);

    // 2. Camera
    const aspect = container.clientWidth / container.clientHeight;
    const camera = new THREE.PerspectiveCamera(60, aspect, 0.5, 500);
    cameraRef.current = camera;
    camera.position.set(0, 15, 20);

    // 3. Renderer with antialiasing
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    rendererRef.current = renderer;
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.3;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // 4. Lighting Rig (Moonlight + Tactical Sky ambient + City light reflections)
    const ambientLight = new THREE.AmbientLight(0x0c4a6e, 1.4);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x38bdf8, 2.5);
    dirLight.position.set(50, 80, 40);
    scene.add(dirLight);

    const cityGlowLight = new THREE.DirectionalLight(0x0284c7, 1.0);
    cityGlowLight.position.set(-40, 20, -50);
    scene.add(cityGlowLight);

    // 5. GEOSPATIAL TERRAIN (Google Maps 3D Elevation Mesh)
    const terrainSize = 220;
    const terrainSegments = 64;
    const terrainGeo = new THREE.PlaneGeometry(terrainSize, terrainSize, terrainSegments, terrainSegments);
    terrainGeo.rotateX(-Math.PI / 2);

    // Elevate mountains on outer boundaries and carve river valley
    const posAttr = terrainGeo.attributes.position;
    for (let i = 0; i < posAttr.count; i++) {
      const vx = posAttr.getX(i);
      const vz = posAttr.getZ(i);

      // Distance from center
      const distFromCenter = Math.sqrt(vx * vx + vz * vz);
      let height = 0;

      // Outer mountain ridgelines
      if (distFromCenter > 40) {
        height = Math.sin(vx * 0.06) * Math.cos(vz * 0.06) * 16 + (distFromCenter - 40) * 0.18;
      } else {
        // Flat valley for urban city & airfield
        height = Math.sin(vx * 0.1) * Math.cos(vz * 0.1) * 1.5;
      }

      posAttr.setY(i, Math.max(-0.5, height));
    }
    terrainGeo.computeVertexNormals();

    const terrainTexture = createSatelliteTerrainTexture();
    const terrainMat = new THREE.MeshStandardMaterial({
      map: terrainTexture,
      roughness: 0.75,
      metalness: 0.15,
      flatShading: true,
    });
    const terrainMesh = new THREE.Mesh(terrainGeo, terrainMat);
    terrainMesh.position.y = -2;
    scene.add(terrainMesh);

    // 6. URBAN INFRASTRUCTURES (3D City Skylines, Hangars, Bridges, Towers)
    const infrastructureGroup = new THREE.Group();
    const buildingMat = new THREE.MeshStandardMaterial({
      map: createBuildingFacadeTexture(),
      roughness: 0.4,
      metalness: 0.7,
    });

    const roofMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
    const beaconLights: THREE.PointLight[] = [];

    // Array of 28 3D Buildings & Towers arranged in downtown blocks
    const buildingDefs = [
      // Downtown Highrises
      { x: -18, z: -12, w: 7, h: 28, d: 7, label: 'BLDG-ALPHA [HQ]' },
      { x: -8, z: -14, w: 6, h: 36, d: 6, label: 'SKYTOWER-01' },
      { x: 0, z: -18, w: 8, h: 22, d: 8, label: 'FINANCE-PLAZA' },
      { x: 12, z: -15, w: 6, h: 30, d: 6, label: 'TECH-CAMPUS' },
      { x: -14, z: 2, w: 6, h: 18, d: 6, label: 'CIVIC-CENTER' },
      { x: -24, z: -4, w: 8, h: 25, d: 8, label: 'TELECOM-HUB' },
      { x: 18, z: -4, w: 7, h: 24, d: 7, label: 'METRO-TOWER' },
      { x: 8, z: 4, w: 6, h: 16, d: 6, label: 'LOGISTICS-02' },
      { x: -6, z: 8, w: 5, h: 14, d: 5, label: 'SUBSTATION-GRID' },
      { x: 22, z: 12, w: 8, h: 20, d: 8, label: 'WAREHOUSE-DIST' },
      { x: -28, z: 16, w: 7, h: 16, d: 7, label: 'ENERGY-CORE' },
      { x: 14, z: 22, w: 6, h: 18, d: 6, label: 'TERMINAL-SOUTH' },
    ];

    buildingDefs.forEach((b) => {
      const bldgGeo = new THREE.BoxGeometry(b.w, b.h, b.d);
      const bldg = new THREE.Mesh(bldgGeo, buildingMat);
      bldg.position.set(b.x, b.h / 2 - 2, b.z);
      infrastructureGroup.add(bldg);

      // Rooftop Helipad / Structure
      const roofGeo = new THREE.BoxGeometry(b.w * 0.7, 1.2, b.d * 0.7);
      const roof = new THREE.Mesh(roofGeo, roofMat);
      roof.position.set(b.x, b.h - 1.4, b.z);
      infrastructureGroup.add(roof);

      // Rooftop Red Obstacle Warning Strobe
      const redStrobe = new THREE.PointLight(0xef4444, 1.5, 12);
      redStrobe.position.set(b.x, b.h - 0.5, b.z);
      infrastructureGroup.add(redStrobe);
      beaconLights.push(redStrobe);
    });

    // Communication Relay Mast (Tall lattice steel tower)
    const towerGeo = new THREE.CylinderGeometry(0.2, 1.8, 38, 6);
    const towerMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.9, roughness: 0.2 });
    const tower = new THREE.Mesh(towerGeo, towerMat);
    tower.position.set(-36, 17, -25);
    infrastructureGroup.add(tower);

    const towerStrobe = new THREE.PointLight(0xef4444, 3, 20);
    towerStrobe.position.set(-36, 36, -25);
    infrastructureGroup.add(towerStrobe);
    beaconLights.push(towerStrobe);

    // Geodesic Radar Dome (Air Traffic & Missile Defense Radar)
    const domeGeo = new THREE.SphereGeometry(4.5, 16, 12, 0, Math.PI * 2, 0, Math.PI / 2);
    const domeMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.3 });
    const dome = new THREE.Mesh(domeGeo, domeMat);
    dome.position.set(32, -2, -32);
    infrastructureGroup.add(dome);

    // Suspension Bridge over River
    const bridgeDeckGeo = new THREE.BoxGeometry(6, 0.8, 60);
    const bridgeMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.8 });
    const bridge = new THREE.Mesh(bridgeDeckGeo, bridgeMat);
    bridge.position.set(0, 1.5, -42);
    infrastructureGroup.add(bridge);

    scene.add(infrastructureGroup);
    beaconLightsRef.current = beaconLights;

    // 7. AEGIS AUTONOMOUS DRONE 3D MODEL
    const droneGroup = new THREE.Group();
    droneGroupRef.current = droneGroup;

    // Fuselage
    const fuselageGeo = new THREE.BoxGeometry(1.6, 0.45, 2.4);
    const carbonMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.35, metalness: 0.85 });
    const fuselage = new THREE.Mesh(fuselageGeo, carbonMat);
    droneGroup.add(fuselage);

    // Armor Canopy
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

    // 8. 5D Spatial Array (LiDAR / RF Point Cloud surrounding the flight corridor)
    const pointsCount = 350;
    const pointsGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(pointsCount * 3);
    const colors = new Float32Array(pointsCount * 3);

    for (let i = 0; i < pointsCount; i++) {
      const px = (Math.random() - 0.5) * 80;
      const py = 2 + Math.random() * 25;
      const pz = (Math.random() - 0.5) * 80;

      positions[i * 3] = px;
      positions[i * 3 + 1] = py;
      positions[i * 3 + 2] = pz;

      // Color coding: Cyan (infrastructure return), Amber (RF beacon), Green (safe corridor)
      const tCol = i % 3;
      if (tCol === 0) {
        colors[i * 3] = 0.05; colors[i * 3 + 1] = 0.75; colors[i * 3 + 2] = 0.95;
      } else if (tCol === 1) {
        colors[i * 3] = 0.95; colors[i * 3 + 1] = 0.65; colors[i * 3 + 2] = 0.1;
      } else {
        colors[i * 3] = 0.1; colors[i * 3 + 1] = 0.85; colors[i * 3 + 2] = 0.35;
      }
    }
    pointsGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    pointsGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const pointsMat = new THREE.PointsMaterial({ size: 0.35, vertexColors: true, transparent: true, opacity: 0.75 });
    const spatialPoints = new THREE.Points(pointsGeo, pointsMat);
    spatialPointsRef.current = spatialPoints;
    scene.add(spatialPoints);

    // 9. ANIMATION LOOP
    const clock = new THREE.Clock();

    const animate = () => {
      const elapsedTime = clock.getElapsedTime();

      // Spin rotors
      rotorBladeMeshes.forEach((blade, idx) => {
        blade.rotation.y += (idx % 2 === 0 ? 0.55 : -0.55);
      });

      // Strobe beacon lights
      const strobeOn = (Math.floor(elapsedTime * 2.5) % 2) === 0;
      beaconLights.forEach((light) => {
        light.intensity = strobeOn ? 2.5 : 0.2;
      });

      // Drone Flight Trajectory over 3D City & Terrain
      const speedFactor = flightSpeedKnots / 60;
      const flightTime = elapsedTime * 0.35 * speedFactor;

      // Elliptical Reconnaissance Flight Path around the city
      const droneX = Math.sin(flightTime) * 32;
      const droneZ = Math.cos(flightTime * 0.8) * 28;
      const droneY = (flightAltitudeMeters / 15) + Math.sin(flightTime * 2) * 1.5;

      // Forward flight direction angle
      const forwardTangentX = Math.cos(flightTime) * 32;
      const forwardTangentZ = -Math.sin(flightTime * 0.8) * 28 * 0.8;
      const droneHeading = Math.atan2(forwardTangentX, forwardTangentZ);

      if (droneGroupRef.current) {
        droneGroupRef.current.position.set(droneX, droneY, droneZ);
        droneGroupRef.current.rotation.y = droneHeading;
        // Natural banking tilt when turning
        droneGroupRef.current.rotation.z = Math.sin(flightTime) * -0.22;
        droneGroupRef.current.rotation.x = Math.sin(flightTime * 2) * 0.08;
      }

      setCurrentCoords3D({ x: droneX, y: droneY, z: droneZ });

      // Camera Positioning according to viewMode
      if (cameraRef.current) {
        if (viewMode === 'COCKPIT_POV') {
          // 5D FIRST PERSON POV: Directly inside the drone gimbal camera looking forward over the 3D terrain and city!
          const eyeX = droneX + Math.sin(droneHeading) * 1.4;
          const eyeZ = droneZ + Math.cos(droneHeading) * 1.4;
          const eyeY = droneY + 0.2;

          cameraRef.current.position.set(eyeX, eyeY, eyeZ);

          // Look forward along heading and slightly down towards ground
          const lookAtX = eyeX + Math.sin(droneHeading) * 45;
          const lookAtZ = eyeZ + Math.cos(droneHeading) * 45;
          const lookAtY = eyeY - 6.0;
          cameraRef.current.lookAt(lookAtX, lookAtY, lookAtZ);
        } else if (viewMode === 'ORBIT') {
          // Orbital Situational 360 view around the drone
          if (isAutoSpinning && !isDraggingRef.current) {
            sphericalRef.current.theta += 0.006;
          }
          const { radius, theta, phi } = sphericalRef.current;
          cameraRef.current.position.x = droneX + radius * Math.sin(phi) * Math.sin(theta);
          cameraRef.current.position.y = droneY + radius * Math.cos(phi);
          cameraRef.current.position.z = droneZ + radius * Math.sin(phi) * Math.cos(theta);
          cameraRef.current.lookAt(droneX, droneY, droneZ);
        } else if (viewMode === 'FLYOVER_RECON') {
          // Chase camera tracking behind and above drone
          const chaseDistance = 14;
          const chaseHeight = 6;
          const chaseX = droneX - Math.sin(droneHeading) * chaseDistance;
          const chaseZ = droneZ - Math.cos(droneHeading) * chaseDistance;
          const chaseY = droneY + chaseHeight;

          cameraRef.current.position.set(chaseX, chaseY, chaseZ);
          cameraRef.current.lookAt(droneX, droneY + 1.0, droneZ);
        } else if (viewMode === 'TOP_DOWN') {
          // Orthogonal satellite view looking down at the 3D map
          cameraRef.current.position.set(droneX, droneY + 65, droneZ + 0.01);
          cameraRef.current.lookAt(droneX, droneY, droneZ);
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
  }, [viewMode, flightSpeedKnots, flightAltitudeMeters, isAutoSpinning, cameraDistance]);

  // Pointer interactions for Orbit mode
  const handlePointerDown = (e: React.PointerEvent) => {
    isDraggingRef.current = true;
    previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isDraggingRef.current) return;
    const deltaX = e.clientX - previousMousePositionRef.current.x;
    const deltaY = e.clientY - previousMousePositionRef.current.y;

    sphericalRef.current.theta -= deltaX * 0.008;
    sphericalRef.current.phi = Math.max(0.1, Math.min(Math.PI - 0.1, sphericalRef.current.phi - deltaY * 0.008));

    previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
  };

  const handlePointerUp = () => {
    isDraggingRef.current = false;
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    setCameraDistance((prev) => Math.max(3.0, Math.min(45.0, prev + e.deltaY * 0.02)));
  };

  // Live Real-Time First-Person Camera Feed Rendering with Tactical HUD
  useEffect(() => {
    const canvas = videoCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;

    const renderLiveCam = () => {
      const w = canvas.width;
      const h = canvas.height;
      const t = Date.now() / 1000;

      // Update timecode
      const hrs = String(Math.floor(t / 3600) % 24).padStart(2, '0');
      const mins = String(Math.floor(t / 60) % 60).padStart(2, '0');
      const secs = String(Math.floor(t) % 60).padStart(2, '0');
      const ms = String(Math.floor((t % 1) * 100)).padStart(2, '0');
      setTelemetryTimecode(`${hrs}:${mins}:${secs}:${ms}`);

      // Background color & terrain horizon based on footage mode
      if (footageMode === 'FLIR_THERMAL') {
        ctx.fillStyle = '#05070d';
        ctx.fillRect(0, 0, w, h);

        // Simulated thermal horizon & buildings
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, h * 0.52);
        ctx.lineTo(w, h * 0.52);
        ctx.stroke();

        // Building Heat signatures
        const bldgCount = 6;
        for (let i = 0; i < bldgCount; i++) {
          const bx = ((w / bldgCount) * i + (Math.sin(t * 0.4 + i) * 15)) % w;
          const bh = 45 + (i * 12) % 60;
          const bw = 24 + (i * 6) % 30;
          ctx.fillStyle = i % 2 === 0 ? '#fef08a' : '#f97316';
          ctx.fillRect(bx, h * 0.52 - bh, bw, bh);
        }
      } else if (footageMode === 'NIGHT_VISION') {
        ctx.fillStyle = '#011708';
        ctx.fillRect(0, 0, w, h);

        // Phosphor grain
        ctx.fillStyle = 'rgba(34, 197, 94, 0.2)';
        for (let i = 0; i < 90; i++) {
          ctx.fillRect(Math.random() * w, Math.random() * h, 1.5, 1.5);
        }

        // Night city silhouettes
        ctx.fillStyle = '#042f14';
        for (let i = 0; i < 7; i++) {
          const bx = (i * 55) % w;
          const bh = 35 + (i * 15) % 55;
          ctx.fillRect(bx, h * 0.52 - bh, 35, bh);
        }
      } else if (footageMode === 'LIDAR_DEPTH') {
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
        // EO_COLOR (Real-time daylight optical)
        const skyGrad = ctx.createLinearGradient(0, 0, 0, h);
        skyGrad.addColorStop(0, '#0284c7');
        skyGrad.addColorStop(0.52, '#38bdf8');
        skyGrad.addColorStop(0.53, '#0f172a');
        skyGrad.addColorStop(1, '#020617');
        ctx.fillStyle = skyGrad;
        ctx.fillRect(0, 0, w, h);

        // Mountain silhouettes in background
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
          const bx = (i * 50 + Math.sin(t * 0.3 + i) * 10) % w;
          const bh = 40 + (i * 14) % 65;
          ctx.fillStyle = i % 2 === 0 ? '#1e293b' : '#0f172a';
          ctx.fillRect(bx, h * 0.52 - bh, 35, bh);
          // Windows
          ctx.fillStyle = '#fef08a';
          for (let wy = h * 0.52 - bh + 6; wy < h * 0.52 - 6; wy += 8) {
            ctx.fillRect(bx + 6, wy, 4, 4);
            ctx.fillRect(bx + 16, wy, 4, 4);
          }
        }
      }

      // Tactical HUD Overlay
      if (showFootageOverlay) {
        const cx = w / 2;
        const cy = h / 2;

        ctx.strokeStyle = footageMode === 'NIGHT_VISION' ? '#4ade80' : '#38bdf8';
        ctx.lineWidth = 1.2;
        ctx.font = '9px monospace';
        ctx.fillStyle = ctx.strokeStyle;

        // Pitch Ladder
        ctx.beginPath();
        ctx.moveTo(cx - 30, cy); ctx.lineTo(cx - 15, cy);
        ctx.moveTo(cx + 15, cy); ctx.lineTo(cx + 30, cy);
        ctx.moveTo(cx, cy - 25); ctx.lineTo(cx, cy - 15);
        ctx.moveTo(cx, cy + 15); ctx.lineTo(cx, cy + 25);
        ctx.stroke();

        // Center reticle
        ctx.strokeRect(cx - 5, cy - 5, 10, 10);

        // Infrastructure Target Lock Box (e.g. Skytower-01)
        const targetX = cx + Math.sin(t * 0.8) * 45;
        const targetY = cy - 20 + Math.cos(t * 0.6) * 15;
        ctx.strokeStyle = '#ef4444';
        ctx.strokeRect(targetX - 18, targetY - 18, 36, 36);
        ctx.fillStyle = '#ef4444';
        ctx.fillText('TARGET: SKYTOWER-01', targetX - 25, targetY - 22);
        ctx.fillText('RNG: 284m | ELEV: +12°', targetX - 25, targetY + 28);

        // Heading Tape
        ctx.fillStyle = 'rgba(15, 23, 42, 0.75)';
        ctx.fillRect(cx - 75, 8, 150, 18);
        ctx.strokeStyle = '#0284c7';
        ctx.strokeRect(cx - 75, 8, 150, 18);
        ctx.fillStyle = '#38bdf8';
        ctx.textAlign = 'center';
        const hdg = Math.round((t * 14) % 360);
        ctx.fillText(`HDG: ${String(hdg).padStart(3, '0')}°  [POV TRACK]`, cx, 20);

        // Flight Telemetry Overlays
        ctx.textAlign = 'left';
        ctx.fillText(`ALT: ${flightAltitudeMeters} M (MSL)`, 10, cy - 18);
        ctx.fillText(`SPD: ${flightSpeedKnots} KTS`, 10, cy);
        ctx.fillText(`LAT: ${currentLatencyMicros.toFixed(1)} μs`, 10, cy + 18);

        ctx.textAlign = 'right';
        ctx.fillText(`ZOOM: ${footageZoom.toFixed(1)}X`, w - 10, cy - 18);
        ctx.fillText(`5D TENSOR: ACTIVE`, w - 10, cy);
        ctx.fillText(`BATT: ${batteryPct}%`, w - 10, cy + 18);

        // Scanlines
        ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        for (let y = 0; y < h; y += 4) {
          ctx.fillRect(0, y, w, 1.2);
        }
      }

      animId = requestAnimationFrame(renderLiveCam);
    };

    renderLiveCam();

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [footageMode, showFootageOverlay, footageZoom, flightSpeedKnots, flightAltitudeMeters, currentLatencyMicros, batteryPct]);

  return (
    <div className="space-y-4">
      {/* Top Status & Controls Header */}
      <div className="flex flex-wrap items-center justify-between text-xs bg-slate-900/60 border border-slate-800 px-3.5 py-2 rounded">
        <div className="flex items-center space-x-2 text-slate-300">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span className="font-bold">5D FIRST PERSON POV • REAL-TIME 3D TERRAIN & INFRASTRUCTURE MATRIX</span>
        </div>
        <div className="flex items-center space-x-4 text-slate-400 font-mono text-[11px]">
          <span>SPEED: <strong className="text-emerald-400">{flightSpeedKnots} KTS</strong></span>
          <span>•</span>
          <span>ALTITUDE: <strong className="text-cyan-300">{flightAltitudeMeters}M MSL</strong></span>
          <span>•</span>
          <span>TARGET LOCK: <strong className="text-amber-300">SKYTOWER-01</strong></span>
        </div>
      </div>

      {/* Main Viewport Container */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* 3D SPATIAL TERRAIN & INFRASTRUCTURE VIEWPORT (8 cols or 12 cols if fullscreen) */}
        <div className={`${isFullscreenPOV ? 'lg:col-span-12 h-[680px]' : 'lg:col-span-8 h-[520px]'} bg-slate-950 border border-blue-900/70 rounded shadow-lg overflow-hidden flex flex-col justify-between relative group`}>
          {/* Top Viewport Navigation Bar */}
          <div className="border-b border-blue-900/60 px-4 py-2 bg-slate-900/80 backdrop-blur flex flex-wrap items-center justify-between gap-2 z-10">
            <div className="flex items-center space-x-2">
              <Crosshair className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-bold tracking-wider text-blue-400 uppercase font-mono">
                {viewMode === 'COCKPIT_POV' ? '5D Drone Cockpit First-Person POV' : 'Reconnaissance Situational View'}
              </span>
              <span className="text-[10px] bg-cyan-950/80 text-cyan-300 border border-cyan-800 px-1.5 py-0.5 rounded font-mono">
                3D Terrain + City Grid
              </span>
            </div>

            {/* View Modes Switcher */}
            <div className="flex items-center space-x-1 bg-slate-950 p-0.5 rounded border border-slate-800 text-[11px] font-mono">
              {[
                { id: 'COCKPIT_POV', label: '1st Person POV' },
                { id: 'FLYOVER_RECON', label: 'Flyover Recon' },
                { id: 'ORBIT', label: 'Orbit 360°' },
                { id: 'TOP_DOWN', label: 'Satellite 3D' },
              ].map((m) => (
                <button
                  key={m.id}
                  onClick={() => setViewMode(m.id as any)}
                  className={`px-2 py-0.5 rounded transition cursor-pointer ${
                    viewMode === m.id
                      ? 'bg-cyan-950 text-cyan-300 border border-cyan-500 font-bold'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {m.label}
                </button>
              ))}

              {/* Fullscreen Toggle */}
              <button
                onClick={() => setIsFullscreenPOV(!isFullscreenPOV)}
                title={isFullscreenPOV ? 'Exit Fullscreen' : 'Fullscreen POV'}
                className="p-1 ml-1 text-slate-400 hover:text-cyan-300 cursor-pointer"
              >
                {isFullscreenPOV ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          {/* Interactive 3D Canvas */}
          <div
            ref={mountRef}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onWheel={handleWheel}
            className="w-full flex-1 cursor-grab active:cursor-grabbing relative select-none"
          >
            {/* Live First Person HUD Overlay on Canvas when in COCKPIT_POV */}
            {viewMode === 'COCKPIT_POV' && (
              <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-4 font-mono">
                <div className="flex justify-between items-start">
                  <div className="bg-slate-950/75 backdrop-blur p-2.5 rounded border border-cyan-900/60 text-[11px] space-y-1">
                    <div className="text-cyan-400 font-bold flex items-center space-x-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                      <span>FIRST PERSON GIMBAL: STABILIZED</span>
                    </div>
                    <div className="text-slate-300">POSITION: X: {currentCoords3D.x.toFixed(1)}m | Y: {currentCoords3D.y.toFixed(1)}m | Z: {currentCoords3D.z.toFixed(1)}m</div>
                    <div className="text-slate-300">TERRAIN ELEVATION: <strong className="text-emerald-400">{flightAltitudeMeters}m MSL</strong></div>
                    <div className="text-slate-300">AUTONOMOUS CORRIDOR: <strong className="text-cyan-300">WGS-84 VECTOR</strong></div>
                  </div>

                  <div className="bg-slate-950/75 backdrop-blur p-2.5 rounded border border-cyan-900/60 text-[11px] text-right space-y-1">
                    <div className="text-amber-400 font-bold">INFRASTRUCTURE SCAN: ACTIVE</div>
                    <div className="text-slate-300">LOCKED: <span className="text-red-400 font-bold">{nearestTarget}</span></div>
                    <div className="text-slate-400">LATENCY: <span className="text-emerald-400 font-bold">{currentLatencyMicros.toFixed(1)} μs</span></div>
                  </div>
                </div>

                {/* Center Reticle */}
                <div className="self-center flex flex-col items-center">
                  <div className="w-10 h-10 border border-cyan-400/50 rounded-full flex items-center justify-center">
                    <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full" />
                  </div>
                  <span className="text-[10px] text-cyan-300 bg-slate-950/70 px-1 rounded mt-1">GIMBAL LOCK</span>
                </div>

                <div className="flex justify-between items-end text-[10px] text-slate-400">
                  <span className="bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
                    Use slider controls below to change airspeed & altitude
                  </span>
                  <span className="bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
                    5D Point Cloud + Terrain Contours Rendered
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Bottom Flight & View Controls Bar */}
          <div className="border-t border-blue-900/40 p-3 bg-slate-900/50 flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
            {/* Airspeed Slider */}
            <div className="flex items-center space-x-2 flex-1 min-w-[200px]">
              <span className="text-slate-400 flex items-center space-x-1 whitespace-nowrap text-[11px]">
                <Gauge className="w-3.5 h-3.5 text-cyan-400" />
                <span>Airspeed:</span>
              </span>
              <input
                type="range"
                min="20"
                max="120"
                step="5"
                value={flightSpeedKnots}
                onChange={(e) => setFlightSpeedKnots(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
              <span className="text-cyan-300 font-bold w-14 text-right text-[11px]">
                {flightSpeedKnots} kts
              </span>
            </div>

            {/* Altitude Slider */}
            <div className="flex items-center space-x-2 flex-1 min-w-[200px]">
              <span className="text-slate-400 flex items-center space-x-1 whitespace-nowrap text-[11px]">
                <Plane className="w-3.5 h-3.5 text-emerald-400" />
                <span>Altitude:</span>
              </span>
              <input
                type="range"
                min="50"
                max="400"
                step="10"
                value={flightAltitudeMeters}
                onChange={(e) => setFlightAltitudeMeters(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-emerald-400"
              />
              <span className="text-emerald-300 font-bold w-14 text-right text-[11px]">
                {flightAltitudeMeters} m
              </span>
            </div>

            {/* Orbit Auto Spin control */}
            {viewMode === 'ORBIT' && (
              <button
                onClick={() => setIsAutoSpinning(!isAutoSpinning)}
                className={`flex items-center space-x-1 px-2.5 py-1 rounded text-[11px] font-semibold border transition cursor-pointer ${
                  isAutoSpinning
                    ? 'bg-cyan-950 border-cyan-500 text-cyan-300'
                    : 'bg-slate-900 border-slate-800 text-slate-400'
                }`}
              >
                <RotateCw className={`w-3.5 h-3.5 ${isAutoSpinning ? 'animate-spin' : ''}`} />
                <span>{isAutoSpinning ? 'Auto Orbit' : 'Orbit Paused'}</span>
              </button>
            )}
          </div>
        </div>

        {/* RIGHT: REAL-TIME FIRST-PERSON GIMBAL CAMERA STREAM (4 cols, hidden if full-screen) */}
        {!isFullscreenPOV && (
          <div className="lg:col-span-4 bg-slate-950 border border-blue-900/70 rounded shadow-lg overflow-hidden flex flex-col justify-between">
            <div className="border-b border-blue-900/60 px-4 py-2.5 bg-slate-900/80 flex items-center justify-between">
              <span className="text-xs font-bold tracking-wider text-blue-400 uppercase flex items-center space-x-1.5 font-mono">
                <Camera className="w-4 h-4 text-emerald-400" />
                <span>Live Drone Sensor Stream</span>
              </span>
              <div className="flex items-center space-x-1.5 text-xs font-mono text-red-400 font-bold">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
                <span>LIVE FEED</span>
              </div>
            </div>

            <div className="p-4 space-y-3 flex-1 flex flex-col">
              {/* Live Canvas Gimbal Feed */}
              <div className="relative rounded overflow-hidden border border-cyan-800/80 bg-black aspect-video flex items-center justify-center shadow-inner">
                <canvas
                  ref={videoCanvasRef}
                  width={380}
                  height={220}
                  className="w-full h-full object-cover"
                />

                <div className="absolute top-2 left-2 text-[10px] font-mono text-cyan-400 bg-black/60 px-1.5 py-0.5 rounded">
                  REC ● {telemetryTimecode}
                </div>

                <div className="absolute top-2 right-2 text-[10px] font-mono text-emerald-400 bg-black/60 px-1.5 py-0.5 rounded border border-emerald-800">
                  {footageMode}
                </div>
              </div>

              {/* Multi-Spectrum Sensor Selector */}
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-mono text-slate-400">Sensor Spectrum:</label>
                <div className="grid grid-cols-2 gap-1.5 text-xs font-mono">
                  {[
                    { id: 'EO_COLOR', label: 'EO Optical' },
                    { id: 'FLIR_THERMAL', label: 'FLIR Thermal' },
                    { id: 'NIGHT_VISION', label: 'NVG Green' },
                    { id: 'LIDAR_DEPTH', label: 'LiDAR Depth' },
                  ].map((m) => (
                    <button
                      key={m.id}
                      onClick={() => setFootageMode(m.id as any)}
                      className={`py-1.5 px-2 rounded border text-[11px] transition cursor-pointer text-center ${
                        footageMode === m.id
                          ? 'bg-cyan-950 text-cyan-300 border-cyan-500 font-bold'
                          : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                      }`}
                    >
                      {m.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Optical Digital Zoom */}
              <div className="space-y-2 pt-2 border-t border-slate-900 text-xs font-mono">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400 text-[11px]">Gimbal Optical Zoom:</span>
                  <div className="flex items-center space-x-1.5">
                    {[1.0, 1.5, 3.0, 6.0].map((z) => (
                      <button
                        key={z}
                        onClick={() => setFootageZoom(z)}
                        className={`px-1.5 py-0.5 rounded border text-[10px] cursor-pointer ${
                          footageZoom === z
                            ? 'bg-emerald-950 border-emerald-500 text-emerald-300 font-bold'
                            : 'border-slate-800 text-slate-400'
                        }`}
                      >
                        {z}x
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex justify-between items-center pt-1">
                  <span className="text-slate-400 text-[11px]">Tactical HUD Overlay:</span>
                  <button
                    onClick={() => setShowFootageOverlay(!showFootageOverlay)}
                    className={`px-2 py-0.5 rounded border text-[11px] cursor-pointer ${
                      showFootageOverlay
                        ? 'bg-cyan-950 text-cyan-300 border-cyan-600'
                        : 'bg-slate-900 text-slate-500 border-slate-800'
                    }`}
                  >
                    {showFootageOverlay ? 'Enabled' : 'Disabled'}
                  </button>
                </div>
              </div>

              {/* Detected 3D Infrastructure Readout */}
              <div className="bg-slate-900/70 p-2.5 rounded border border-slate-800 text-[11px] font-mono space-y-1">
                <div className="flex justify-between text-slate-300">
                  <span className="text-slate-400">Infrastructure Target:</span>
                  <span className="text-red-400 font-bold">SKYTOWER-01</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span className="text-slate-400">Rangefinder Distance:</span>
                  <span className="text-emerald-400 font-bold">284 meters</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span className="text-slate-400">Environment Rendering:</span>
                  <span className="text-cyan-300 font-bold">REAL-TIME 60 FPS</span>
                </div>
              </div>
            </div>

            <div className="border-t border-blue-900/40 px-3 py-2 bg-slate-900/50 text-[10px] font-mono text-slate-400 flex justify-between items-center">
              <span>5D SENSOR ARRAY: SPATIAL MAPPED</span>
              <span className="text-emerald-400 font-bold">STREAMING</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
