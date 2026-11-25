import * as THREE from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import type { AtmosphereMode, LookDevState } from '../types/world';
import { ATMOSPHERE_PRESETS, type AtmosphereKeyframe } from '../config/defaults';
import { createSkyDome, type SkyDomeBundle } from '../shaders/skyShader';
import type { WaterUniforms } from '../shaders/waterShader';

export type EmissiveChannel = 'warm' | 'gold' | 'cyan' | 'accent';

interface TrackedEmissive {
  material: THREE.MeshStandardMaterial;
  channel: EmissiveChannel;
  baseIntensity: number;
}

export class AtmosphereManager {
  public readonly sunLight: THREE.DirectionalLight;
  public readonly hemiLight: THREE.HemisphereLight;
  public readonly fillLight: THREE.DirectionalLight;
  public readonly sky: SkyDomeBundle;
  public readonly fog: THREE.FogExp2;

  private readonly scene: THREE.Scene;
  private readonly renderer: THREE.WebGLRenderer;
  private readonly waterUniforms: WaterUniforms;
  private readonly emissives: TrackedEmissive[] = [];

  private currentKf: AtmosphereKeyframe;
  private transitionFromKf: AtmosphereKeyframe;
  private transitionTargetKf: AtmosphereKeyframe;
  private transitionElapsed = 1.5;
  private readonly transitionDuration = 1.5;
  private mode: AtmosphereMode = 'auto';
  private manualTimeOfDay = 0.12;
  private userLightOverride = false;
  private userFogOverride = false;
  private userWaterOverride = false;

  // Reusable math scratch objects (zero per-frame GC)
  private readonly tmpSunDir = new THREE.Vector3();
  private readonly tmpColorA = new THREE.Color();
  private readonly tmpColorB = new THREE.Color();
  private readonly tmpTargetPos = new THREE.Vector3();

  public currentEmissiveGlobal = 0.75;
  public currentNightFactor = 0.22;

  constructor(
    scene: THREE.Scene,
    renderer: THREE.WebGLRenderer,
    waterUniforms: WaterUniforms
  ) {
    this.scene = scene;
    this.renderer = renderer;
    this.waterUniforms = waterUniforms;

    // Lightweight procedural PMREM environment for crisp glass & metal reflections
    const pmrem = new THREE.PMREMGenerator(renderer);
    const envRT = pmrem.fromScene(new RoomEnvironment(), 0.04);
    scene.environment = envRT.texture;
    scene.environmentIntensity = 0.55;
    pmrem.dispose();

    // Exponential atmospheric fog
    this.fog = new THREE.FogExp2(ATMOSPHERE_PRESETS.golden.fogColor, ATMOSPHERE_PRESETS.golden.fogDensity);
    scene.fog = this.fog;

    // Sky Dome
    this.sky = createSkyDome();
    scene.add(this.sky.mesh);

    // HARD RULE: Strictly 3 Real-Time Lights total (ZERO PointLights / SpotLights!)
    // Light #1: Primary Sun / Moon DirectionalLight with shadow frustum tracking the drone
    this.sunLight = new THREE.DirectionalLight('#ffba6e', 2.85);
    this.sunLight.name = 'PrimarySunLight';
    this.sunLight.castShadow = true;
    this.sunLight.shadow.mapSize.set(2048, 2048);
    this.sunLight.shadow.camera.near = 20;
    this.sunLight.shadow.camera.far = 1400;
    const shadowHalf = 280;
    this.sunLight.shadow.camera.left = -shadowHalf;
    this.sunLight.shadow.camera.right = shadowHalf;
    this.sunLight.shadow.camera.top = shadowHalf;
    this.sunLight.shadow.camera.bottom = -shadowHalf;
    this.sunLight.shadow.bias = -0.0005;
    this.sunLight.shadow.normalBias = 0.06;
    scene.add(this.sunLight);
    scene.add(this.sunLight.target);

    // Light #2: Hemisphere Sky/Ground Bounce Light
    this.hemiLight = new THREE.HemisphereLight('#9cb8dc', '#5c4637', 0.92);
    this.hemiLight.name = 'SkyHemisphereLight';
    scene.add(this.hemiLight);

    // Light #3: Subtle Cool Back/Rim Fill DirectionalLight (no shadow)
    this.fillLight = new THREE.DirectionalLight('#6f96c8', 0.58);
    this.fillLight.name = 'RimFillLight';
    this.fillLight.castShadow = false;
    this.fillLight.position.set(400, 260, 350);
    scene.add(this.fillLight);

    this.currentKf = { ...ATMOSPHERE_PRESETS.golden };
    this.transitionFromKf = { ...ATMOSPHERE_PRESETS.golden };
    this.transitionTargetKf = { ...ATMOSPHERE_PRESETS.golden };
  }

  public getActiveLightCount(): number {
    let count = 0;
    this.scene.traverse((obj) => {
      if ((obj as THREE.Light).isLight && obj.visible) count++;
    });
    return count;
  }

  /** Scan an object hierarchy and register all tagged Emissive_* PBR materials */
  public registerEmissivesFromObject(root: THREE.Object3D): void {
    const seen = new Set<THREE.Material>();
    root.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (!mesh.isMesh || !mesh.material) return;
      const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      for (const m of mats) {
        if (seen.has(m)) continue;
        seen.add(m);
        if (!(m as THREE.MeshStandardMaterial).isMeshStandardMaterial) continue;
        const std = m as THREE.MeshStandardMaterial;
        const name = (std.name || '').toLowerCase();

        let channel: EmissiveChannel | null = null;
        if (name.includes('emissive_warm') || name.includes('lantern') || name.includes('eave_light')) {
          channel = 'warm';
        } else if (name.includes('emissive_gold') || name.includes('gold_light') || name.includes('crown_light')) {
          channel = 'gold';
        } else if (name.includes('emissive_cyan') || name.includes('cyan_light') || name.includes('led_blue')) {
          channel = 'cyan';
        } else if (name.includes('emissive_accent') || name.includes('neon') || name.includes('magenta')) {
          channel = 'accent';
        } else if (std.emissive && (std.emissive.r + std.emissive.g + std.emissive.b) > 0.15 && std.emissiveIntensity > 0.05) {
          // Fallback classification by emissive hue
          if (std.emissive.b > std.emissive.r * 1.15) channel = 'cyan';
          else if (std.emissive.r > 0.7 && std.emissive.b > 0.45) channel = 'accent';
          else if (std.emissive.g > 0.72) channel = 'gold';
          else channel = 'warm';
        }

        if (channel) {
          // Ensure non-black emissive color and tone-mapped crisp highlights
          if (std.emissive.r + std.emissive.g + std.emissive.b < 0.05) {
            if (channel === 'warm') std.emissive.set('#ffba66');
            else if (channel === 'gold') std.emissive.set('#ffd98a');
            else if (channel === 'cyan') std.emissive.set('#4de2ff');
            else std.emissive.set('#ff5cc8');
          }
          std.toneMapped = true;
          // Clamp exported Blender emissive strength (often 3..6) so Selective Bloom never washes out to white!
          const baseIntensity = Math.min(Math.max(std.emissiveIntensity || 1.0, 0.45), 1.25);
          this.emissives.push({ material: std, channel, baseIntensity });
        }
      }
    });
  }

  public setMode(mode: AtmosphereMode, instant = false): void {
    this.mode = mode;
    this.userLightOverride = false;
    this.userFogOverride = false;
    this.userWaterOverride = false;

    if (mode !== 'auto') {
      this.transitionFromKf = { ...this.currentKf };
      this.transitionTargetKf = { ...ATMOSPHERE_PRESETS[mode] };
      if (mode === 'dawn') this.manualTimeOfDay = 0.0;
      else if (mode === 'golden') this.manualTimeOfDay = 0.30;
      else if (mode === 'dusk') this.manualTimeOfDay = 0.65;
      else if (mode === 'night') this.manualTimeOfDay = 1.0;

      if (instant) {
        this.transitionElapsed = this.transitionDuration;
        Object.assign(this.currentKf, this.transitionTargetKf);
      } else {
        this.transitionElapsed = 0;
      }
    } else if (instant) {
      this.transitionElapsed = this.transitionDuration;
    }
  }

  public setTimeOfDay(t: number, lookDev: LookDevState): void {
    this.manualTimeOfDay = THREE.MathUtils.clamp(t, 0, 1);
    this.userLightOverride = false;
    this.userFogOverride = false;
    this.userWaterOverride = false;
    lookDev.atmosphere.timeOfDay = this.manualTimeOfDay;
    // Direct scrub computes the exact keyframe immediately and locks target to match
    this.sampleTimelineKeyframe(this.manualTimeOfDay, this.currentKf);
    Object.assign(this.transitionTargetKf, this.currentKf);
    this.transitionElapsed = this.transitionDuration;
  }

  public markUserOverride(group: 'lights' | 'fog' | 'water'): void {
    if (group === 'lights') this.userLightOverride = true;
    if (group === 'fog') this.userFogOverride = true;
    if (group === 'water') this.userWaterOverride = true;
  }

  public clearOverrides(): void {
    this.userLightOverride = false;
    this.userFogOverride = false;
    this.userWaterOverride = false;
  }

  private lerpHex(a: string, b: string, t: number): string {
    this.tmpColorA.set(a);
    this.tmpColorB.set(b);
    this.tmpColorA.lerp(this.tmpColorB, t);
    return '#' + this.tmpColorA.getHexString();
  }

  private lerpKeyframe(a: AtmosphereKeyframe, b: AtmosphereKeyframe, t: number, out: AtmosphereKeyframe): void {
    const k = THREE.MathUtils.clamp(t, 0, 1);
    out.sunColor = this.lerpHex(a.sunColor, b.sunColor, k);
    out.sunIntensity = THREE.MathUtils.lerp(a.sunIntensity, b.sunIntensity, k);
    out.sunElevation = THREE.MathUtils.lerp(a.sunElevation, b.sunElevation, k);
    out.sunAzimuth = THREE.MathUtils.lerp(a.sunAzimuth, b.sunAzimuth, k);
    out.hemiSkyColor = this.lerpHex(a.hemiSkyColor, b.hemiSkyColor, k);
    out.hemiGroundColor = this.lerpHex(a.hemiGroundColor, b.hemiGroundColor, k);
    out.hemiIntensity = THREE.MathUtils.lerp(a.hemiIntensity, b.hemiIntensity, k);
    out.fillColor = this.lerpHex(a.fillColor, b.fillColor, k);
    out.fillIntensity = THREE.MathUtils.lerp(a.fillIntensity, b.fillIntensity, k);
    out.fogColor = this.lerpHex(a.fogColor, b.fogColor, k);
    out.fogDensity = THREE.MathUtils.lerp(a.fogDensity, b.fogDensity, k);
    out.skyTopColor = this.lerpHex(a.skyTopColor, b.skyTopColor, k);
    out.skyMidColor = this.lerpHex(a.skyMidColor, b.skyMidColor, k);
    out.skyHorizonColor = this.lerpHex(a.skyHorizonColor, b.skyHorizonColor, k);
    out.skySunGlowColor = this.lerpHex(a.skySunGlowColor, b.skySunGlowColor, k);
    out.skyGlow = THREE.MathUtils.lerp(a.skyGlow, b.skyGlow, k);
    out.starIntensity = THREE.MathUtils.lerp(a.starIntensity, b.starIntensity, k);
    out.waterShallowColor = this.lerpHex(a.waterShallowColor, b.waterShallowColor, k);
    out.waterDeepColor = this.lerpHex(a.waterDeepColor, b.waterDeepColor, k);
    out.waterShimmer = THREE.MathUtils.lerp(a.waterShimmer, b.waterShimmer, k);
    out.emissiveScale = THREE.MathUtils.lerp(a.emissiveScale, b.emissiveScale, k);
    out.exposure = THREE.MathUtils.lerp(a.exposure, b.exposure, k);
    out.bloomStrength = THREE.MathUtils.lerp(a.bloomStrength, b.bloomStrength, k);
    out.bloomThreshold = THREE.MathUtils.lerp(a.bloomThreshold, b.bloomThreshold, k);
    out.nightFactor = THREE.MathUtils.lerp(a.nightFactor, b.nightFactor, k);
  }

  /**
   * Maps continuous time t in [0..1]:
   * 0.00 = Dawn, 0.28 = Golden Hour (West Suzhou), 0.62 = Dusk (Core Gusu), 0.90..1.00 = Blue Hour Night (Jinji Lake)
   */
  private sampleTimelineKeyframe(t: number, out: AtmosphereKeyframe): void {
    const c = THREE.MathUtils.clamp(t, 0, 1);
    if (c < 0.25) {
      this.lerpKeyframe(ATMOSPHERE_PRESETS.dawn, ATMOSPHERE_PRESETS.golden, c / 0.25, out);
    } else if (c < 0.64) {
      this.lerpKeyframe(ATMOSPHERE_PRESETS.golden, ATMOSPHERE_PRESETS.dusk, (c - 0.25) / 0.39, out);
    } else {
      this.lerpKeyframe(ATMOSPHERE_PRESETS.dusk, ATMOSPHERE_PRESETS.night, Math.min((c - 0.64) / 0.28, 1.0), out);
    }
  }

  /**
   * Piecewise Auto flight lighting timeline:
   * - progress 0.00..0.30 (Act I & SW West): Golden Hour (mappedT 0.24..0.40)
   * - progress 0.30..0.52 (Act II Gusu Gardens): Pink/Violet Dusk (mappedT 0.40..0.68)
   * - progress 0.52..0.72 (Act III Gate of Orient ~0.59 -> Blue Hour 0.85, reaching Night 1.0 at 0.72)
   * - progress 0.72..1.00 (Act IV Jinji Lake Ligongdi/MoCA/Eye/Arts/IFS): Rich Sapphire Night (1.0)
   */
  private sampleAutoFlightKeyframe(flightProgress: number, out: AtmosphereKeyframe): number {
    const p = THREE.MathUtils.clamp(flightProgress, 0, 1);
    let mappedT: number;
    if (p < 0.30) {
      mappedT = THREE.MathUtils.lerp(0.24, 0.40, p / 0.30);
    } else if (p < 0.52) {
      mappedT = THREE.MathUtils.lerp(0.40, 0.68, (p - 0.30) / 0.22);
    } else if (p < 0.72) {
      mappedT = THREE.MathUtils.lerp(0.68, 1.0, (p - 0.52) / 0.20);
    } else {
      mappedT = 1.0;
    }
    this.sampleTimelineKeyframe(mappedT, out);
    return mappedT;
  }

  public update(
    dt: number,
    elapsed: number,
    flightProgress: number,
    cameraPos: THREE.Vector3,
    lookDev: LookDevState,
    bloomPass?: { strength: number; threshold: number; radius: number; enabled: boolean }
  ): void {
    if (this.mode === 'auto') {
      lookDev.atmosphere.timeOfDay = this.sampleAutoFlightKeyframe(flightProgress, this.currentKf);
    } else if (this.transitionElapsed < this.transitionDuration) {
      this.transitionElapsed = Math.min(this.transitionElapsed + dt, this.transitionDuration);
      const u = this.transitionElapsed / this.transitionDuration;
      const ease = u * u * (3 - 2 * u);
      this.lerpKeyframe(this.transitionFromKf, this.transitionTargetKf, ease, this.currentKf);
      lookDev.atmosphere.timeOfDay = this.manualTimeOfDay;
    } else {
      Object.assign(this.currentKf, this.transitionTargetKf);
      lookDev.atmosphere.timeOfDay = this.manualTimeOfDay;
    }

    const kf = this.currentKf;

    // Sync auto values back into LookDev state unless manually tweaked
    if (!this.userLightOverride) {
      lookDev.lights.sunColor = kf.sunColor;
      lookDev.lights.sunIntensity = kf.sunIntensity;
      lookDev.lights.sunElevation = kf.sunElevation;
      lookDev.lights.sunAzimuth = kf.sunAzimuth;
      lookDev.lights.hemiSkyColor = kf.hemiSkyColor;
      lookDev.lights.hemiGroundColor = kf.hemiGroundColor;
      lookDev.lights.hemiIntensity = kf.hemiIntensity;
      lookDev.lights.fillColor = kf.fillColor;
      lookDev.lights.fillIntensity = kf.fillIntensity;
    }
    if (!this.userFogOverride) {
      lookDev.atmosphere.fogColor = kf.fogColor;
      lookDev.atmosphere.fogDensity = kf.fogDensity;
      lookDev.atmosphere.skyGlow = kf.skyGlow;
      lookDev.postProcessing.exposure = kf.exposure;
      lookDev.postProcessing.bloomStrength = kf.bloomStrength;
      lookDev.postProcessing.bloomThreshold = kf.bloomThreshold;
    }
    if (!this.userWaterOverride) {
      lookDev.materials.waterColor = kf.waterShallowColor;
      lookDev.materials.waterDeepColor = kf.waterDeepColor;
      lookDev.materials.waterShimmer = kf.waterShimmer;
    }

    // Compute Sun Direction from Elevation & Azimuth
    const elevRad = THREE.MathUtils.degToRad(lookDev.lights.sunElevation);
    const azimRad = THREE.MathUtils.degToRad(lookDev.lights.sunAzimuth);
    this.tmpSunDir.set(
      Math.cos(elevRad) * Math.sin(azimRad),
      Math.sin(elevRad),
      Math.cos(elevRad) * Math.cos(azimRad)
    ).normalize();

    // Update Lights (strictly 3 lights!)
    this.sunLight.color.set(lookDev.lights.sunColor);
    this.sunLight.intensity = lookDev.lights.sunIntensity;
    this.sunLight.shadow.bias = lookDev.lights.shadowBias;

    // Keep shadow frustum anchored near the camera horizontally (snapped to 4m grid to eliminate shadow shimmer)
    const snapX = Math.round(cameraPos.x / 4) * 4;
    const snapZ = Math.round(cameraPos.z / 4) * 4;
    this.tmpTargetPos.set(snapX, 0, snapZ);
    this.sunLight.target.position.copy(this.tmpTargetPos);
    this.sunLight.position.copy(this.tmpTargetPos).addScaledVector(this.tmpSunDir, 760);

    this.hemiLight.color.set(lookDev.lights.hemiSkyColor);
    this.hemiLight.groundColor.set(lookDev.lights.hemiGroundColor);
    this.hemiLight.intensity = lookDev.lights.hemiIntensity;

    this.fillLight.color.set(lookDev.lights.fillColor);
    this.fillLight.intensity = lookDev.lights.fillIntensity;
    this.fillLight.position.set(-this.tmpSunDir.x * 500, 260, -this.tmpSunDir.z * 500);

    // Update Fog & Environment Intensity
    this.fog.color.set(lookDev.atmosphere.fogColor);
    this.fog.density = lookDev.atmosphere.fogDensity;
    this.scene.environmentIntensity = THREE.MathUtils.lerp(0.68, 0.34, kf.nightFactor);

    // Update Sky Dome Shader
    this.sky.mesh.position.copy(cameraPos);
    this.sky.uniforms.uTopColor.value.set(kf.skyTopColor);
    this.sky.uniforms.uMidColor.value.set(kf.skyMidColor);
    this.sky.uniforms.uHorizonColor.value.set(kf.skyHorizonColor);
    this.sky.uniforms.uSunGlowColor.value.set(kf.skySunGlowColor);
    this.sky.uniforms.uSunDir.value.copy(this.tmpSunDir);
    this.sky.uniforms.uSunGlow.value = lookDev.atmosphere.skyGlow;
    this.sky.uniforms.uStarIntensity.value = kf.starIntensity;
    this.sky.uniforms.uTurbidity.value = lookDev.atmosphere.skyTurbidity;
    this.sky.uniforms.uTime.value = elapsed;

    // Update Water Shader Uniforms
    this.waterUniforms.uTime.value = elapsed;
    this.waterUniforms.uShallowColor.value.set(lookDev.materials.waterColor);
    this.waterUniforms.uDeepColor.value.set(lookDev.materials.waterDeepColor);
    this.waterUniforms.uSkyTopColor.value.set(kf.skyTopColor);
    this.waterUniforms.uSkyHorizonColor.value.set(kf.skyHorizonColor);
    this.waterUniforms.uSunDir.value.copy(this.tmpSunDir);
    this.waterUniforms.uSunColor.value.set(lookDev.lights.sunColor);
    this.waterUniforms.uFogColor.value.set(lookDev.atmosphere.fogColor);
    this.waterUniforms.uFogDensity.value = lookDev.atmosphere.fogDensity;
    this.waterUniforms.uWaveScale.value = lookDev.materials.waveScale;
    this.waterUniforms.uWaveSpeed.value = lookDev.materials.waveSpeed;
    this.waterUniforms.uRoughness.value = lookDev.materials.waterRoughness;
    this.waterUniforms.uShimmer.value = lookDev.materials.waterShimmer;
    this.waterUniforms.uNightFactor.value = kf.nightFactor;

    // Update ToneMapping & Bloom
    this.renderer.toneMappingExposure = lookDev.postProcessing.exposure;
    if (bloomPass) {
      bloomPass.enabled = lookDev.postProcessing.bloomEnabled;
      bloomPass.threshold = lookDev.postProcessing.bloomThreshold;
      bloomPass.strength = lookDev.postProcessing.bloomStrength;
      bloomPass.radius = lookDev.postProcessing.bloomRadius;
    }

    // Update All Registered Emissive Building Materials dynamically!
    // Gate modern neon (cyan/gold/accent) off during dawn & golden hour so distant skyscrapers don't glow white in daylight!
    this.currentEmissiveGlobal = kf.emissiveScale;
    this.currentNightFactor = kf.nightFactor;
    const modernNightGate = THREE.MathUtils.smoothstep(kf.nightFactor, 0.28, 0.72);
    const warmLanternGate = THREE.MathUtils.lerp(0.22, 1.0, THREE.MathUtils.smoothstep(kf.nightFactor, 0.14, 0.62));

    for (let i = 0; i < this.emissives.length; i++) {
      const e = this.emissives[i];
      const channelMul = lookDev.emissives[e.channel];
      const gate = e.channel === 'warm' ? warmLanternGate : modernNightGate;
      e.material.emissiveIntensity = e.baseIntensity * kf.emissiveScale * channelMul * gate;
    }
  }
}
