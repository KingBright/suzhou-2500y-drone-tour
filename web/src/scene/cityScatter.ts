import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import type { WorldLayout } from '../types/world';
import type { TerrainSystem } from './terrain';
import type { AtmosphereManager } from './atmosphere';

export interface CityScatterResult {
  group: THREE.Group;
  loadedKits: string[];
  missingKits: string[];
  instanceCount: number;
}

interface ExtractedPart {
  meshes: Array<{
    geometry: THREE.BufferGeometry;
    material: THREE.Material;
    isEmissive: boolean;
  }>;
}

function createRng(seed: number) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

function getKitEmissiveChannel(std: THREE.MeshStandardMaterial): 'warm' | 'gold' | 'cyan' | 'accent' | 'none' {
  const n = (std.name || '').toLowerCase();
  if (n.includes('emissive_warm') || n.includes('lantern') || n.includes('window')) return 'warm';
  if (n.includes('emissive_gold')) return 'gold';
  if (n.includes('emissive_cyan')) return 'cyan';
  if (n.includes('emissive_accent')) return 'accent';
  if (std.emissive && std.emissive.r + std.emissive.g + std.emissive.b > 0.15 && std.emissiveIntensity > 0.05) {
    return std.emissive.b > std.emissive.r ? 'cyan' : 'warm';
  }
  return 'none';
}

function bakePartGeometry(
  geo: THREE.BufferGeometry,
  localMat: THREE.Matrix4,
  baseColor: THREE.Color
): THREE.BufferGeometry | null {
  const pos = geo.getAttribute('position');
  if (!pos || pos.count === 0) return null;
  const cloned = geo.index ? geo.toNonIndexed() : geo.clone();
  cloned.applyMatrix4(localMat);
  if (!cloned.getAttribute('normal')) cloned.computeVertexNormals();

  const count = cloned.getAttribute('position').count;
  const colors = new Float32Array(count * 3);
  const existing = cloned.getAttribute('color');
  for (let i = 0; i < count; i++) {
    if (existing) {
      colors[i * 3] = existing.getX(i) * baseColor.r;
      colors[i * 3 + 1] = existing.getY(i) * baseColor.g;
      colors[i * 3 + 2] = existing.getZ(i) * baseColor.b;
    } else {
      colors[i * 3] = baseColor.r;
      colors[i * 3 + 1] = baseColor.g;
      colors[i * 3 + 2] = baseColor.b;
    }
  }
  const keep = new Set(['position', 'normal']);
  for (const attr of Object.keys(cloned.attributes)) {
    if (!keep.has(attr)) cloned.deleteAttribute(attr);
  }
  cloned.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  cloned.clearGroups();
  return cloned;
}

/**
 * Extract each modular kit part and merge its non-emissive sub-meshes into 1 vertex-colored
 * geometry + emissive sub-meshes into 1 geometry per emissive channel, slashing InstancedMesh
 * draw calls in half while preserving 100% of colors and dynamic night glow!
 */
function extractKitParts(root: THREE.Object3D, expectedNames: string[]): Map<string, ExtractedPart> {
  root.updateMatrixWorld(true);
  const map = new Map<string, ExtractedPart>();

  for (const targetName of expectedNames) {
    const lower = targetName.toLowerCase();
    let foundNode: THREE.Object3D | null = null;
    root.traverse((obj) => {
      if (foundNode) return;
      if (obj.name && (obj.name.toLowerCase() === lower || obj.name.toLowerCase().startsWith(lower))) {
        foundNode = obj;
      }
    });
    if (!foundNode) continue;

    const partRoot = foundNode as THREE.Object3D;
    const invRoot = new THREE.Matrix4().copy(partRoot.matrixWorld).invert();
    const isTower = targetName.startsWith('Tower');

    const opaqueGeos: THREE.BufferGeometry[] = [];
    const emissiveBuckets = new Map<string, { color: THREE.Color; geos: THREE.BufferGeometry[] }>();

    partRoot.traverse((child) => {
      const m = child as THREE.Mesh;
      if (!m.isMesh || !m.geometry) return;
      const localMat = new THREE.Matrix4().multiplyMatrices(invRoot, m.matrixWorld);
      const rawMat = Array.isArray(m.material) ? m.material[0] : m.material;
      const std = rawMat && (rawMat as THREE.MeshStandardMaterial).isMeshStandardMaterial
        ? (rawMat as THREE.MeshStandardMaterial)
        : null;
      const baseCol = std ? std.color : new THREE.Color('#cccccc');
      const baked = bakePartGeometry(m.geometry, localMat, baseCol);
      if (!baked) return;

      const emChan = std ? getKitEmissiveChannel(std) : 'none';
      if (emChan !== 'none' && std) {
        let eb = emissiveBuckets.get(emChan);
        if (!eb) {
          eb = { color: std.emissive.clone(), geos: [] };
          emissiveBuckets.set(emChan, eb);
        }
        eb.geos.push(baked);
      } else {
        opaqueGeos.push(baked);
      }
    });

    const meshes: ExtractedPart['meshes'] = [];
    if (opaqueGeos.length > 0) {
      const mergedOpaque = opaqueGeos.length === 1 ? opaqueGeos[0] : mergeGeometries(opaqueGeos, false);
      for (const g of opaqueGeos) if (g !== mergedOpaque) g.dispose();
      if (mergedOpaque) {
        meshes.push({
          geometry: mergedOpaque,
          material: new THREE.MeshStandardMaterial({
            name: `KitOpaque_${targetName}`,
            color: '#ffffff',
            vertexColors: true,
            roughness: isTower ? 0.28 : 0.80,
            metalness: isTower ? 0.68 : 0.06
          }),
          isEmissive: false
        });
      }
    }

    for (const [chan, eb] of emissiveBuckets.entries()) {
      const mergedEm = eb.geos.length === 1 ? eb.geos[0] : mergeGeometries(eb.geos, false);
      for (const g of eb.geos) if (g !== mergedEm) g.dispose();
      if (mergedEm) {
        meshes.push({
          geometry: mergedEm,
          material: new THREE.MeshStandardMaterial({
            name: `Emissive_${chan.charAt(0).toUpperCase() + chan.slice(1)}_Kit_${targetName}`,
            color: '#ffffff',
            vertexColors: true,
            emissive: eb.color,
            emissiveIntensity: 1.0,
            roughness: 0.35,
            toneMapped: true
          }),
          isEmissive: true
        });
      }
    }

    if (meshes.length > 0) {
      map.set(targetName, { meshes });
    }
  }
  return map;
}

function createFallbackKitParts(): Map<string, ExtractedPart> {
  const map = new Map<string, ExtractedPart>();
  const mat = new THREE.MeshStandardMaterial({ color: '#d8d2c6', roughness: 0.82 });
  const box = new THREE.BoxGeometry(10, 8, 10);
  box.translate(0, 4, 0);
  for (const name of [
    'HouseA', 'HouseB', 'HouseC', 'WillowTree', 'PineTree', 'StoneBridge', 'LanternPost', 'WoodenBoat',
    'TowerA', 'TowerB', 'TowerC', 'TowerD', 'ModernLamp', 'YachtBoat', 'ParkTree'
  ]) {
    map.set(name, { meshes: [{ geometry: box, material: mat, isEmissive: false }] });
  }
  return map;
}

function addInstancedPart(
  parent: THREE.Group,
  partName: string,
  part: ExtractedPart | undefined,
  matrices: THREE.Matrix4[],
  castShadow: boolean
): number {
  if (!part || matrices.length === 0) return 0;

  for (let mIdx = 0; mIdx < part.meshes.length; mIdx++) {
    const sub = part.meshes[mIdx];
    const inst = new THREE.InstancedMesh(sub.geometry, sub.material, matrices.length);
    inst.name = `Inst_${partName}_${mIdx}`;
    inst.castShadow = castShadow && !sub.isEmissive;
    inst.receiveShadow = true;

    for (let i = 0; i < matrices.length; i++) {
      inst.setMatrixAt(i, matrices[i]);
    }
    inst.instanceMatrix.needsUpdate = true;
    inst.computeBoundingSphere();
    parent.add(inst);
  }
  return matrices.length;
}

export async function buildCityScatter(
  layout: WorldLayout,
  terrain: TerrainSystem,
  atmosphere: AtmosphereManager
): Promise<CityScatterResult> {
  const group = new THREE.Group();
  group.name = 'SuzhouInstancedCity';

  const loader = new GLTFLoader();
  const loadedKits: string[] = [];
  const missingKits: string[] = [];
  const parts = createFallbackKitParts();

  await Promise.all(
    layout.modularKits.map(async (kit) => {
      const file = kit.glb.split('/').pop() || kit.id;
      try {
        const gltf = await loader.loadAsync(`./${kit.glb}`);
        const extracted = extractKitParts(gltf.scene, kit.parts);
        for (const [k, v] of extracted.entries()) {
          parts.set(k, v);
        }
        loadedKits.push(file);
      } catch {
        missingKits.push(file);
      }
    })
  );

  // Exclusion zones around every Hero station footprint + key drone sightlines + heroView foregrounds
  const exclusions: Array<{ x: number; z: number; rx: number; rz: number }> = [];
  for (const st of layout.stations) {
    exclusions.push({
      x: st.anchor.x,
      z: st.anchor.z,
      rx: st.footprint.w * 0.56 + 14,
      rz: st.footprint.d * 0.56 + 14
    });
    if (st.xiyuanAnchor) {
      exclusions.push({ x: st.xiyuanAnchor.x, z: st.xiyuanAnchor.z, rx: 95, rz: 85 });
    }
    if (st.shizilinAnchor) {
      exclusions.push({ x: st.shizilinAnchor.x, z: st.shizilinAnchor.z, rx: 72, rz: 70 });
    }
    if (st.museumAnchor) {
      exclusions.push({ x: st.museumAnchor.x, z: st.museumAnchor.z, rx: 82, rz: 75 });
    }
    exclusions.push({ x: st.heroView.cam[0], z: st.heroView.cam[2], rx: 58, rz: 58 });
    exclusions.push({
      x: (st.heroView.cam[0] + st.heroView.lookAt[0]) * 0.5,
      z: (st.heroView.cam[2] + st.heroView.lookAt[2]) * 0.5,
      rx: 46,
      rz: 46
    });
  }

  const isExcluded = (x: number, z: number, extraPad = 0): boolean => {
    if (x > -480 && x < 740 && Math.abs(z) < 28 + extraPad) return true;
    if (Math.abs(x - 1465) < 26 + extraPad && Math.abs(z) < 420) return true;
    if (x > 460 && x < 840 && Math.abs(z) < 62 + extraPad) return true;

    for (let i = 0; i < exclusions.length; i++) {
      const e = exclusions[i];
      if (Math.abs(x - e.x) < e.rx + extraPad && Math.abs(z - e.z) < e.rz + extraPad) {
        return true;
      }
    }
    return false;
  };

  const rng = createRng(25000514);
  const landY = layout.coordinateSystem.groundLevelY - 0.12;
  const waterY = layout.coordinateSystem.waterLevelY;

  const dummy = new THREE.Object3D();
  const makeMat = (x: number, y: number, z: number, rotY: number, sx: number, sy: number, sz: number) => {
    dummy.position.set(x, y, z);
    dummy.rotation.set(0, rotY, 0);
    dummy.scale.set(sx, sy, sz);
    dummy.updateMatrix();
    return dummy.matrix.clone();
  };

  const buckets: Record<string, THREE.Matrix4[]> = {
    HouseA: [],
    HouseB: [],
    HouseC: [],
    WillowTree: [],
    PineTree: [],
    StoneBridge: [],
    LanternPost: [],
    WoodenBoat: [],
    TowerA: [],
    TowerB: [],
    TowerC: [],
    TowerD: [],
    ModernLamp: [],
    YachtBoat: [],
    ParkTree: []
  };

  // --- 1. ANCIENT GUSU HOUSES ---
  for (let gx = -1480; gx <= 430; gx += 26) {
    for (let gz = -580; gz <= 560; gz += 24) {
      const x = gx + (rng() - 0.5) * 10;
      const z = gz + (rng() - 0.5) * 9;
      if (terrain.waterSignedDistance(x, z) < 11) continue;
      if (isExcluded(x, z, 6)) continue;

      const insideMoat = x > -470 && x < 370 && z > -390 && z < 410;
      const nearShantang = x > -1180 && x < -480 && z > -380 && z < 160;
      const keepProb = insideMoat ? 0.68 : nearShantang ? 0.45 : 0.28;
      if (rng() > keepProb) continue;

      const pick = rng();
      const key = pick < 0.38 ? 'HouseA' : pick < 0.72 ? 'HouseB' : 'HouseC';
      const rot = (Math.floor(rng() * 4) * Math.PI) / 2;
      const s = 0.85 + rng() * 0.35;
      buckets[key].push(makeMat(x, landY, z, rot, s, s * (0.9 + rng() * 0.25), s));
    }
  }

  // --- 2. GUSU WILLOWS, PINES & LANTERN POSTS ---
  for (let i = 0; i < 650; i++) {
    const x = -1480 + rng() * 1980;
    const z = -620 + rng() * 1240;
    const d = terrain.waterSignedDistance(x, z);
    if (d < 4 || d > 180) continue;
    if (isExcluded(x, z, 2)) continue;

    if (d < 16) {
      const s = 0.78 + rng() * 0.52;
      buckets.WillowTree.push(makeMat(x, landY, z, rng() * Math.PI * 2, s, s, s));
      if (rng() < 0.45 && buckets.LanternPost.length < 180) {
        buckets.LanternPost.push(makeMat(x + (rng() - 0.5) * 3, landY, z + (rng() - 0.5) * 3, rng() * Math.PI * 2, 1, 1, 1));
      }
    } else if (rng() < 0.35) {
      const s = 0.8 + rng() * 0.5;
      const key = rng() < 0.55 ? 'PineTree' : 'WillowTree';
      buckets[key].push(makeMat(x, landY, z, rng() * Math.PI * 2, s, s, s));
    }
  }

  // --- 3. WOODEN AWNING BOATS ---
  const canalBoatSpots: Array<[number, number, number]> = [
    [-1320, -140, Math.PI / 2 + 0.08],
    [-1305, 45, Math.PI / 2 - 0.05],
    [-1330, 220, Math.PI / 2 + 0.12],
    [-1315, -310, Math.PI / 2],
    [-810, -290, -0.50],
    [-710, -235, -0.52],
    [-610, -180, -0.48],
    [-480, -210, Math.PI / 2],
    [-480, 80, Math.PI / 2],
    [-480, 240, Math.PI / 2],
    [-120, 420, 0.0],
    [160, 420, 0.0],
    [380, 160, Math.PI / 2],
    [380, -140, Math.PI / 2],
    [40, -400, 0.0],
    [140, -210, Math.PI / 2],
    [140, -60, Math.PI / 2],
    [140, 65, Math.PI / 2]
  ];
  for (const [bx, bz, rot] of canalBoatSpots) {
    if (terrain.isWater(bx, bz, 2)) {
      buckets.WoodenBoat.push(makeMat(bx, waterY + 0.08, bz, rot, 1.0, 1.0, 1.0));
    }
  }

  // --- 4. STONE BRIDGES ---
  const bridgeSpots: Array<[number, number, number, number]> = [
    [-760, -262, 1.05, 1.55],
    [-640, -195, 1.05, 1.55],
    [-480, -260, 0.0, 2.3],
    [-480, 110, 0.0, 2.3],
    [380, 0, 0.0, 2.5],
    [140, -140, 0.0, 1.05],
    [140, 35, 0.0, 1.05]
  ];
  for (const [bx, bz, rot, sc] of bridgeSpots) {
    buckets.StoneBridge.push(makeMat(bx, waterY + 0.15, bz, rot, sc, 1.05, 1.25));
  }

  // --- 5. MODERN JINJI LAKE CBD SKYSCRAPER CLUSTERS ---
  const cbdClusters: Array<{ xMin: number; xMax: number; zMin: number; zMax: number; stepX: number; stepZ: number; heightBoost: number }> = [
    { xMin: 465, xMax: 695, zMin: -540, zMax: -175, stepX: 66, stepZ: 64, heightBoost: 0.95 },
    { xMin: 465, xMax: 695, zMin: 175, zMax: 520, stepX: 66, stepZ: 64, heightBoost: 0.92 },
    { xMin: 1410, xMax: 1680, zMin: -540, zMax: 480, stepX: 68, stepZ: 68, heightBoost: 1.15 },
    { xMin: 780, xMax: 1380, zMin: -640, zMax: -475, stepX: 78, stepZ: 68, heightBoost: 0.85 },
    { xMin: 760, xMax: 1420, zMin: 530, zMax: 680, stepX: 82, stepZ: 72, heightBoost: 0.78 }
  ];

  const towerKeys = ['TowerA', 'TowerB', 'TowerC', 'TowerD'];
  for (const c of cbdClusters) {
    for (let gx = c.xMin; gx <= c.xMax; gx += c.stepX) {
      for (let gz = c.zMin; gz <= c.zMax; gz += c.stepZ) {
        const x = gx + (rng() - 0.5) * 20;
        const z = gz + (rng() - 0.5) * 20;
        if (terrain.waterSignedDistance(x, z) < 22) continue;
        if (isExcluded(x, z, 18)) continue;
        if (rng() > 0.74) continue;

        const tKey = towerKeys[Math.floor(rng() * towerKeys.length)];
        const rot = (Math.floor(rng() * 4) * Math.PI) / 2;
        const wScale = 0.78 + rng() * 0.44;
        const hScale = (0.65 + rng() * 0.65) * c.heightBoost;
        buckets[tKey].push(makeMat(x, landY, z, rot, wScale, hScale, wScale));
      }
    }
  }

  // --- 6. JINJI LAKE PARK TREES, MODERN LAMPS & YACHTS ---
  for (let i = 0; i < 360; i++) {
    const x = 440 + rng() * 1240;
    const z = -620 + rng() * 1240;
    const d = terrain.waterSignedDistance(x, z);
    if (d > 5 && d < 42 && !isExcluded(x, z, 4)) {
      const s = 0.85 + rng() * 0.55;
      buckets.ParkTree.push(makeMat(x, landY, z, rng() * Math.PI * 2, s, s, s));
      if (rng() < 0.35 && buckets.ModernLamp.length < 130) {
        buckets.ModernLamp.push(makeMat(x + 2.5, landY, z + 2.5, rng() * Math.PI * 2, 1, 1, 1));
      }
    }
  }

  for (let i = 0; i < 24; i++) {
    const angle = (i / 24) * Math.PI * 2;
    const r = 130 + rng() * 185;
    const x = 1030 + Math.cos(angle) * r;
    const z = 25 + Math.sin(angle) * (r * 1.15);
    if (!terrain.isWater(x, z, 32)) continue;
    if (Math.hypot(x - 795, z) < 95) continue;
    if (Math.abs(z - 365) < 55) continue;
    buckets.YachtBoat.push(makeMat(x, waterY + 0.1, z, rng() * Math.PI * 2, 0.9 + rng() * 0.35, 1, 0.9 + rng() * 0.35));
  }

  // Only tall CBD skyscrapers cast shadows; small scattered houses/trees receive shadows without shadow-pass bloat!
  let totalInstances = 0;
  for (const [partName, mats] of Object.entries(buckets)) {
    const castsShadow = partName.startsWith('Tower');
    totalInstances += addInstancedPart(group, partName, parts.get(partName), mats, castsShadow);
  }

  atmosphere.registerEmissivesFromObject(group);

  return {
    group,
    loadedKits,
    missingKits,
    instanceCount: totalInstances
  };
}
