import * as THREE from 'three';
import type { LookDevState, StationConfig, WorldLayout } from '../types/world';

interface Waypoint {
  cam: [number, number, number];
  lookAt: [number, number, number];
  /** Relative playback speed multiplier on the segment leading out of this point: 1.0 = scenic, 5.5..8.0 = high-speed swoop */
  speed: number;
  /** Station index (1..12) associated with this waypoint */
  stationIndex: number;
  /** True if this waypoint is the canonical hero frame for its station */
  isHero?: boolean;
}

export class DroneCinematographyEngine {
  private readonly layout: WorldLayout;
  private readonly camera: THREE.PerspectiveCamera;
  private readonly posCurve: THREE.CatmullRomCurve3;
  private readonly lookCurve: THREE.CatmullRomCurve3;
  private readonly waypoints: Waypoint[];
  private readonly stationHeroU = new Map<number, number>();
  private readonly totalDurationSec = 115; // ~115s continuous cinematic tour

  public progress = 0; // Normalized timeline progress [0..1]
  public paused = false;
  public freeFly = false;
  public speedIntensity = 0; // 0 = scenic, 1 = max swoop speed
  public currentStationIndex = 1;

  // Smooth station jump interpolation
  private jumpActive = false;
  private jumpElapsed = 0;
  private jumpDuration = 1.25;
  private jumpStartPos = new THREE.Vector3();
  private jumpStartLook = new THREE.Vector3();
  private jumpTargetU = 0;

  // Free-fly state
  private readonly keys = new Set<string>();
  private isDragging = false;
  private lastPointerX = 0;
  private lastPointerY = 0;
  private yaw = 0;
  private pitch = 0;

  // Smoothed cinema telemetry
  private smoothFov = 48;
  private smoothRoll = 0;

  // Reusable scratch objects (zero per-frame allocations)
  private readonly tmpPos = new THREE.Vector3();
  private readonly tmpPosPrev = new THREE.Vector3();
  private readonly tmpPosNext = new THREE.Vector3();
  private readonly tmpLook = new THREE.Vector3();
  private readonly tmpFwd = new THREE.Vector3();
  private readonly tmpNextFwd = new THREE.Vector3();
  private readonly tmpRight = new THREE.Vector3();
  private readonly tmpUp = new THREE.Vector3();
  private readonly tmpWorldUp = new THREE.Vector3(0, 1, 0);
  private readonly tmpMatrix = new THREE.Matrix4();
  private readonly tmpQuat = new THREE.Quaternion();
  private readonly tmpRollQuat = new THREE.Quaternion();
  private readonly tmpMove = new THREE.Vector3();
  private readonly domElement: HTMLElement;

  constructor(layout: WorldLayout, camera: THREE.PerspectiveCamera, domElement: HTMLElement) {
    this.layout = layout;
    this.camera = camera;
    this.domElement = domElement;
    this.waypoints = this.buildWaypoints();

    const posPts = this.waypoints.map((w) => new THREE.Vector3(...w.cam));
    const lookPts = this.waypoints.map((w) => new THREE.Vector3(...w.lookAt));
    this.posCurve = new THREE.CatmullRomCurve3(posPts, false, 'centripetal', 0.45);
    this.lookCurve = new THREE.CatmullRomCurve3(lookPts, false, 'centripetal', 0.45);

    const n = this.waypoints.length - 1;
    this.waypoints.forEach((wp, idx) => {
      if (wp.isHero) {
        this.stationHeroU.set(wp.stationIndex, idx / n);
      }
    });

    this.bindFreeFlyInput();
    this.applyCurvePose(0, 0.016, 48, 32, 1.0, true);
  }

  private buildWaypoints(): Waypoint[] {
    const s = this.layout.stations;
    return [
      // === STATION 01: Hanshan Temple & Maple Bridge ===
      { cam: s[0].heroView.cam, lookAt: s[0].heroView.lookAt, speed: 0.9, stationIndex: 1, isHero: true },
      { cam: [-1395, 22, 140], lookAt: [-1340, 18, 95], speed: 1.1, stationIndex: 1 },
      { cam: [-1315, 14, 70], lookAt: [-1315, 16, -20], speed: 5.8, stationIndex: 1 }, // Swoop down Grand Canal!

      // === SWOOP 1->2: Up Grand Canal past Xiyuan Temple to Tiger Hill ===
      { cam: [-1265, 28, -95], lookAt: [-1080, 18, -160], speed: 6.5, stationIndex: 2 },
      { cam: [-1015, 42, -195], lookAt: [-920, 44, -355], speed: 5.2, stationIndex: 2 },

      // === STATION 02: Xiyuan Temple & Tiger Hill Leaning Pagoda ===
      { cam: s[1].heroView.cam, lookAt: s[1].heroView.lookAt, speed: 0.95, stationIndex: 2, isHero: true },
      { cam: [-855, 68, -420], lookAt: [-920, 48, -360], speed: 1.2, stationIndex: 2 },
      { cam: [-875, 36, -305], lookAt: [-740, 12, -250], speed: 6.2, stationIndex: 2 }, // Dive down Shantang Canal!

      // === SWOOP 2->3: Shantang Canal ===
      { cam: [-725, 18, -235], lookAt: [-575, 10, -125], speed: 6.0, stationIndex: 3 },

      // === STATION 03: Lingering Garden ===
      { cam: s[2].heroView.cam, lookAt: s[2].heroView.lookAt, speed: 0.9, stationIndex: 3, isHero: true },
      { cam: [-515, 20, -45], lookAt: [-560, 8, -90], speed: 1.2, stationIndex: 3 },
      { cam: [-480, 18, 45], lookAt: [-470, 16, 230], speed: 6.8, stationIndex: 3 }, // High-speed south swoop down West Moat!

      // === SWOOP 3->4: West Moat to Panmen Three Views ===
      { cam: [-478, 22, 245], lookAt: [-370, 26, 340], speed: 5.6, stationIndex: 4 },

      // === STATION 04: Panmen Three Views & Canglang Pavilion (WUMEN BRIDGE ARCH FLY-THROUGH!) ===
      { cam: s[3].heroView.cam, lookAt: s[3].heroView.lookAt, speed: 0.95, stationIndex: 4, isHero: true },
      { cam: [-360, 6.5, 352], lookAt: [-320, 7.0, 352], speed: 1.5, stationIndex: 4 }, // Clear Panmen inner Water Gate lintel & align with Wumen Bridge arch!
      { cam: [-336, 6.8, 352], lookAt: [-255, 10.5, 346], speed: 2.2, stationIndex: 4 }, // Cleanly dead-center through Wumen Bridge's 14.6m arch!
      { cam: [-255, 16, 340], lookAt: [-160, 14, 320], speed: 5.8, stationIndex: 4 }, // Past Canglang Pavilion, swoop east!

      // === SWOOP 4->5: East across southern Gusu ===
      { cam: [-110, 26, 335], lookAt: [75, 20, 245], speed: 6.2, stationIndex: 5 },

      // === STATION 05: Wangshi Garden & Twin Pagodas (TWIN PAGODAS GAP FLY-THROUGH!) ===
      { cam: s[4].heroView.cam, lookAt: s[4].heroView.lookAt, speed: 0.9, stationIndex: 5, isHero: true },
      { cam: [134, 22, 275], lookAt: [134, 22, 210], speed: 1.4, stationIndex: 5 }, // Align with 24.6m gap between Twin Pagodas (world X=116 & 152, Z=232)
      { cam: [134, 23, 215], lookAt: [30, 44, -140], speed: 6.2, stationIndex: 5 }, // Cleanly between Twin Pagodas -> climb NW to 76m Beisi Pagoda!

      // === SWOOP 5->6: Across Gusu skyline to Beisi Pagoda ===
      { cam: [-55, 62, -10], lookAt: [-25, 46, -188], speed: 5.6, stationIndex: 6 },

      // === STATION 06: Beisi Pagoda & Pingjiang Road ===
      { cam: s[5].heroView.cam, lookAt: s[5].heroView.lookAt, speed: 0.95, stationIndex: 6, isHero: true },
      { cam: [38, 56, -248], lookAt: [-25, 44, -188], speed: 1.25, stationIndex: 6 },
      { cam: [70, 17, -235], lookAt: [70, 8, -110], speed: 2.1, stationIndex: 6 }, // Dive right down Pingjiang Road lantern canal (world X=70)!
      { cam: [70, 14, -105], lookAt: [210, 10, -95], speed: 5.0, stationIndex: 7 }, // Whip NE towards Lion Grove!

      // === STATION 07: Lion Grove, Humble Administrator's Garden & Suzhou Museum ===
      { cam: [170, 22, -70], lookAt: [210, 9, -95], speed: 1.5, stationIndex: 7 }, // Glide Lion Grove
      { cam: s[6].heroView.cam, lookAt: s[6].heroView.lookAt, speed: 0.95, stationIndex: 7, isHero: true }, // Hero Humble Admin + Museum
      { cam: [255, 24, -270], lookAt: [265, 8, -215], speed: 1.2, stationIndex: 7 }, // Hop over white wall into Suzhou Museum
      { cam: [320, 22, -140], lookAt: [460, 42, -20], speed: 6.8, stationIndex: 7 }, // Launch onto Ganjiang Road!

      // === SWOOP 7->8: Ganjiang Road High-Speed Light-Trail Rocket to Gate of the Orient ===
      { cam: [390, 62, 15], lookAt: [650, 130, 0], speed: 7.5, stationIndex: 8 },

      // === STATION 08: Gate of the Orient & Suzhou Center (ARCH FLY-THROUGH!) ===
      { cam: s[7].heroView.cam, lookAt: s[7].heroView.lookAt, speed: 1.15, stationIndex: 8, isHero: true },
      { cam: [540, 126, 4], lookAt: [760, 118, 0], speed: 2.8, stationIndex: 8 }, // Align cleanly with arch center
      { cam: [650, 125, 0], lookAt: [830, 72, 0], speed: 4.5, stationIndex: 8 }, // RIGHT THROUGH THE ARCH (clearWidth>=62m, Y=125)!
      { cam: [740, 82, 6], lookAt: [810, 18, 25], speed: 6.2, stationIndex: 8 }, // Dramatic 60° dive!
      { cam: [815, 16, 85], lookAt: [960, 14, 340], speed: 6.8, stationIndex: 9 }, // Low skim past Music Fountain south across Jinji Lake!

      // === SWOOP 8->9: Low lake skim to Ligongdi ===
      { cam: [845, 22, 265], lookAt: [990, 10, 365], speed: 5.5, stationIndex: 9 },

      // === STATION 09: Ligongdi Causeway (ARCH BRIDGE FLY-THROUGH!) ===
      { cam: s[8].heroView.cam, lookAt: s[8].heroView.lookAt, speed: 1.0, stationIndex: 9, isHero: true },
      { cam: [1000, 5.2, 412], lookAt: [1000, 5.6, 345], speed: 2.0, stationIndex: 9 }, // Align dead-straight with Ligongdi central arch (X=1000, Z=365, clearH=14.4m)
      { cam: [1000, 5.2, 355], lookAt: [1005, 8.0, 300], speed: 2.8, stationIndex: 9 }, // Cleanly through Ligongdi Arch Bridge before banking NE!
      { cam: [1065, 22, 315], lookAt: [1260, 52, 165], speed: 6.6, stationIndex: 9 }, // Whip NE across Jinji Lake!

      // === STATION 10: Suzhou MoCA & Eye of Suzhou Ferris Wheel ===
      { cam: s[9].heroView.cam, lookAt: s[9].heroView.lookAt, speed: 0.95, stationIndex: 10, isHero: true },
      { cam: [1235, 32, 165], lookAt: [1310, 52, 125], speed: 1.35, stationIndex: 10 }, // Skim MoCA ribbon roof
      { cam: [1225, 76, 225], lookAt: [1345, 68, 125], speed: 1.6, stationIndex: 10 }, // Wide cinematic sweep framing 128m Eye of Suzhou Ferris Wheel!
      { cam: [1360, 74, 25], lookAt: [1285, 34, -180], speed: 6.2, stationIndex: 10 }, // Bank north along East Lakefront!

      // === STATION 11: Suzhou Culture & Arts Centre & Moon Harbour ===
      { cam: s[10].heroView.cam, lookAt: s[10].heroView.lookAt, speed: 0.95, stationIndex: 11, isHero: true },
      { cam: [1210, 42, -295], lookAt: [1295, 24, -225], speed: 1.35, stationIndex: 11 }, // Drift over crescent dome
      { cam: [1375, 72, -175], lookAt: [1480, 195, -60], speed: 5.8, stationIndex: 11 }, // Launch into East CBD Skyscraper Canyon!

      // === STATION 12: Suzhou IFS (450m Vertical Climb & 180° Climax Panorama!) ===
      { cam: [1415, 120, -45], lookAt: [1480, 290, -60], speed: 3.4, stationIndex: 12 }, // Vertical rocket up 450m glass facade
      { cam: [1360, 315, -15], lookAt: [1480, 405, -60], speed: 2.2, stationIndex: 12 }, // Backed-out hero angle framing the sculpted fishtail crown!
      { cam: [1525, 458, -10], lookAt: [1260, 180, 0], speed: 1.0, stationIndex: 12 }, // Crest the 450m crown and bank west
      { cam: s[11].heroView.cam, lookAt: s[11].heroView.lookAt, speed: 0.65, stationIndex: 12, isHero: true }, // Grand 2500-Year West Panorama!
      { cam: [1645, 470, 55], lookAt: [720, 75, 0], speed: 0.55, stationIndex: 12 } // Lingering cinema finale
    ];
  }

  public getStationForProgress(u: number): StationConfig {
    const n = this.waypoints.length - 1;
    const idx = Math.min(Math.max(Math.round(u * n), 0), n);
    const stIdx = this.waypoints[idx].stationIndex;
    return this.layout.stations[Math.min(Math.max(stIdx - 1, 0), this.layout.stations.length - 1)];
  }

  private getSpeedMultiplierAt(u: number): number {
    const n = this.waypoints.length - 1;
    const f = THREE.MathUtils.clamp(u, 0, 0.9999) * n;
    const i0 = Math.floor(f);
    const i1 = Math.min(i0 + 1, n);
    const frac = f - i0;
    const smooth = frac * frac * (3 - 2 * frac);
    return THREE.MathUtils.lerp(this.waypoints[i0].speed, this.waypoints[i1].speed, smooth);
  }

  public getStationHeroProgress(stationIndex1Based: number): number {
    return this.stationHeroU.get(stationIndex1Based) ?? 0;
  }

  /** Smoothly fly (or snap immediately when deterministic=true) to a station's hero frame */
  public jumpToStation(stationIndex1Based: number, deterministic = false): void {
    const clamped = Math.min(Math.max(Math.round(stationIndex1Based), 1), this.layout.stations.length);
    const targetU = this.getStationHeroProgress(clamped);
    this.freeFly = false;

    if (deterministic) {
      this.jumpActive = false;
      this.progress = targetU;
      this.currentStationIndex = clamped;
      this.speedIntensity = 0;
      this.applyCurvePose(targetU, 0.016, this.camera.fov, 0, 0, true);
      return;
    }

    this.jumpStartPos.copy(this.camera.position);
    this.camera.getWorldDirection(this.tmpFwd);
    this.jumpStartLook.copy(this.camera.position).addScaledVector(this.tmpFwd, 120);
    this.jumpTargetU = targetU;
    this.jumpElapsed = 0;
    this.jumpActive = true;
    this.currentStationIndex = clamped;
  }

  public setProgress(p: number, lookDev: LookDevState): void {
    this.jumpActive = false;
    this.freeFly = false;
    this.progress = THREE.MathUtils.clamp(p, 0, 1);
    this.currentStationIndex = this.getStationForProgress(this.progress).index;
    this.applyCurvePose(
      this.progress,
      0.016,
      lookDev.drone.baseFov,
      lookDev.drone.swoopFovBoost,
      lookDev.drone.rollStrength,
      true
    );
  }

  public setFreeFly(enabled: boolean): void {
    this.freeFly = enabled;
    this.jumpActive = false;
    if (enabled) {
      // Initialize yaw/pitch from current camera direction
      this.camera.getWorldDirection(this.tmpFwd);
      this.yaw = Math.atan2(-this.tmpFwd.x, -this.tmpFwd.z);
      this.pitch = Math.asin(THREE.MathUtils.clamp(this.tmpFwd.y, -0.95, 0.95));
      this.speedIntensity = 0;
    }
  }

  private applyCurvePose(
    u: number,
    dt: number,
    baseFov: number,
    swoopFovBoost: number,
    rollStrength: number,
    instant: boolean
  ): void {
    const uc = THREE.MathUtils.clamp(u, 0, 1);
    this.posCurve.getPoint(uc, this.tmpPos);
    this.lookCurve.getPoint(uc, this.tmpLook);

    const speedMul = this.getSpeedMultiplierAt(uc);
    // Normalize speed intensity: 0 when speed <= 1.6, 1 when speed >= 6.8
    const targetSpeedNorm = THREE.MathUtils.clamp((speedMul - 1.6) / 5.2, 0, 1);
    this.speedIntensity = instant ? targetSpeedNorm : THREE.MathUtils.lerp(this.speedIntensity, targetSpeedNorm, Math.min(dt * 4.5, 1));

    // Dynamic FOV (48° scenic -> up to 82° during explosive inter-landmark swoops!)
    const targetFov = THREE.MathUtils.clamp(baseFov + this.speedIntensity * swoopFovBoost, 38, 86);
    this.smoothFov = instant ? targetFov : THREE.MathUtils.lerp(this.smoothFov, targetFov, Math.min(dt * 4.2, 1));
    if (Math.abs(this.camera.fov - this.smoothFov) > 0.02) {
      this.camera.fov = this.smoothFov;
      this.camera.updateProjectionMatrix();
    }

    // Compute lateral turn curvature for FPV Bank/Roll (±22° max)
    const eps = 0.004;
    this.posCurve.getPoint(Math.max(0, uc - eps), this.tmpPosPrev);
    this.posCurve.getPoint(Math.min(1, uc + eps), this.tmpPosNext);
    this.tmpFwd.subVectors(this.tmpPos, this.tmpPosPrev).normalize();
    this.tmpNextFwd.subVectors(this.tmpPosNext, this.tmpPos).normalize();
    this.tmpRight.crossVectors(this.tmpFwd, this.tmpWorldUp).normalize();
    const lateralTurn = this.tmpNextFwd.dot(this.tmpRight);
    const maxRollRad = THREE.MathUtils.degToRad(22);
    const targetRoll = THREE.MathUtils.clamp(
      -lateralTurn * (4.2 + this.speedIntensity * 6.5) * rollStrength,
      -maxRollRad,
      maxRollRad
    );
    this.smoothRoll = instant ? targetRoll : THREE.MathUtils.lerp(this.smoothRoll, targetRoll, Math.min(dt * 4.8, 1));

    // Orient camera cleanly + apply FPV roll around forward axis
    this.camera.position.copy(this.tmpPos);
    this.tmpMatrix.lookAt(this.tmpPos, this.tmpLook, this.tmpWorldUp);
    this.tmpQuat.setFromRotationMatrix(this.tmpMatrix);

    if (!instant && Math.abs(this.smoothRoll) > 0.0005) {
      this.tmpFwd.subVectors(this.tmpLook, this.tmpPos).normalize();
      this.tmpRollQuat.setFromAxisAngle(this.tmpFwd, this.smoothRoll);
      this.tmpQuat.premultiply(this.tmpRollQuat);
    }
    this.camera.quaternion.copy(this.tmpQuat);
  }

  public update(dt: number, lookDev: LookDevState): void {
    const safeDt = Math.min(dt, 0.05);

    if (this.freeFly) {
      this.updateFreeFly(safeDt, lookDev);
      return;
    }

    if (this.jumpActive) {
      this.jumpElapsed += safeDt;
      const t = Math.min(this.jumpElapsed / this.jumpDuration, 1);
      const ease = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

      this.posCurve.getPoint(this.jumpTargetU, this.tmpPos);
      this.lookCurve.getPoint(this.jumpTargetU, this.tmpLook);

      this.camera.position.lerpVectors(this.jumpStartPos, this.tmpPos, ease);
      this.tmpPosNext.lerpVectors(this.jumpStartLook, this.tmpLook, ease);
      this.camera.lookAt(this.tmpPosNext);
      this.speedIntensity = Math.sin(t * Math.PI) * 0.72;

      const targetFov = lookDev.drone.baseFov + this.speedIntensity * lookDev.drone.swoopFovBoost * 0.6;
      this.smoothFov = THREE.MathUtils.lerp(this.smoothFov, targetFov, Math.min(safeDt * 6, 1));
      this.camera.fov = this.smoothFov;
      this.camera.updateProjectionMatrix();

      if (t >= 1) {
        this.jumpActive = false;
        this.progress = this.jumpTargetU;
      }
      return;
    }

    if (!this.paused) {
      // Speed-ramped progress advance: scenic landmarks play slower, inter-station swoops surge rapidly!
      const speedMul = this.getSpeedMultiplierAt(this.progress);
      // Normalize average speed across all waypoints so total tour stays ~115s
      const avgSpeed = 2.65;
      const deltaU = ((safeDt / this.totalDurationSec) * (speedMul / avgSpeed)) * lookDev.drone.speedScale;
      this.progress += deltaU;
      if (this.progress >= 1.0) {
        this.progress = 0.0; // Seamless loop!
      }
    }

    this.currentStationIndex = this.getStationForProgress(this.progress).index;
    this.applyCurvePose(
      this.progress,
      safeDt,
      lookDev.drone.baseFov,
      lookDev.drone.swoopFovBoost,
      lookDev.drone.rollStrength,
      false
    );
  }

  private updateFreeFly(dt: number, lookDev: LookDevState): void {
    const boost = this.keys.has('ShiftLeft') || this.keys.has('ShiftRight') ? 2.8 : 1.0;
    const speed = 115 * boost * lookDev.drone.speedScale;

    this.camera.rotation.order = 'YXZ';
    this.camera.rotation.set(this.pitch, this.yaw, 0);

    this.camera.getWorldDirection(this.tmpFwd);
    this.tmpRight.crossVectors(this.tmpFwd, this.tmpWorldUp).normalize();
    this.tmpUp.set(0, 1, 0);
    this.tmpMove.set(0, 0, 0);

    if (this.keys.has('KeyW') || this.keys.has('ArrowUp')) this.tmpMove.add(this.tmpFwd);
    if (this.keys.has('KeyS') || this.keys.has('ArrowDown')) this.tmpMove.sub(this.tmpFwd);
    if (this.keys.has('KeyD') || this.keys.has('ArrowRight')) this.tmpMove.add(this.tmpRight);
    if (this.keys.has('KeyA') || this.keys.has('ArrowLeft')) this.tmpMove.sub(this.tmpRight);
    if (this.keys.has('KeyE')) this.tmpMove.add(this.tmpUp);
    if (this.keys.has('KeyQ')) this.tmpMove.sub(this.tmpUp);

    if (this.tmpMove.lengthSq() > 0) {
      this.tmpMove.normalize().multiplyScalar(speed * dt);
      this.camera.position.add(this.tmpMove);
      // Prevent diving underground / below water
      this.camera.position.y = Math.max(this.camera.position.y, 4.0);
      this.camera.position.x = THREE.MathUtils.clamp(this.camera.position.x, -1750, 1850);
      this.camera.position.z = THREE.MathUtils.clamp(this.camera.position.z, -1050, 1050);
      this.speedIntensity = THREE.MathUtils.lerp(this.speedIntensity, boost > 1.5 ? 0.65 : 0.15, Math.min(dt * 5, 1));
    } else {
      this.speedIntensity = THREE.MathUtils.lerp(this.speedIntensity, 0, Math.min(dt * 6, 1));
    }

    // Track nearest station for HUD title card while free-flying!
    let bestIdx = 1;
    let bestDist = Infinity;
    for (const st of this.layout.stations) {
      const d = Math.hypot(this.camera.position.x - st.anchor.x, this.camera.position.z - st.anchor.z);
      if (d < bestDist) {
        bestDist = d;
        bestIdx = st.index;
      }
    }
    this.currentStationIndex = bestIdx;

    const targetFov = lookDev.drone.baseFov + this.speedIntensity * 16;
    this.smoothFov = THREE.MathUtils.lerp(this.smoothFov, targetFov, Math.min(dt * 5, 1));
    this.camera.fov = this.smoothFov;
    this.camera.updateProjectionMatrix();
  }

  private bindFreeFlyInput(): void {
    window.addEventListener('keydown', (e) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      this.keys.add(e.code);
    });
    window.addEventListener('keyup', (e) => {
      this.keys.delete(e.code);
    });
    this.domElement.addEventListener('pointerdown', (e) => {
      if (!this.freeFly) return;
      this.isDragging = true;
      this.lastPointerX = e.clientX;
      this.lastPointerY = e.clientY;
    });
    window.addEventListener('pointermove', (e) => {
      if (!this.freeFly || !this.isDragging) return;
      const dx = e.clientX - this.lastPointerX;
      const dy = e.clientY - this.lastPointerY;
      this.lastPointerX = e.clientX;
      this.lastPointerY = e.clientY;
      this.yaw -= dx * 0.0032;
      this.pitch = THREE.MathUtils.clamp(this.pitch - dy * 0.0032, -1.35, 1.35);
    });
    window.addEventListener('pointerup', () => {
      this.isDragging = false;
    });
  }
}
