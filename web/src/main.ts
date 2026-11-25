import './styles.css';
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';

import worldLayoutRaw from './config/world-layout.json';
import { createDefaultLookDevState } from './config/defaults';
import type { AtmosphereMode, LookDevState, TelemetryStats, WorldLayout } from './types/world';
import { createTerrainSystem } from './scene/terrain';
import { AtmosphereManager } from './scene/atmosphere';
import { createDynamicLifeSystem } from './scene/dynamicLife';
import { loadAllLandmarks } from './scene/landmarkLoader';
import { buildCityScatter } from './scene/cityScatter';
import { DroneCinematographyEngine } from './camera/droneEngine';
import { SpeedLinesOverlay } from './ui/speedLines';
import { CinemaHUD } from './ui/hud';
import { LookDevPanel } from './ui/lookdevPanel';

const layout = worldLayoutRaw as unknown as WorldLayout;

async function bootstrap(): Promise<void> {
  const canvas = document.getElementById('webgl-canvas') as HTMLCanvasElement;
  const speedCanvas = document.getElementById('speedlines-canvas') as HTMLCanvasElement;
  const vignetteEl = document.getElementById('vignette-overlay') as HTMLElement;
  const hudRoot = document.getElementById('hud-root') as HTMLElement;
  const lookDevRoot = document.getElementById('lookdev-root') as HTMLElement;
  const loadingOverlay = document.getElementById('loading-overlay') as HTMLElement;
  const loadingBarFill = document.getElementById('loading-bar-fill') as HTMLElement;
  const loadingStatus = document.getElementById('loading-status') as HTMLElement;

  // --- 1. RENDERER & COMPOSER ---
  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    powerPreference: 'high-performance'
  });
  const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
  renderer.setPixelRatio(dpr);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.04;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.info.autoReset = false;

  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 1.5, 6800);

  // Clean post-processing pipeline: RenderPass -> UnrealBloomPass (half-res for 60 FPS!) -> OutputPass
  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(dpr);
  composer.setSize(window.innerWidth, window.innerHeight);

  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);

  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(Math.floor(window.innerWidth * 0.5), Math.floor(window.innerHeight * 0.5)),
    0.18,
    0.45,
    0.92
  );
  composer.addPass(bloomPass);

  const outputPass = new OutputPass();
  composer.addPass(outputPass);

  // --- 2. TERRAIN, WATER, ATMOSPHERE & DYNAMIC LIFE ---
  const lookDevState: LookDevState = createDefaultLookDevState();

  const terrain = createTerrainSystem(layout);
  scene.add(terrain.group);

  const atmosphere = new AtmosphereManager(scene, renderer, terrain.waterUniforms);

  const dynamicLife = createDynamicLifeSystem();
  scene.add(dynamicLife.group);

  // --- 3. DRONE CINEMATOGRAPHY ENGINE & UI ---
  const drone = new DroneCinematographyEngine(layout, camera, canvas);
  const speedLines = new SpeedLinesOverlay(speedCanvas);

  let uiHidden = false;
  const setHideUI = (hidden: boolean) => {
    uiHidden = hidden;
    document.body.classList.toggle('ui-hidden', hidden);
  };

  let lookDevPanel!: LookDevPanel;

  const setAtmosphereMode = (mode: AtmosphereMode, instant = false) => {
    lookDevState.atmosphere.mode = mode;
    atmosphere.setMode(mode, instant);
    lookDevPanel?.refreshValues();
  };

  const resetDefaults = () => {
    const fresh = createDefaultLookDevState();
    Object.assign(lookDevState.lights, fresh.lights);
    Object.assign(lookDevState.emissives, fresh.emissives);
    Object.assign(lookDevState.materials, fresh.materials);
    Object.assign(lookDevState.atmosphere, fresh.atmosphere);
    Object.assign(lookDevState.drone, fresh.drone);
    Object.assign(lookDevState.postProcessing, fresh.postProcessing);
    atmosphere.clearOverrides();
    atmosphere.setMode(fresh.atmosphere.mode, false);
  };

  const hud = new CinemaHUD(hudRoot, layout, {
    onSelectStation: (idx) => drone.jumpToStation(idx, false),
    onSelectAtmosphere: (mode) => setAtmosphereMode(mode, false),
    onTogglePlay: () => {
      drone.paused = !drone.paused;
    },
    onScrub: (p) => drone.setProgress(p, lookDevState),
    onToggleFreeFly: () => drone.setFreeFly(!drone.freeFly),
    onToggleLookDev: () => lookDevPanel.toggle(),
    onToggleHideUI: () => setHideUI(!uiHidden)
  });

  lookDevPanel = new LookDevPanel(lookDevRoot, lookDevState, {
    onAtmosphereMode: (m) => setAtmosphereMode(m, false),
    onTimeOfDayScrub: (t) => {
      lookDevState.atmosphere.mode = t < 0.16 ? 'dawn' : t < 0.48 ? 'golden' : t < 0.8 ? 'dusk' : 'night';
      atmosphere.setTimeOfDay(t, lookDevState);
    },
    onManualOverride: (group) => atmosphere.markUserOverride(group),
    onResetDefaults: resetDefaults
  });

  // --- 4. LOAD ALL 15 HERO LANDMARKS + 2 MODULAR CITY KITS ---
  let loadedModels: string[] = [];
  let missingModels: string[] = [];
  let ferrisRotor: THREE.Object3D | null = null;
  let ferrisAxis: 'x' | 'y' | 'z' = 'x';
  let readyResolve!: () => void;
  const readyPromise = new Promise<void>((res) => {
    readyResolve = res;
  });

  // Capture true 3D scene draw calls & triangles right when RenderPass completes (before Bloom/OutputPass)
  let fpsValue = 60;
  let lastDrawCalls = 0;
  let lastTriangles = 0;
  scene.onAfterRender = () => {
    lastDrawCalls = renderer.info.render.calls;
    lastTriangles = renderer.info.render.triangles;
  };

  const renderFrame = () => {
    renderer.info.reset();
    composer.render();
  };

  const getStats = (): TelemetryStats => {
    const st = layout.stations[Math.min(Math.max(drone.currentStationIndex - 1, 0), layout.stations.length - 1)];
    return {
      fps: fpsValue,
      drawCalls: lastDrawCalls,
      triangles: lastTriangles,
      activeLights: atmosphere.getActiveLightCount(),
      loadedModels: [...loadedModels],
      missingModels: [...missingModels],
      currentStation: st.index,
      currentStationId: st.id,
      currentStationName: st.nameZh,
      atmosphereMode: lookDevState.atmosphere.mode,
      timeOfDay: Number(lookDevState.atmosphere.timeOfDay.toFixed(3)),
      progress: Number(drone.progress.toFixed(4)),
      freeFly: drone.freeFly
    };
  };

  const renderOnceImmediately = () => {
    atmosphere.update(0.016, performance.now() * 0.001, drone.progress, camera.position, lookDevState, bloomPass);
    renderFrame();
    hud.update(getStats(), drone.paused, lookDevPanel.open);
  };

  let captureMode = false;

  const stepSimulation = (dt: number, elapsed: number, forceHud = false) => {
    drone.update(dt, lookDevState);
    atmosphere.update(dt, elapsed, drone.progress, camera.position, lookDevState, bloomPass);
    dynamicLife.update(elapsed, atmosphere.currentNightFactor, atmosphere.currentEmissiveGlobal);
    if (ferrisRotor) {
      ferrisRotor.rotation[ferrisAxis] += dt * 0.16;
    }
    vignetteEl.style.opacity = String(lookDevState.postProcessing.vignetteIntensity);
    renderFrame();
    speedLines.render(elapsed, drone.speedIntensity, atmosphere.currentNightFactor, uiHidden);
    if (forceHud) {
      hud.update(getStats(), drone.paused, lookDevPanel.open);
    }
  };

  window.__SUZHOU_DEBUG__ = {
    jumpToStation: (index1Based: number) => {
      drone.jumpToStation(index1Based, true);
      renderOnceImmediately();
    },
    setProgress: (p: number) => {
      drone.setProgress(p, lookDevState);
      renderOnceImmediately();
    },
    setAtmosphere: (mode: AtmosphereMode) => {
      setAtmosphereMode(mode, true);
      renderOnceImmediately();
    },
    setTimeOfDay: (t: number) => {
      lookDevState.atmosphere.mode = t < 0.16 ? 'dawn' : t < 0.48 ? 'golden' : t < 0.8 ? 'dusk' : 'night';
      atmosphere.setTimeOfDay(t, lookDevState);
      renderOnceImmediately();
    },
    setPaused: (paused: boolean) => {
      drone.paused = paused;
      renderOnceImmediately();
    },
    setFreeFly: (enabled: boolean) => {
      drone.setFreeFly(enabled);
      renderOnceImmediately();
    },
    toggleLookDev: (open?: boolean) => {
      lookDevPanel.setOpen(open !== undefined ? open : !lookDevPanel.open);
      renderOnceImmediately();
    },
    togglePanel: (open?: boolean) => {
      lookDevPanel.setOpen(open !== undefined ? open : !lookDevPanel.open);
      renderOnceImmediately();
    },
    setHideUI: (hidden: boolean) => {
      setHideUI(hidden);
    },
    hideAllUI: (hidden: boolean) => {
      setHideUI(hidden);
    },
    getLookDevState: () => structuredClone(lookDevState),
    getStats,
    setCaptureMode: (enabled: boolean) => {
      captureMode = enabled;
      if (enabled) {
        fpsValue = 30;
      }
    },
    stepFrame: (dt: number, simTime: number, speedScale?: number) => {
      if (speedScale !== undefined) {
        lookDevState.drone.speedScale = speedScale;
      }
      stepSimulation(dt, simTime, true);
      return getStats();
    },
    whenReady: () => readyPromise
  };

  // --- 5. KEYBOARD SHORTCUTS ---
  window.addEventListener('keydown', (e) => {
    if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLSelectElement) {
      return;
    }
    if (e.code === 'Space') {
      e.preventDefault();
      drone.paused = !drone.paused;
    } else if (e.code === 'KeyG') {
      e.preventDefault();
      if (uiHidden) setHideUI(false);
      lookDevPanel.toggle();
    } else if (e.code === 'KeyH') {
      e.preventDefault();
      setHideUI(!uiHidden);
    } else if (e.code === 'KeyF') {
      e.preventDefault();
      drone.setFreeFly(!drone.freeFly);
    } else if (!drone.freeFly && e.key >= '1' && e.key <= '9') {
      drone.jumpToStation(Number(e.key), false);
    } else if (!drone.freeFly && e.key === '0') {
      drone.jumpToStation(10, false);
    } else if (!drone.freeFly && e.key === '-') {
      drone.jumpToStation(11, false);
    } else if (!drone.freeFly && e.key === '=') {
      drone.jumpToStation(12, false);
    }
  });

  // --- 6. RESIZE HANDLER ---
  window.addEventListener('resize', () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    const curDpr = Math.min(window.devicePixelRatio || 1, 1.5);
    renderer.setPixelRatio(curDpr);
    renderer.setSize(w, h);
    composer.setPixelRatio(curDpr);
    composer.setSize(w, h);
    bloomPass.resolution.set(Math.floor(w * 0.5), Math.floor(h * 0.5));
    speedLines.resize();
  });

  // --- 7. ASYNC LOAD HERO LANDMARKS & INSTANCED CITY ---
  const [landmarks, cityScatter] = await Promise.all([
    loadAllLandmarks(layout, atmosphere, (done, total, label) => {
      const pct = Math.round(15 + (done / total) * 70);
      loadingBarFill.style.width = `${pct}%`;
      loadingStatus.textContent = `加载苏州地标模型 (${done}/${total}) · ${label}`;
    }),
    buildCityScatter(layout, terrain, atmosphere)
  ]);

  scene.add(landmarks.group);
  scene.add(cityScatter.group);

  loadedModels = [...landmarks.loadedModels, ...cityScatter.loadedKits];
  missingModels = [...landmarks.missingModels, ...cityScatter.missingKits];
  ferrisRotor = landmarks.ferrisWheelRotor;
  ferrisAxis = landmarks.ferrisRotationAxis;

  loadingBarFill.style.width = '100%';
  loadingStatus.textContent = `已就绪 · ${loadedModels.length} 个高精度模型 · ${cityScatter.instanceCount} 个实例化城景`;

  // Prime first frame cleanly before hiding loader
  atmosphere.update(0.016, 0, drone.progress, camera.position, lookDevState, bloomPass);
  renderFrame();

  window.setTimeout(() => loadingOverlay.classList.add('hidden'), 220);
  readyResolve();

  // --- 8. MAIN ANIMATION LOOP (45–60 FPS) ---
  let lastTime = performance.now();
  let fpsAccum = 0;
  let fpsFrames = 0;
  let uiTickAccum = 0;

  const animate = (now: number) => {
    requestAnimationFrame(animate);
    if (captureMode) return;

    const dt = Math.min((now - lastTime) * 0.001, 0.05);
    lastTime = now;
    const elapsed = now * 0.001;

    stepSimulation(dt, elapsed, false);

    // Telemetry & HUD update (throttled to ~6Hz so DOM never steals GPU frame time!)
    fpsAccum += dt;
    fpsFrames++;
    uiTickAccum += dt;
    if (fpsAccum >= 0.5) {
      fpsValue = Math.round(fpsFrames / fpsAccum);
      fpsAccum = 0;
      fpsFrames = 0;
    }
    if (uiTickAccum >= 0.16) {
      uiTickAccum = 0;
      hud.update(getStats(), drone.paused, lookDevPanel.open);
      lookDevPanel.refreshValues();
    }
  };

  requestAnimationFrame(animate);
}

bootstrap().catch((err) => {
  console.error('[SuzhouDroneTour] Fatal startup error:', err);
});
