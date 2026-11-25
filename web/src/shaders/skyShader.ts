import * as THREE from 'three';

export interface SkyDomeBundle {
  mesh: THREE.Mesh;
  material: THREE.ShaderMaterial;
  uniforms: {
    uTopColor: { value: THREE.Color };
    uMidColor: { value: THREE.Color };
    uHorizonColor: { value: THREE.Color };
    uSunGlowColor: { value: THREE.Color };
    uSunDir: { value: THREE.Vector3 };
    uSunGlow: { value: number };
    uStarIntensity: { value: number };
    uTurbidity: { value: number };
    uTime: { value: number };
  };
}

const SKY_VERTEX_SHADER = /* glsl */ `
  varying vec3 vWorldDir;

  void main() {
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vWorldDir = normalize(position);
    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`;

const SKY_FRAGMENT_SHADER = /* glsl */ `
  uniform vec3 uTopColor;
  uniform vec3 uMidColor;
  uniform vec3 uHorizonColor;
  uniform vec3 uSunGlowColor;
  uniform vec3 uSunDir;
  uniform float uSunGlow;
  uniform float uStarIntensity;
  uniform float uTurbidity;
  uniform float uTime;

  varying vec3 vWorldDir;

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(
      mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
      mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x),
      u.y
    );
  }

  float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    mat2 rot = mat2(0.8, 0.6, -0.6, 0.8);
    for (int i = 0; i < 4; i++) {
      v += a * noise(p);
      p = rot * p * 2.02;
      a *= 0.5;
    }
    return v;
  }

  void main() {
    vec3 dir = normalize(vWorldDir);
    float h = clamp(dir.y, 0.0, 1.0);

    // Three-band atmospheric gradient
    float lowMix = pow(1.0 - h, 2.2 * uTurbidity);
    float midMix = smoothstep(0.02, 0.42, h);
    vec3 col = mix(uMidColor, uTopColor, smoothstep(0.28, 0.88, h));
    col = mix(col, uHorizonColor, lowMix);
    col = mix(uHorizonColor, col, clamp(midMix + 0.12, 0.0, 1.0));

    // Directional solar / lunar scatter & disc
    vec3 sunD = normalize(uSunDir);
    float sunCos = max(dot(dir, sunD), 0.0);
    float mieHalo = pow(sunCos, 6.0) * 0.48 * uSunGlow;
    float sunCore = pow(sunCos, 180.0) * 1.45 * uSunGlow;
    float sunDisc = smoothstep(0.9988, 0.9997, sunCos) * 2.2 * uSunGlow;
    col += uSunGlowColor * (mieHalo + sunCore + sunDisc);

    // Horizon belt warmth near sun azimuth
    float horizonBelt = exp(-abs(dir.y) * 9.0) * (0.28 + 0.45 * pow(sunCos, 2.0)) * uSunGlow;
    col += uSunGlowColor * horizonBelt * 0.35;

    // Subtle painterly high-altitude cloud wisps
    if (dir.y > 0.02) {
      vec2 cloudUV = dir.xz / (dir.y + 0.24) * 1.15 + vec2(uTime * 0.008, -uTime * 0.004);
      float c = fbm(cloudUV);
      float cloudMask = smoothstep(0.50, 0.78, c) * smoothstep(0.02, 0.22, dir.y) * (1.0 - smoothstep(0.55, 0.95, dir.y));
      vec3 cloudColor = mix(uHorizonColor * 1.12, uSunGlowColor * 1.25, pow(sunCos, 3.0) * 0.65);
      col = mix(col, cloudColor, cloudMask * 0.36);
    }

    // Crisp pinpoint twilight/night stars above horizon (sub-cell radial distance avoids blocky squares!)
    if (uStarIntensity > 0.01 && dir.y > 0.08) {
      vec2 starCoord = dir.xz / (dir.y + 0.35) * 145.0;
      vec2 starCell = floor(starCoord);
      vec2 cellUv = fract(starCoord);
      float starRand = hash(starCell);
      if (starRand > 0.986) {
        vec2 starCenter = vec2(
          0.25 + 0.5 * hash(starCell + vec2(17.3, 4.1)),
          0.25 + 0.5 * hash(starCell + vec2(3.7, 29.9))
        );
        float dist = length(cellUv - starCenter);
        float pinpoint = smoothstep(0.22, 0.0, dist);
        pinpoint *= pinpoint;
        float twinkle = 0.68 + 0.32 * sin(uTime * 2.6 + starRand * 62.8);
        float starFade = smoothstep(0.08, 0.32, dir.y);
        col += vec3(0.88, 0.93, 1.0) * pinpoint * twinkle * starFade * uStarIntensity * 1.45;
      }
    }

    // Smooth ground-reflection darkening below horizon
    if (dir.y < 0.0) {
      col = mix(uHorizonColor * 0.55, uTopColor * 0.22, clamp(-dir.y * 4.0, 0.0, 1.0));
    }

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function createSkyDome(): SkyDomeBundle {
  const uniforms = {
    uTopColor: { value: new THREE.Color('#294878') },
    uMidColor: { value: new THREE.Color('#8d6e7b') },
    uHorizonColor: { value: new THREE.Color('#f5a96b') },
    uSunGlowColor: { value: new THREE.Color('#ffd28e') },
    uSunDir: { value: new THREE.Vector3(-0.85, 0.24, -0.42).normalize() },
    uSunGlow: { value: 1.1 },
    uStarIntensity: { value: 0.02 },
    uTurbidity: { value: 1.0 },
    uTime: { value: 0 }
  };

  const geometry = new THREE.SphereGeometry(5200, 32, 20);
  const material = new THREE.ShaderMaterial({
    vertexShader: SKY_VERTEX_SHADER,
    fragmentShader: SKY_FRAGMENT_SHADER,
    uniforms,
    side: THREE.BackSide,
    depthWrite: false,
    fog: false
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = 'ProceduralSkyDome';
  mesh.frustumCulled = false;
  mesh.renderOrder = -100;

  return { mesh, material, uniforms };
}
