import * as THREE from 'three';
import type { WorldLayout } from '../types/world';
import { createWaterMaterial, type WaterUniforms } from '../shaders/waterShader';

export interface TerrainSystem {
  group: THREE.Group;
  groundMesh: THREE.Mesh;
  waterMesh: THREE.Mesh;
  waterUniforms: WaterUniforms;
  /** Returns signed distance to nearest water body: < 0 inside water, > 0 on land (meters) */
  waterSignedDistance: (x: number, z: number) => number;
  /** True if (x, z) is safely inside open water */
  isWater: (x: number, z: number, margin?: number) => boolean;
  /** Returns terrain ground elevation at (x, z) */
  getElevation: (x: number, z: number) => number;
}

function distToSegment(px: number, pz: number, ax: number, az: number, bx: number, bz: number): number {
  const vx = bx - ax;
  const vz = bz - az;
  const wx = px - ax;
  const wz = pz - az;
  const c1 = vx * wx + vz * wz;
  if (c1 <= 0) return Math.hypot(px - ax, pz - az);
  const c2 = vx * vx + vz * vz;
  if (c2 <= c1) return Math.hypot(px - bx, pz - bz);
  const t = c1 / c2;
  return Math.hypot(px - (ax + t * vx), pz - (az + t * vz));
}

/**
 * Signed distance to the continuous Suzhou waterway network:
 * negative = inside water, 0 = shoreline, positive = land (approximate meters).
 */
export function computeWaterSignedDistance(x: number, z: number, layout: WorldLayout): number {
  const wb = layout.waterBodies;

  // 1. Grand Canal (North-South, gentle organic bend near Hanshan Temple)
  const grandCurveOffset = Math.sin(z * 0.0022) * 18;
  const dGrand = Math.abs(x - (wb.grandCanal.xCenter + grandCurveOffset)) - wb.grandCanal.width * 0.5;

  // 2. Shantang Canal (Tiger Hill -> NW Outer Moat)
  const dShantang =
    distToSegment(x, z, wb.shantangCanal.from[0], wb.shantangCanal.from[1], wb.shantangCanal.to[0], wb.shantangCanal.to[1]) -
    wb.shantangCanal.width * 0.5;

  // 2b. Short connecting canal from Grand Canal east towards Xiyuan/Tiger Hill
  const dWestLink = distToSegment(x, z, -1290, -280, -900, -340) - 13;

  // 3. Outer Moat rectangular ring (minX..maxX, minZ..maxZ)
  const m = wb.outerMoat;
  const dMoatTop = distToSegment(x, z, m.minX, m.minZ, m.maxX, m.minZ) - m.width * 0.5;
  const dMoatBot = distToSegment(x, z, m.minX, m.maxZ, m.maxX, m.maxZ) - m.width * 0.5;
  const dMoatLeft = distToSegment(x, z, m.minX, m.minZ, m.minX, m.maxZ) - m.width * 0.5;
  const dMoatRight = distToSegment(x, z, m.maxX, m.minZ, m.maxX, m.maxZ) - m.width * 0.5;
  const dMoat = Math.min(dMoatTop, dMoatBot, dMoatLeft, dMoatRight);

  // 4. Pingjiang Canal (inside NE Gusu) + feeder to North Moat
  const dPingjiang =
    distToSegment(x, z, wb.pingjiangCanal.from[0], wb.pingjiangCanal.from[1] - 110, wb.pingjiangCanal.to[0], wb.pingjiangCanal.to[1]) -
    wb.pingjiangCanal.width * 0.5;

  // 4b. Panmen Wumen Bridge & Twin Water Gate East-West Canal branch (world Z = 352, X in [-480, -210])
  const dPanmenCanal = distToSegment(x, z, -485, 352, -205, 352) - 13.0;

  // 5. Jinji Lake — organic lake basin respecting West Bank Plaza, MoCA/Eye Peninsula & Moon Harbour Peninsula
  const jl = wb.jinjiLake;
  const nx = (x - jl.centerX) / jl.radiusX;
  const nz = (z - jl.centerZ) / jl.radiusZ;
  const rNorm = Math.hypot(nx, nz);
  // Subtle organic coastline undulation
  const angle = Math.atan2(nz, nx);
  const coastWobble = 0.035 * Math.sin(angle * 3.0 + 0.6) + 0.02 * Math.cos(angle * 5.0 - 0.4);
  let dJinji = (rNorm - (1.0 + coastWobble)) * 410;

  // Carve solid waterfront land promontories so Gate of Orient, MoCA/Eye & Arts Centre sit on real lakeside plazas!
  // a) West Bank Plaza (x <= 732 around Gate of the Orient z in [-210, 210])
  const westPlazaCut = 732 - x;
  if (Math.abs(z) < 260) {
    const zBlend = 1.0 - THREE.MathUtils.smoothstep(Math.abs(z), 170, 260);
    dJinji = Math.max(dJinji, westPlazaCut * zBlend - (1.0 - zBlend) * 90);
  }

  // b) East Bank MoCA + Eye of Suzhou Peninsula around (1310, 125)
  const dMoCAPeninsula = 135 - Math.hypot((x - 1345) * 1.0, (z - 125) * 1.12);
  dJinji = Math.max(dJinji, dMoCAPeninsula);

  // c) NE Arts Centre + Moon Harbour Peninsula around (1280, -230)
  const dArtsPeninsula = 138 - Math.hypot((x - 1320) * 1.0, (z + 230) * 1.15);
  dJinji = Math.max(dJinji, dArtsPeninsula);

  // d) East Bank continuous shoreline beyond x >= 1390
  const eastShore = x - 1390;
  dJinji = Math.max(dJinji, eastShore);

  return Math.min(dGrand, dShantang, dWestLink, dMoat, dPingjiang, dPanmenCanal, dJinji);
}

export function createTerrainSystem(layout: WorldLayout): TerrainSystem {
  const group = new THREE.Group();
  group.name = 'SuzhouBasinTerrain';

  const waterSignedDistance = (x: number, z: number) => computeWaterSignedDistance(x, z, layout);
  const isWater = (x: number, z: number, margin = 0) => waterSignedDistance(x, z) < -margin;

  // Land base sits at 1.48m (0.12m below station groundLevelY=1.6m) to prevent Z-fighting with hero plinths!
  const LAND_Y = layout.coordinateSystem.groundLevelY - 0.12;
  const BED_Y = -2.4;

  // Ancient/Garden station pads with recessed internal ponds/canals: depress terrain to 0.35m (above y=0 water, below y=0.85..1.25 model ponds!)
  const recessedPads: Array<{ cx: number; cz: number; hx: number; hz: number }> = [
    { cx: -1360, cz: 110, hx: 68, hz: 54 },  // Hanshan & Maple Canal
    { cx: -1080, cz: -160, hx: 58, hz: 50 }, // Xiyuan Release Pond
    { cx: -560, cz: -90, hx: 58, hz: 48 },   // Lingering Garden Pond
    { cx: 80, cz: 240, hx: 82, hz: 56 },     // Wangshi Rosy Cloud Pool
    { cx: -10, cz: -180, hx: 108, hz: 92 },  // Beisi & Pingjiang Road Canal
    { cx: 210, cz: -95, hx: 44, hz: 40 },    // Lion Grove Pond
    { cx: 230, cz: -230, hx: 72, hz: 50 },   // Humble Admin Lotus Pond
    { cx: 265, cz: -220, hx: 56, hz: 40 }    // Suzhou Museum Water Court
  ];

  const getElevation = (x: number, z: number): number => {
    const d = waterSignedDistance(x, z);
    if (d <= -10) return BED_Y;
    let baseY = LAND_Y;
    if (d < 6) {
      const t = THREE.MathUtils.smoothstep(d, -10, 6);
      baseY = THREE.MathUtils.lerp(BED_Y, LAND_Y, t);
    } else {
      // Gentle rolling hills in far western periphery (outside playable city) for scenic silhouette
      const westFar = THREE.MathUtils.smoothstep(-x, 1540, 2150);
      const northFar = THREE.MathUtils.smoothstep(-z, 760, 1250);
      const southFar = THREE.MathUtils.smoothstep(z, 760, 1250);
      const hillNoise =
        Math.sin(x * 0.0055) * Math.cos(z * 0.0065) * 0.5 +
        Math.sin(x * 0.011 - z * 0.009) * 0.35 +
        0.65;
      const farHills = Math.max(westFar, northFar * 0.55, southFar * 0.55) * 58 * Math.max(hillNoise, 0.15);
      baseY = LAND_Y + farHills;
    }

    // Smoothly depress under Hero garden/canal footprints so recessed ponds/canals never clip terrain
    if (baseY > 0.35) {
      for (let i = 0; i < recessedPads.length; i++) {
        const p = recessedPads[i];
        const dx = Math.abs(x - p.cx) - p.hx;
        const dz = Math.abs(z - p.cz) - p.hz;
        const edgeDist = Math.max(dx, dz);
        if (edgeDist < 12) {
          const blend = 1.0 - THREE.MathUtils.smoothstep(edgeDist, -6, 12);
          baseY = Math.min(baseY, THREE.MathUtils.lerp(baseY, 0.35, blend));
        }
      }
    }
    return baseY;
  };

  // 1. Continuous Basin Ground Mesh (4600m x 2800m, 230 x 140 grid = ~64K tris, 1 draw call!)
  const width = 4600;
  const depth = 2800;
  const segX = 230;
  const segZ = 140;

  const groundGeo = new THREE.PlaneGeometry(width, depth, segX, segZ);
  groundGeo.rotateX(-Math.PI / 2);

  const posAttr = groundGeo.attributes.position as THREE.BufferAttribute;
  const colors = new Float32Array(posAttr.count * 3);

  const colBed = new THREE.Color('#13222b');
  const colQuay = new THREE.Color('#6f6c66');
  const colGusuStone = new THREE.Color('#4a4946');
  const colGusuGreen = new THREE.Color('#2c4432');
  const colRoad = new THREE.Color('#252830');
  const colModernPlaza = new THREE.Color('#4d535e');
  const colHillGreen = new THREE.Color('#25392a');
  const tmpColor = new THREE.Color();

  for (let i = 0; i < posAttr.count; i++) {
    const x = posAttr.getX(i) + 40; // center slightly east to match [-1700, 1750]
    const z = posAttr.getZ(i);
    posAttr.setX(i, x);

    const d = waterSignedDistance(x, z);
    const y = getElevation(x, z);
    posAttr.setY(i, y);

    // Determine land-use vertex color
    if (d < -1.5) {
      tmpColor.copy(colBed);
    } else if (d < 9.0) {
      // Crisp Suzhou granite embankment along canals & Jinji Lake promenade
      tmpColor.copy(colQuay);
    } else {
      // Modern East Suzhou vs Historic Gusu West
      const modernBlend = THREE.MathUtils.smoothstep(x, 380, 580);
      tmpColor.copy(colGusuStone).lerp(colModernPlaza, modernBlend);

      // Subtle organic park / garden green zones
      const patch = Math.sin(x * 0.012) * Math.cos(z * 0.014) + Math.sin((x + z) * 0.008) * 0.5;
      if (patch > 0.38 && modernBlend < 0.85) {
        tmpColor.lerp(colGusuGreen, 0.48);
      }

      // Lakefront greenery belt around Jinji Lake
      if (x > 640 && d < 32) {
        tmpColor.lerp(colGusuGreen, 0.35);
      }

      // Ganjiang Road (East-West grand boulevard along z ≈ 0 from Old City to Gate of Orient!)
      if (x > -460 && x < 720 && Math.abs(z) < 16) {
        tmpColor.lerp(colRoad, 0.85);
      }
      // East CBD Avenue along x ≈ 1460 (in front of IFS)
      if (Math.abs(x - 1465) < 15 && Math.abs(z) < 420) {
        tmpColor.lerp(colRoad, 0.78);
      }
      // Distant hills greenery
      if (y > LAND_Y + 4) {
        tmpColor.lerp(colHillGreen, THREE.MathUtils.clamp((y - LAND_Y) / 28, 0, 0.85));
      }

      // Micro tonal variation so large ground planes never look plastic
      const micro = (Math.sin(x * 0.07) * Math.cos(z * 0.07)) * 0.035;
      tmpColor.offsetHSL(0, 0, micro);
    }

    colors[i * 3] = tmpColor.r;
    colors[i * 3 + 1] = tmpColor.g;
    colors[i * 3 + 2] = tmpColor.b;
  }

  groundGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  groundGeo.computeVertexNormals();

  const groundMat = new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.88,
    metalness: 0.06
  });

  const groundMesh = new THREE.Mesh(groundGeo, groundMat);
  groundMesh.name = 'SuzhouBasinGround';
  groundMesh.receiveShadow = true;
  groundMesh.castShadow = false;
  group.add(groundMesh);

  // 2. Continuous Custom GLSL Animated Water Surface Mesh at y = waterLevelY (0.0)
  // Using 160x100 grid with per-vertex aShore attribute so shoreline foam & swells align cleanly!
  const waterGeo = new THREE.PlaneGeometry(4200, 2400, 160, 100);
  waterGeo.rotateX(-Math.PI / 2);
  const wPos = waterGeo.attributes.position as THREE.BufferAttribute;
  const shoreAttr = new Float32Array(wPos.count);

  for (let i = 0; i < wPos.count; i++) {
    const x = wPos.getX(i) + 40;
    const z = wPos.getZ(i);
    wPos.setX(i, x);

    const d = waterSignedDistance(x, z);
    // Shore factor = 1 near coastline (d in [-14..2]), 0 in deep open lake (d < -45)
    shoreAttr[i] = 1.0 - THREE.MathUtils.clamp(-d / 28, 0, 1);
  }
  waterGeo.setAttribute('aShore', new THREE.BufferAttribute(shoreAttr, 1));

  const { material: waterMat, uniforms: waterUniforms } = createWaterMaterial();
  const waterMesh = new THREE.Mesh(waterGeo, waterMat);
  waterMesh.name = 'SuzhouWaterSurface';
  waterMesh.position.y = layout.coordinateSystem.waterLevelY;
  waterMesh.receiveShadow = false;
  group.add(waterMesh);

  return {
    group,
    groundMesh,
    waterMesh,
    waterUniforms,
    waterSignedDistance,
    isWater,
    getElevation
  };
}
