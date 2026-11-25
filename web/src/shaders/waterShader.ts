import * as THREE from 'three';

export interface WaterUniforms {
  [uniform: string]: THREE.IUniform;
  uTime: { value: number };
  uShallowColor: { value: THREE.Color };
  uDeepColor: { value: THREE.Color };
  uSkyTopColor: { value: THREE.Color };
  uSkyHorizonColor: { value: THREE.Color };
  uSunDir: { value: THREE.Vector3 };
  uSunColor: { value: THREE.Color };
  uFogColor: { value: THREE.Color };
  uFogDensity: { value: number };
  uWaveScale: { value: number };
  uWaveSpeed: { value: number };
  uRoughness: { value: number };
  uShimmer: { value: number };
  uNightFactor: { value: number };
}

const WATER_VERTEX_SHADER = /* glsl */ `
  attribute float aShore;

  uniform float uTime;
  uniform float uWaveScale;
  uniform float uWaveSpeed;

  varying vec3 vWorldPos;
  varying float vShore;

  void main() {
    vShore = aShore;
    vec3 pos = position;
    vec4 worldPos = modelMatrix * vec4(pos, 1.0);

    // Subtle vertical swell on open Jinji Lake (away from narrow canal banks)
    float openWater = clamp(1.0 - aShore, 0.0, 1.0);
    float t = uTime * uWaveSpeed;
    float swell = (
      sin(worldPos.x * 0.045 * uWaveScale + t * 1.15) * 0.07 +
      cos(worldPos.z * 0.055 * uWaveScale - t * 0.92) * 0.06
    ) * openWater;
    worldPos.y += swell;

    vWorldPos = worldPos.xyz;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`;

const WATER_FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec3 uShallowColor;
  uniform vec3 uDeepColor;
  uniform vec3 uSkyTopColor;
  uniform vec3 uSkyHorizonColor;
  uniform vec3 uSunDir;
  uniform vec3 uSunColor;
  uniform vec3 uFogColor;
  uniform float uFogDensity;
  uniform float uWaveScale;
  uniform float uWaveSpeed;
  uniform float uRoughness;
  uniform float uShimmer;
  uniform float uNightFactor;

  varying vec3 vWorldPos;
  varying float vShore;

  // Lightweight procedural multi-directional wave height for crisp analytical normal
  float waveHeight(vec2 p, float t) {
    float h = 0.0;
    h += sin(p.x * 0.21 + p.y * 0.14 + t * 1.35) * 0.34;
    h += sin(p.x * -0.17 + p.y * 0.28 + t * 1.10) * 0.28;
    h += sin(p.x * 0.48 - p.y * 0.36 + t * 2.15) * 0.18;
    h += cos(p.x * 0.92 + p.y * 0.85 - t * 2.75) * 0.10;
    h += sin(p.x * 1.85 - p.y * 1.42 + t * 3.40) * 0.05;
    return h;
  }

  void main() {
    float t = uTime * uWaveSpeed;
    vec2 p = vWorldPos.xz * uWaveScale;

    // Finite-difference normal from multi-octave flowing ripples
    float eps = 0.18;
    float hC = waveHeight(p, t);
    float hX = waveHeight(p + vec2(eps, 0.0), t);
    float hZ = waveHeight(p + vec2(0.0, eps), t);

    float normalStrength = mix(0.20, 0.52, clamp(uRoughness * 1.8, 0.0, 1.0));
    vec3 N = normalize(vec3((hC - hX) * normalStrength, 1.0, (hC - hZ) * normalStrength));

    vec3 V = normalize(cameraPosition - vWorldPos);
    float NdotV = max(dot(N, V), 0.001);

    // Schlick Fresnel reflection
    float fresnel = pow(1.0 - NdotV, 4.2);
    fresnel = clamp(0.06 + fresnel * 0.88, 0.0, 0.96);

    // Water depth tint (shallower near shorelines, deeper in Jinji Lake center)
    vec3 baseWater = mix(uDeepColor, uShallowColor, clamp(vShore * 0.85 + 0.15, 0.0, 1.0));

    // Sky reflection using reflected vector
    vec3 R = reflect(-V, N);
    float reflElev = clamp(R.y, 0.0, 1.0);
    vec3 skyRefl = mix(uSkyHorizonColor, uSkyTopColor, pow(reflElev, 0.55));

    // Night/Dusk warm Jinji Lake & Gusu skyline glow shimmer reflected on water
    float jinjiMask = smoothstep(520.0, 880.0, vWorldPos.x);
    float gusuMask = smoothstep(450.0, -50.0, vWorldPos.x);
    float rippleGlow = smoothstep(0.12, 0.72, abs(N.x * 3.2 + N.z * 2.4));

    vec3 cbdWaterBounce = mix(vec3(1.0, 0.72, 0.34), vec3(0.24, 0.82, 1.0), 0.45 + 0.45 * sin(vWorldPos.z * 0.015 + vWorldPos.x * 0.01));
    vec3 gusuWaterBounce = vec3(1.0, 0.58, 0.24);
    vec3 cityReflection = (jinjiMask * cbdWaterBounce * 0.52 + gusuMask * gusuWaterBounce * 0.34) * uNightFactor * (0.35 + 0.65 * rippleGlow);

    vec3 color = mix(baseWater, skyRefl + cityReflection, fresnel);
    color += cityReflection * 0.28;

    // Sun / Moon specular glints
    vec3 L = normalize(uSunDir);
    vec3 H = normalize(L + V);
    float specPow = mix(360.0, 48.0, clamp(uRoughness, 0.02, 1.0));
    float specCore = pow(max(dot(N, H), 0.0), specPow);
    float specBroad = pow(max(dot(N, H), 0.0), specPow * 0.14);
    color += uSunColor * (specCore * 2.4 + specBroad * 0.42) * uShimmer;

    // Subtle animated shoreline foam where water meets stone embankments
    float foamWave = sin(vWorldPos.x * 0.35 + vWorldPos.z * 0.35 - t * 2.4) * 0.5 + 0.5;
    float shoreFoam = smoothstep(0.68, 0.98, vShore) * (0.45 + 0.55 * foamWave);
    vec3 foamColor = mix(uSkyHorizonColor * 0.92, vec3(0.88, 0.94, 0.98), 0.55);
    color = mix(color, foamColor, shoreFoam * 0.38);

    // Match scene FogExp2 cleanly
    float dist = length(cameraPosition - vWorldPos);
    float fogFactor = 1.0 - exp(-pow(dist * uFogDensity, 2.0));
    color = mix(color, uFogColor, clamp(fogFactor, 0.0, 1.0));

    gl_FragColor = vec4(color, 1.0);
  }
`;

export function createWaterMaterial(): { material: THREE.ShaderMaterial; uniforms: WaterUniforms } {
  const uniforms: WaterUniforms = {
    uTime: { value: 0 },
    uShallowColor: { value: new THREE.Color('#254a54') },
    uDeepColor: { value: new THREE.Color('#122933') },
    uSkyTopColor: { value: new THREE.Color('#294878') },
    uSkyHorizonColor: { value: new THREE.Color('#f5a96b') },
    uSunDir: { value: new THREE.Vector3(-0.85, 0.24, -0.42).normalize() },
    uSunColor: { value: new THREE.Color('#ffba6e') },
    uFogColor: { value: new THREE.Color('#d9a882') },
    uFogDensity: { value: 0.00044 },
    uWaveScale: { value: 1.0 },
    uWaveSpeed: { value: 0.9 },
    uRoughness: { value: 0.14 },
    uShimmer: { value: 1.25 },
    uNightFactor: { value: 0.22 }
  };

  const material = new THREE.ShaderMaterial({
    vertexShader: WATER_VERTEX_SHADER,
    fragmentShader: WATER_FRAGMENT_SHADER,
    uniforms,
    transparent: false,
    depthWrite: true
  });

  return { material, uniforms };
}
