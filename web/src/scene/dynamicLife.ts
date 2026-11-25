import * as THREE from 'three';

export interface DynamicLifeSystem {
  group: THREE.Group;
  update: (elapsed: number, nightFactor: number, emissiveScale: number) => void;
}

/**
 * Environmental cinema life (total: 4 Draw Calls):
 * 1. Jinji Lake Music Fountain (GPU-animated glowing parabolic water jets at x=792, z=0)
 * 2. Ganjiang Road & CBD glowing traffic light-trail streams (custom shader ribbons)
 * 3. Floating warm lantern / firefly shimmer along Gusu canals & Jinji Lake promenade
 * 4. High-altitude soft drifting mist / cloud wisps
 */
export function createDynamicLifeSystem(): DynamicLifeSystem {
  const group = new THREE.Group();
  group.name = 'SuzhouDynamicLife';

  // --- 1. JINJI LAKE MUSIC FOUNTAIN (x=792, z=0, directly east of Gate of the Orient arch!) ---
  const fountainCount = 1800;
  const fPositions = new Float32Array(fountainCount * 3);
  const fSeeds = new Float32Array(fountainCount * 4); // x: jetIndex, y: phase, z: maxHeight, w: spread

  for (let i = 0; i < fountainCount; i++) {
    const jetIdx = i % 24;
    const isCenter = jetIdx >= 10 && jetIdx <= 13;
    const zBase = (jetIdx - 11.5) * 8.2;
    const xBase = 795 + Math.cos((jetIdx - 11.5) * 0.25) * 14;
    fPositions[i * 3] = xBase;
    fPositions[i * 3 + 1] = 0.2;
    fPositions[i * 3 + 2] = zBase;

    fSeeds[i * 4] = jetIdx / 24.0;
    fSeeds[i * 4 + 1] = (i * 0.6180339887) % 1.0;
    fSeeds[i * 4 + 2] = isCenter ? 54.0 : 22.0 + Math.cos((jetIdx - 11.5) * 0.24) * 20.0;
    fSeeds[i * 4 + 3] = ((i * 17) % 100) / 100.0 - 0.5;
  }

  const fountainGeo = new THREE.BufferGeometry();
  fountainGeo.setAttribute('position', new THREE.BufferAttribute(fPositions, 3));
  fountainGeo.setAttribute('aSeed', new THREE.BufferAttribute(fSeeds, 4));

  const fountainUniforms = {
    uTime: { value: 0 },
    uNightFactor: { value: 0.4 }
  };

  const fountainMat = new THREE.ShaderMaterial({
    uniforms: fountainUniforms,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    vertexShader: /* glsl */ `
      attribute vec4 aSeed;
      uniform float uTime;
      varying float vLife;
      varying float vJet;

      void main() {
        float jetNorm = aSeed.x;
        float phase = fract(aSeed.y + uTime * 0.42);
        // Choreographed wave amplitude across the 24 jets
        float wave = 0.58 + 0.42 * sin(uTime * 1.45 + jetNorm * 12.56);
        float maxH = aSeed.z * wave;

        // Parabolic water trajectory y = 4 * H * t * (1 - t)
        float y = 4.0 * maxH * phase * (1.0 - phase);
        float spread = phase * (2.5 + maxH * 0.14);

        vec3 pos = position;
        pos.y += y;
        pos.x += aSeed.w * spread * 2.2;
        pos.z += sin(aSeed.y * 28.0) * spread * 0.9;

        vLife = phase;
        vJet = jetNorm;

        vec4 mvPos = modelViewMatrix * vec4(pos, 1.0);
        gl_Position = projectionMatrix * mvPos;
        gl_PointSize = clamp((380.0 / -mvPos.z) * (0.65 + 0.7 * (1.0 - phase)), 2.0, 14.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform float uTime;
      uniform float uNightFactor;
      varying float vLife;
      varying float vJet;

      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        float soft = smoothstep(0.5, 0.06, d);

        // Shift between electric cyan, warm gold, and magenta accents
        vec3 colCyan = vec3(0.32, 0.88, 1.0);
        vec3 colGold = vec3(1.0, 0.80, 0.42);
        vec3 colPink = vec3(1.0, 0.38, 0.78);
        float hueWave = sin(vJet * 6.283 + uTime * 0.65) * 0.5 + 0.5;
        vec3 col = mix(colCyan, colGold, hueWave);
        col = mix(col, colPink, smoothstep(0.75, 1.0, sin(vLife * 3.14159 + uTime) * 0.5 + 0.5) * 0.45);
        col = mix(vec3(0.85, 0.95, 1.0), col, 0.35 + 0.65 * uNightFactor);

        float alpha = soft * sin(vLife * 3.14159) * (0.48 + 0.42 * uNightFactor);
        gl_FragColor = vec4(col * (1.0 + 0.8 * uNightFactor), alpha);
      }
    `
  });

  const fountainPoints = new THREE.Points(fountainGeo, fountainMat);
  fountainPoints.name = 'JinjiMusicFountain';
  fountainPoints.frustumCulled = false;
  group.add(fountainPoints);

  // --- 2. GANJIANG ROAD & CBD TRAFFIC LIGHT TRAILS (1 Draw Call) ---
  // Ribbon strips along Ganjiang Road (z = ±5.5, x from 140 to 635) and East CBD Ave (x = 1465 ± 5.5)
  const ribbonSegments: Array<{ ax: number; az: number; bx: number; bz: number; dir: number; lane: number }> = [
    // Ganjiang Road Eastbound & Westbound
    { ax: 160, az: -7.5, bx: 625, bz: -7.5, dir: 1, lane: 0 },
    { ax: 160, az: -3.5, bx: 625, bz: -3.5, dir: 1, lane: 1 },
    { ax: 160, az: 3.5, bx: 625, bz: 3.5, dir: -1, lane: 2 },
    { ax: 160, az: 7.5, bx: 625, bz: 7.5, dir: -1, lane: 3 },
    // West Bank Promenade Boulevard (N-S in front of Suzhou Center)
    { ax: 565, az: -360, bx: 565, bz: 360, dir: 1, lane: 4 },
    { ax: 573, az: -360, bx: 573, bz: 360, dir: -1, lane: 5 },
    // East CBD Avenue past Suzhou IFS
    { ax: 1460, az: -420, bx: 1460, bz: 380, dir: 1, lane: 6 },
    { ax: 1468, az: -420, bx: 1468, bz: 380, dir: -1, lane: 7 }
  ];

  const rPos: number[] = [];
  const rUv: number[] = [];
  const rMeta: number[] = []; // x: direction (+1/-1), y: laneSeed
  const rIdx: number[] = [];
  let vertOffset = 0;

  for (const seg of ribbonSegments) {
    const dx = seg.bx - seg.ax;
    const dz = seg.bz - seg.az;
    const len = Math.hypot(dx, dz);
    const nx = (-dz / len) * 1.1;
    const nz = (dx / len) * 1.1;
    const y = 1.92;

    rPos.push(
      seg.ax - nx, y, seg.az - nz,
      seg.ax + nx, y, seg.az + nz,
      seg.bx - nx, y, seg.bz - nz,
      seg.bx + nx, y, seg.bz + nz
    );
    rUv.push(0, 0, 0, 1, len / 45.0, 0, len / 45.0, 1);
    for (let k = 0; k < 4; k++) {
      rMeta.push(seg.dir, seg.lane * 1.37);
    }
    rIdx.push(
      vertOffset, vertOffset + 2, vertOffset + 1,
      vertOffset + 1, vertOffset + 2, vertOffset + 3
    );
    vertOffset += 4;
  }

  const trafficGeo = new THREE.BufferGeometry();
  trafficGeo.setAttribute('position', new THREE.Float32BufferAttribute(rPos, 3));
  trafficGeo.setAttribute('uv', new THREE.Float32BufferAttribute(rUv, 2));
  trafficGeo.setAttribute('aMeta', new THREE.Float32BufferAttribute(rMeta, 2));
  trafficGeo.setIndex(rIdx);

  const trafficUniforms = {
    uTime: { value: 0 },
    uIntensity: { value: 1.0 }
  };

  const trafficMat = new THREE.ShaderMaterial({
    uniforms: trafficUniforms,
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
    blending: THREE.AdditiveBlending,
    vertexShader: /* glsl */ `
      attribute vec2 aMeta;
      varying vec2 vUv;
      varying vec2 vMeta;
      void main() {
        vUv = uv;
        vMeta = aMeta;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform float uTime;
      uniform float uIntensity;
      varying vec2 vUv;
      varying vec2 vMeta;

      void main() {
        float dir = vMeta.x;
        float seed = vMeta.y;
        float speed = 1.45 + fract(seed * 0.71) * 0.6;
        float flow = vUv.x - dir * uTime * speed + seed;

        // Sharp head + long glowing tail streaks
        float streak1 = pow(fract(flow * 0.55), 5.0);
        float streak2 = pow(fract(flow * 0.92 + 0.37), 7.0);
        float widthMask = 1.0 - abs(vUv.y * 2.0 - 1.0);
        widthMask = pow(clamp(widthMask, 0.0, 1.0), 1.6);

        // Warm gold headlights one way, crimson/amber taillights the opposite way
        vec3 col = dir > 0.0 ? vec3(1.0, 0.84, 0.52) : vec3(1.0, 0.28, 0.22);
        // Subtle cyan accent pulse on CBD expressway
        vec3 accent = vec3(0.28, 0.82, 1.0);
        col = mix(col, accent, 0.16 * smoothstep(3.5, 6.5, seed));

        float alpha = (streak1 * 0.85 + streak2 * 0.65) * widthMask * uIntensity;
        if (alpha < 0.02) discard;
        gl_FragColor = vec4(col * 1.65, alpha);
      }
    `
  });

  const trafficMesh = new THREE.Mesh(trafficGeo, trafficMat);
  trafficMesh.name = 'GanjiangTrafficTrails';
  group.add(trafficMesh);

  // --- 3. FLOATING LANTERN GLOW & CANAL AMBIENT SPARKLES (1 Draw Call) ---
  const sparkCount = 420;
  const sPos = new Float32Array(sparkCount * 3);
  const sPhase = new Float32Array(sparkCount * 2); // x: phase, y: isModern (0=warm lantern, 1=cyan/gold)

  for (let i = 0; i < sparkCount; i++) {
    const t = i / sparkCount;
    let x = 0;
    let y = 5;
    let z = 0;
    let modern = 0;

    if (t < 0.25) {
      // Shantang Canal warm lanterns
      const u = t / 0.25;
      x = THREE.MathUtils.lerp(-900, -540, u) + (Math.sin(i * 13.7) * 16);
      z = THREE.MathUtils.lerp(-340, -140, u) + (Math.cos(i * 9.3) * 16);
      y = 4.5 + (i % 7) * 0.6;
    } else if (t < 0.52) {
      // Pingjiang Road & Old City lanterns
      const u = (t - 0.25) / 0.27;
      x = 140 + (i % 2 === 0 ? -12 : 12) + Math.sin(i * 7.1) * 8;
      z = THREE.MathUtils.lerp(-290, 120, u);
      y = 4.2 + (i % 5) * 0.55;
    } else if (t < 0.72) {
      // Hanshan & Panmen canal glow
      const u = (t - 0.52) / 0.20;
      x = i % 2 === 0 ? -1320 + Math.sin(i * 5.2) * 55 : -340 + Math.cos(i * 6.3) * 110;
      z = i % 2 === 0 ? 110 + (u - 0.5) * 260 : 340 + (u - 0.5) * 140;
      y = 4.5 + (i % 6) * 0.8;
    } else {
      // Jinji Lake promenade & Ligongdi twilight lights
      const u = (t - 0.72) / 0.28;
      const angle = u * Math.PI * 2;
      x = 1030 + Math.cos(angle) * (350 + Math.sin(i * 11.1) * 35);
      z = 40 + Math.sin(angle) * (410 + Math.cos(i * 8.3) * 35);
      y = 6.0 + (i % 8) * 1.4;
      modern = 1;
    }

    sPos[i * 3] = x;
    sPos[i * 3 + 1] = y;
    sPos[i * 3 + 2] = z;
    sPhase[i * 2] = (i * 0.371) % 6.283;
    sPhase[i * 2 + 1] = modern;
  }

  const sparkGeo = new THREE.BufferGeometry();
  sparkGeo.setAttribute('position', new THREE.BufferAttribute(sPos, 3));
  sparkGeo.setAttribute('aPhase', new THREE.BufferAttribute(sPhase, 2));

  const sparkUniforms = {
    uTime: { value: 0 },
    uGlow: { value: 0.8 }
  };

  const sparkMat = new THREE.ShaderMaterial({
    uniforms: sparkUniforms,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    vertexShader: /* glsl */ `
      attribute vec2 aPhase;
      uniform float uTime;
      varying float vModern;
      varying float vTwinkle;
      void main() {
        vec3 p = position;
        p.y += sin(uTime * 0.9 + aPhase.x) * 1.1;
        vModern = aPhase.y;
        vTwinkle = 0.72 + 0.28 * sin(uTime * 2.1 + aPhase.x * 2.0);
        vec4 mvPos = modelViewMatrix * vec4(p, 1.0);
        gl_Position = projectionMatrix * mvPos;
        gl_PointSize = clamp(520.0 / -mvPos.z, 2.5, 16.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform float uGlow;
      varying float vModern;
      varying float vTwinkle;
      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        float radial = pow(1.0 - d * 2.0, 2.2);
        vec3 warmLantern = vec3(1.0, 0.54, 0.20);
        vec3 cbdGlow = vec3(0.42, 0.85, 1.0);
        vec3 col = mix(warmLantern, cbdGlow, vModern);
        gl_FragColor = vec4(col * 1.5, radial * vTwinkle * uGlow);
      }
    `
  });

  const sparkPoints = new THREE.Points(sparkGeo, sparkMat);
  sparkPoints.name = 'SuzhouLanternGlows';
  group.add(sparkPoints);

  // --- 4. SOFT DRIFTING CANAL MIST & HIGH CLOUD WISPS (1 Draw Call) ---
  const mistCount = 120;
  const mPos = new Float32Array(mistCount * 3);
  const mSeed = new Float32Array(mistCount);

  for (let i = 0; i < mistCount; i++) {
    mPos[i * 3] = -1550 + ((i * 271.3) % 3200);
    mPos[i * 3 + 1] = 165 + ((i * 53.7) % 190);
    mPos[i * 3 + 2] = -780 + ((i * 197.9) % 1560);
    mSeed[i] = i * 0.73;
  }

  const mistGeo = new THREE.BufferGeometry();
  mistGeo.setAttribute('position', new THREE.BufferAttribute(mPos, 3));
  mistGeo.setAttribute('aSeed', new THREE.BufferAttribute(mSeed, 1));

  const mistUniforms = {
    uTime: { value: 0 },
    uNightFactor: { value: 0.2 }
  };

  const mistMat = new THREE.ShaderMaterial({
    uniforms: mistUniforms,
    transparent: true,
    depthWrite: false,
    vertexShader: /* glsl */ `
      attribute float aSeed;
      uniform float uTime;
      varying float vAlpha;
      void main() {
        vec3 p = position;
        p.x = mod(p.x + uTime * 3.5 + 1650.0, 3400.0) - 1650.0;
        p.z += sin(uTime * 0.12 + aSeed) * 14.0;
        vec4 mvPos = modelViewMatrix * vec4(p, 1.0);
        gl_Position = projectionMatrix * mvPos;
        gl_PointSize = clamp(24000.0 / max(-mvPos.z, 60.0), 18.0, 140.0);
        vAlpha = smoothstep(1800.0, 350.0, -mvPos.z) * smoothstep(50.0, 200.0, -mvPos.z);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform float uNightFactor;
      varying float vAlpha;
      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        float puff = smoothstep(0.5, 0.0, d);
        puff *= puff;
        vec3 dayMist = vec3(1.0, 0.92, 0.84);
        vec3 nightMist = vec3(0.24, 0.36, 0.58);
        vec3 col = mix(dayMist, nightMist, uNightFactor);
        gl_FragColor = vec4(col, puff * vAlpha * mix(0.11, 0.055, uNightFactor));
      }
    `
  });

  const mistPoints = new THREE.Points(mistGeo, mistMat);
  mistPoints.name = 'SuzhouDriftingMist';
  mistPoints.frustumCulled = false;
  group.add(mistPoints);

  return {
    group,
    update(elapsed: number, nightFactor: number, emissiveScale: number) {
      fountainUniforms.uTime.value = elapsed;
      fountainUniforms.uNightFactor.value = nightFactor;

      trafficUniforms.uTime.value = elapsed;
      trafficUniforms.uIntensity.value = THREE.MathUtils.clamp(0.32 + emissiveScale * 0.52, 0.25, 1.6);

      sparkUniforms.uTime.value = elapsed;
      sparkUniforms.uGlow.value = THREE.MathUtils.clamp(0.18 + emissiveScale * 0.42, 0.15, 1.15);

      mistUniforms.uTime.value = elapsed;
      mistUniforms.uNightFactor.value = nightFactor;
    }
  };
}
