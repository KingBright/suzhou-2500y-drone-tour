export type AtmosphereMode = 'auto' | 'dawn' | 'golden' | 'dusk' | 'night';

export interface Vec3Obj {
  x: number;
  y: number;
  z: number;
}

export interface StationConfig {
  id: string;
  index: number;
  nameZh: string;
  nameEn: string;
  act: number;
  era: 'ancient' | 'transition' | 'modern';
  glb: string;
  extraGlb?: string;
  extraGlbs?: string[];
  owner: string;
  anchor: Vec3Obj;
  xiyuanAnchor?: Vec3Obj;
  shizilinAnchor?: Vec3Obj;
  museumAnchor?: Vec3Obj;
  archCenter?: Vec3Obj & { clearWidth: number; clearHeight: number };
  footprint: { w: number; d: number; maxH: number };
  defaultAtmosphereT: number;
  heroView: {
    cam: [number, number, number];
    lookAt: [number, number, number];
  };
  transitionToNext: string;
}

export interface ModularKitConfig {
  id: string;
  glb: string;
  owner: string;
  parts: string[];
}

export interface WorldLayout {
  project: string;
  coordinateSystem: {
    unit: string;
    threeUp: string;
    waterLevelY: number;
    groundLevelY: number;
    worldBounds: {
      minX: number;
      maxX: number;
      minZ: number;
      maxZ: number;
    };
    note: string;
  };
  waterBodies: {
    grandCanal: { xCenter: number; width: number; runsNorthSouth: boolean };
    shantangCanal: { from: [number, number]; to: [number, number]; width: number };
    outerMoat: { minX: number; maxX: number; minZ: number; maxZ: number; width: number };
    pingjiangCanal: { from: [number, number]; to: [number, number]; width: number };
    jinjiLake: { centerX: number; centerZ: number; radiusX: number; radiusZ: number };
  };
  stations: StationConfig[];
  modularKits: ModularKitConfig[];
}

export interface LookDevState {
  lights: {
    sunColor: string;
    sunIntensity: number;
    sunElevation: number;
    sunAzimuth: number;
    shadowBias: number;
    hemiSkyColor: string;
    hemiGroundColor: string;
    hemiIntensity: number;
    fillColor: string;
    fillIntensity: number;
  };
  emissives: {
    warm: number;
    gold: number;
    cyan: number;
    accent: number;
  };
  materials: {
    waterColor: string;
    waterDeepColor: string;
    waterRoughness: number;
    waveScale: number;
    waveSpeed: number;
    waterShimmer: number;
  };
  atmosphere: {
    mode: AtmosphereMode;
    timeOfDay: number;
    fogDensity: number;
    fogColor: string;
    skyTurbidity: number;
    skyGlow: number;
  };
  drone: {
    speedScale: number;
    baseFov: number;
    swoopFovBoost: number;
    rollStrength: number;
  };
  postProcessing: {
    exposure: number;
    bloomEnabled: boolean;
    bloomThreshold: number;
    bloomStrength: number;
    bloomRadius: number;
    vignetteIntensity: number;
  };
}

export interface TelemetryStats {
  fps: number;
  drawCalls: number;
  triangles: number;
  activeLights: number;
  loadedModels: string[];
  missingModels: string[];
  currentStation: number;
  currentStationId: string;
  currentStationName: string;
  atmosphereMode: AtmosphereMode;
  timeOfDay: number;
  progress: number;
  freeFly: boolean;
}

export interface SuzhouDebugAPI {
  jumpToStation: (index1Based: number) => void;
  setProgress: (p: number) => void;
  setAtmosphere: (mode: AtmosphereMode) => void;
  setTimeOfDay: (t: number) => void;
  setPaused: (paused: boolean) => void;
  setFreeFly: (enabled: boolean) => void;
  toggleLookDev: (open?: boolean) => void;
  togglePanel: (open?: boolean) => void;
  setHideUI: (hidden: boolean) => void;
  hideAllUI: (hidden: boolean) => void;
  getLookDevState: () => LookDevState;
  getStats: () => TelemetryStats;
  setCaptureMode: (enabled: boolean) => void;
  stepFrame: (dt: number, simTime: number, speedScale?: number) => TelemetryStats;
  whenReady: () => Promise<void>;
}

declare global {
  interface Window {
    __SUZHOU_DEBUG__?: SuzhouDebugAPI;
  }
}
