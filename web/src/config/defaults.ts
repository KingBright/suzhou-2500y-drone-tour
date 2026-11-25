import type { AtmosphereMode, LookDevState } from '../types/world';

export interface AtmosphereKeyframe {
  sunColor: string;
  sunIntensity: number;
  sunElevation: number;
  sunAzimuth: number;
  hemiSkyColor: string;
  hemiGroundColor: string;
  hemiIntensity: number;
  fillColor: string;
  fillIntensity: number;
  fogColor: string;
  fogDensity: number;
  skyTopColor: string;
  skyMidColor: string;
  skyHorizonColor: string;
  skySunGlowColor: string;
  skyGlow: number;
  starIntensity: number;
  waterShallowColor: string;
  waterDeepColor: string;
  waterShimmer: number;
  emissiveScale: number;
  exposure: number;
  bloomStrength: number;
  bloomThreshold: number;
  nightFactor: number;
}

export const ATMOSPHERE_PRESETS: Record<Exclude<AtmosphereMode, 'auto'>, AtmosphereKeyframe> = {
  dawn: {
    sunColor: '#ffe1be',
    sunIntensity: 1.95,
    sunElevation: 16,
    sunAzimuth: 72,
    hemiSkyColor: '#bcd6ee',
    hemiGroundColor: '#56646b',
    hemiIntensity: 1.05,
    fillColor: '#9fc5e8',
    fillIntensity: 0.55,
    fogColor: '#cedce6',
    fogDensity: 0.00052,
    skyTopColor: '#486d99',
    skyMidColor: '#9eb8cf',
    skyHorizonColor: '#f2dfd0',
    skySunGlowColor: '#ffd6a8',
    skyGlow: 0.72,
    starIntensity: 0.0,
    waterShallowColor: '#2d5c66',
    waterDeepColor: '#16343f',
    waterShimmer: 0.85,
    emissiveScale: 0.20,
    exposure: 1.04,
    bloomStrength: 0.14,
    bloomThreshold: 0.94,
    nightFactor: 0.05
  },
  golden: {
    sunColor: '#ffba6e',
    sunIntensity: 2.85,
    sunElevation: 13.5,
    sunAzimuth: 248,
    hemiSkyColor: '#9cb8dc',
    hemiGroundColor: '#5c4637',
    hemiIntensity: 0.92,
    fillColor: '#6f96c8',
    fillIntensity: 0.58,
    fogColor: '#d9a882',
    fogDensity: 0.00044,
    skyTopColor: '#294878',
    skyMidColor: '#8d6e7b',
    skyHorizonColor: '#f5a96b',
    skySunGlowColor: '#ffd28e',
    skyGlow: 1.15,
    starIntensity: 0.02,
    waterShallowColor: '#254a54',
    waterDeepColor: '#122933',
    waterShimmer: 1.35,
    emissiveScale: 0.55,
    exposure: 1.04,
    bloomStrength: 0.18,
    bloomThreshold: 0.92,
    nightFactor: 0.20
  },
  dusk: {
    sunColor: '#ff8a6b',
    sunIntensity: 1.55,
    sunElevation: 6.5,
    sunAzimuth: 262,
    hemiSkyColor: '#7669a3',
    hemiGroundColor: '#352b3c',
    hemiIntensity: 0.76,
    fillColor: '#5579b8',
    fillIntensity: 0.55,
    fogColor: '#6d587c',
    fogDensity: 0.00046,
    skyTopColor: '#141c3d',
    skyMidColor: '#4c3866',
    skyHorizonColor: '#d6746e',
    skySunGlowColor: '#ff9c6e',
    skyGlow: 0.92,
    starIntensity: 0.28,
    waterShallowColor: '#1d3247',
    waterDeepColor: '#0c1829',
    waterShimmer: 1.15,
    emissiveScale: 0.95,
    exposure: 1.03,
    bloomStrength: 0.24,
    bloomThreshold: 0.88,
    nightFactor: 0.62
  },
  night: {
    sunColor: '#8eb8ff',
    sunIntensity: 0.92,
    sunElevation: 28,
    sunAzimuth: 215,
    hemiSkyColor: '#3c5a99',
    hemiGroundColor: '#1c2336',
    hemiIntensity: 0.68,
    fillColor: '#4b74b8',
    fillIntensity: 0.46,
    fogColor: '#14213b',
    fogDensity: 0.00038,
    skyTopColor: '#050a18',
    skyMidColor: '#0e1b38',
    skyHorizonColor: '#233b63',
    skySunGlowColor: '#6e9de6',
    skyGlow: 0.38,
    starIntensity: 0.95,
    waterShallowColor: '#0f2238',
    waterDeepColor: '#07111f',
    waterShimmer: 1.25,
    emissiveScale: 1.28,
    exposure: 1.02,
    bloomStrength: 0.28,
    bloomThreshold: 0.85,
    nightFactor: 1.0
  }
};

export const ACT_LABELS: Record<number, { zh: string; en: string }> = {
  1: { zh: '第一幕 · 运河古韵', en: 'Act I · Grand Canal & Tiger Hill' },
  2: { zh: '第二幕 · 姑苏园林', en: 'Act II · Classical Gusu Gardens' },
  3: { zh: '第三幕 · 穿越东方之门', en: 'Act III · Portal to Modernity' },
  4: { zh: '第四幕 · 璀璨金鸡湖', en: 'Act IV · Jinji Lake Skyline' }
};

export const ATMOSPHERE_LABELS: Record<AtmosphereMode, string> = {
  auto: '自动时空',
  dawn: '清晨水墨',
  golden: '金色夕阳',
  dusk: '粉紫暮色',
  night: '蓝调夜景'
};

export function createDefaultLookDevState(): LookDevState {
  const g = ATMOSPHERE_PRESETS.golden;
  return {
    lights: {
      sunColor: g.sunColor,
      sunIntensity: g.sunIntensity,
      sunElevation: g.sunElevation,
      sunAzimuth: g.sunAzimuth,
      shadowBias: -0.0005,
      hemiSkyColor: g.hemiSkyColor,
      hemiGroundColor: g.hemiGroundColor,
      hemiIntensity: g.hemiIntensity,
      fillColor: g.fillColor,
      fillIntensity: g.fillIntensity
    },
    emissives: {
      warm: 1.0,
      gold: 1.0,
      cyan: 1.0,
      accent: 1.0
    },
    materials: {
      waterColor: g.waterShallowColor,
      waterDeepColor: g.waterDeepColor,
      waterRoughness: 0.14,
      waveScale: 1.0,
      waveSpeed: 0.9,
      waterShimmer: 1.25
    },
    atmosphere: {
      mode: 'auto',
      timeOfDay: 0.12,
      fogDensity: g.fogDensity,
      fogColor: g.fogColor,
      skyTurbidity: 1.0,
      skyGlow: g.skyGlow
    },
    drone: {
      speedScale: 1.0,
      baseFov: 48,
      swoopFovBoost: 32,
      rollStrength: 1.0
    },
    postProcessing: {
      exposure: g.exposure,
      bloomEnabled: true,
      bloomThreshold: g.bloomThreshold,
      bloomStrength: g.bloomStrength,
      bloomRadius: 0.48,
      vignetteIntensity: 0.24
    }
  };
}
