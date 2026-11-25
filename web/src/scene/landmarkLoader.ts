import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import type { WorldLayout, Vec3Obj } from '../types/world';
import type { AtmosphereManager } from './atmosphere';

export interface LoadedLandmarks {
  group: THREE.Group;
  loadedModels: string[];
  missingModels: string[];
  ferrisWheelRotor: THREE.Object3D | null;
  ferrisRotationAxis: 'x' | 'y' | 'z';
}

interface LandmarkJob {
  key: string;
  url: string;
  anchor: Vec3Obj;
  stationId: string;
  district: 'west' | 'gusu' | 'modern';
  fallbackKind: string;
  maxH: number;
}

function createFallbackSilhouette(job: LandmarkJob): THREE.Group {
  const g = new THREE.Group();
  g.name = `Fallback_${job.key}`;
  const matWall = new THREE.MeshStandardMaterial({ color: '#e6dfd3', roughness: 0.82 });
  const matGlass = new THREE.MeshStandardMaterial({ color: '#2b4d6e', metalness: 0.75, roughness: 0.18 });
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(40, Math.max(job.maxH * 0.7, 12), 40),
    job.district === 'modern' ? matGlass : matWall
  );
  mesh.position.y = Math.max(job.maxH * 0.35, 6);
  g.add(mesh);
  return g;
}

function buildJobList(layout: WorldLayout): LandmarkJob[] {
  const jobs: LandmarkJob[] = [];
  for (const st of layout.stations) {
    const file = st.glb.split('/').pop() || st.id;
    const district: 'west' | 'gusu' | 'modern' =
      st.index <= 4 ? 'west' : st.index <= 7 ? 'gusu' : 'modern';

    let fallbackKind = 'garden';
    if (st.id === '08-gate-of-orient') fallbackKind = 'gate_of_orient';
    else if (st.id === '12-suzhou-ifs') fallbackKind = 'suzhou_ifs';
    else if (st.id === '10-moca-eye') fallbackKind = 'moca_eye';
    else if (st.id === '11-arts-centre') fallbackKind = 'arts_centre';
    else if (st.id === '09-ligongdi') fallbackKind = 'ligongdi';
    else if (st.footprint.maxH >= 35) fallbackKind = 'pagoda';

    jobs.push({
      key: file,
      url: `./${st.glb}`,
      anchor: st.anchor,
      stationId: st.id,
      district,
      fallbackKind,
      maxH: st.footprint.maxH
    });

    if (st.extraGlb) {
      const extraFile = st.extraGlb.split('/').pop() || `${st.id}_extra`;
      jobs.push({
        key: extraFile,
        url: `./${st.extraGlb}`,
        anchor: st.xiyuanAnchor || st.anchor,
        stationId: st.id,
        district,
        fallbackKind: 'garden',
        maxH: 22
      });
    }

    if (st.extraGlbs) {
      for (const eg of st.extraGlbs) {
        const extraFile = eg.split('/').pop() || `${st.id}_extra`;
        let anchor = st.anchor;
        if (eg.includes('shizilin') && st.shizilinAnchor) anchor = st.shizilinAnchor;
        if (eg.includes('suzhou_museum') && st.museumAnchor) anchor = st.museumAnchor;
        jobs.push({
          key: extraFile,
          url: `./${eg}`,
          anchor,
          stationId: st.id,
          district,
          fallbackKind: 'garden',
          maxH: 18
        });
      }
    }
  }
  return jobs;
}

function getEmissiveTag(std: THREE.MeshStandardMaterial): 'warm' | 'gold' | 'cyan' | 'accent' | 'none' {
  const n = (std.name || '').toLowerCase();
  if (n.includes('emissive_warm') || n.includes('lantern') || n.includes('eave_light')) return 'warm';
  if (n.includes('emissive_gold') || n.includes('gold_light') || n.includes('crown_light')) return 'gold';
  if (n.includes('emissive_cyan') || n.includes('cyan_light') || n.includes('led_blue')) return 'cyan';
  if (n.includes('emissive_accent') || n.includes('neon') || n.includes('magenta')) return 'accent';
  if (std.emissive && std.emissive.r + std.emissive.g + std.emissive.b > 0.15 && std.emissiveIntensity > 0.05) {
    if (std.emissive.b > std.emissive.r * 1.15) return 'cyan';
    if (std.emissive.r > 0.7 && std.emissive.b > 0.45) return 'accent';
    if (std.emissive.g > 0.72) return 'gold';
    return 'warm';
  }
  return 'none';
}

function isDescendantOf(obj: THREE.Object3D, ancestor: THREE.Object3D | null): boolean {
  if (!ancestor) return false;
  let cur: THREE.Object3D | null = obj;
  while (cur) {
    if (cur === ancestor) return true;
    cur = cur.parent;
  }
  return false;
}

/**
 * Normalize geometry to non-indexed (position, normal, color) with material's linear albedo
 * baked directly into vertex colors so dozens of differently colored materials merge into
 * just a handful of ultra-low-Draw-Call district batches with 100% identical visual color!
 */
function prepareForMergeWithColor(
  geo: THREE.BufferGeometry,
  worldMatrix: THREE.Matrix4,
  baseColor: THREE.Color
): THREE.BufferGeometry | null {
  const pos = geo.getAttribute('position');
  if (!pos || pos.count === 0) return null;

  const cloned = geo.index ? geo.toNonIndexed() : geo.clone();
  cloned.applyMatrix4(worldMatrix);

  if (!cloned.getAttribute('normal')) {
    cloned.computeVertexNormals();
  }

  const count = cloned.getAttribute('position').count;
  const existingColor = cloned.getAttribute('color');
  const colors = new Float32Array(count * 3);

  if (existingColor) {
    for (let i = 0; i < count; i++) {
      colors[i * 3] = existingColor.getX(i) * baseColor.r;
      colors[i * 3 + 1] = existingColor.getY(i) * baseColor.g;
      colors[i * 3 + 2] = existingColor.getZ(i) * baseColor.b;
    }
  } else {
    const r = baseColor.r;
    const g = baseColor.g;
    const b = baseColor.b;
    for (let i = 0; i < count; i++) {
      colors[i * 3] = r;
      colors[i * 3 + 1] = g;
      colors[i * 3 + 2] = b;
    }
  }

  // Keep only position, normal, color so mergeGeometries never mismatches attributes
  const keep = new Set(['position', 'normal']);
  for (const attrName of Object.keys(cloned.attributes)) {
    if (!keep.has(attrName)) {
      cloned.deleteAttribute(attrName);
    }
  }
  cloned.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  cloned.clearGroups();
  return cloned;
}

export async function loadAllLandmarks(
  layout: WorldLayout,
  atmosphere: AtmosphereManager,
  onProgress?: (loaded: number, total: number, label: string) => void
): Promise<LoadedLandmarks> {
  const loader = new GLTFLoader();
  const group = new THREE.Group();
  group.name = 'SuzhouLandmarks';

  const jobs = buildJobList(layout);
  const loadedModels: string[] = [];
  const missingModels: string[] = [];
  let ferrisWheelRotor: THREE.Object3D | null = null;
  let ferrisRotationAxis: 'x' | 'y' | 'z' = 'x';
  let completed = 0;

  // Vertex-colored per-district batches: collapses ~300 GLB primitives into ~18 total hero draw calls!
  const mergeBuckets = new Map<
    string,
    { material: THREE.MeshStandardMaterial; castShadow: boolean; geos: THREE.BufferGeometry[] }
  >();
  const unmergedObjects: THREE.Object3D[] = [];

  await Promise.all(
    jobs.map(async (job) => {
      let root: THREE.Object3D;
      try {
        const gltf = await loader.loadAsync(job.url);
        root = gltf.scene;
        root.name = `Landmark_${job.key}`;
        loadedModels.push(job.key);
      } catch {
        root = createFallbackSilhouette(job);
        missingModels.push(job.key);
      } finally {
        completed++;
        onProgress?.(completed, jobs.length, job.key);
      }

      root.position.set(job.anchor.x, job.anchor.y, job.anchor.z);
      root.updateMatrixWorld(true);

      let localRotor: THREE.Object3D | null = null;
      if (job.key.includes('moca_eye')) {
        root.traverse((obj) => {
          if (!localRotor && obj.name && obj.name.toLowerCase().includes('ferriswheelrotor')) {
            localRotor = obj;
          }
        });
      }

      if (localRotor) {
        const rotorObj = localRotor as THREE.Object3D;
        const worldPos = new THREE.Vector3();
        const worldQuat = new THREE.Quaternion();
        const worldScale = new THREE.Vector3();
        rotorObj.matrixWorld.decompose(worldPos, worldQuat, worldScale);

        const box = new THREE.Box3().setFromObject(rotorObj);
        const size = new THREE.Vector3();
        box.getSize(size);
        ferrisRotationAxis = size.x < size.z && size.x < size.y ? 'x' : 'z';

        rotorObj.removeFromParent();
        rotorObj.position.copy(worldPos);
        rotorObj.quaternion.copy(worldQuat);
        rotorObj.scale.copy(worldScale);
        rotorObj.traverse((c) => {
          const m = c as THREE.Mesh;
          if (m.isMesh) {
            m.castShadow = false;
            m.receiveShadow = true;
          }
        });
        ferrisWheelRotor = rotorObj;
        unmergedObjects.push(rotorObj);
      }

      root.traverse((obj) => {
        if (isDescendantOf(obj, localRotor)) return;
        const mesh = obj as THREE.Mesh;
        if (!mesh.isMesh || !mesh.geometry) return;

        const mat = Array.isArray(mesh.material) ? null : mesh.material;
        const std = mat && (mat as THREE.MeshStandardMaterial).isMeshStandardMaterial
          ? (mat as THREE.MeshStandardMaterial)
          : null;

        // Leave textured or non-standard meshes unmerged
        if (!std || std.map || std.normalMap || std.roughnessMap || std.metalnessMap || std.emissiveMap) {
          const cloneMesh = mesh.clone();
          cloneMesh.applyMatrix4(mesh.matrixWorld);
          cloneMesh.castShadow = true;
          cloneMesh.receiveShadow = true;
          unmergedObjects.push(cloneMesh);
          return;
        }

        const emTag = getEmissiveTag(std);
        const prepared = prepareForMergeWithColor(mesh.geometry, mesh.matrixWorld, std.color);
        if (!prepared) return;

        let key: string;
        let bucket = mergeBuckets.get('');

        if (emTag !== 'none') {
          // Emissive bucket: grouped by district + channel (never casts shadows!)
          key = `${job.district}|em|${emTag}`;
          bucket = mergeBuckets.get(key);
          if (!bucket) {
            const emMat = new THREE.MeshStandardMaterial({
              name: `Emissive_${emTag.charAt(0).toUpperCase() + emTag.slice(1)}_Batched_${job.district}`,
              color: '#ffffff',
              vertexColors: true,
              emissive: std.emissive.clone(),
              emissiveIntensity: Math.min(Math.max(std.emissiveIntensity || 1.0, 0.55), 1.2),
              roughness: 0.35,
              metalness: 0.1,
              toneMapped: true
            });
            bucket = { material: emMat, castShadow: false, geos: [] };
            mergeBuckets.set(key, bucket);
          }
        } else if (std.transparent && std.opacity < 0.96) {
          key = `${job.district}|trans|${Math.round(std.opacity * 10)}|${std.side}`;
          bucket = mergeBuckets.get(key);
          if (!bucket) {
            const transMat = new THREE.MeshStandardMaterial({
              name: `BatchedTrans_${job.district}`,
              color: '#ffffff',
              vertexColors: true,
              roughness: std.roughness,
              metalness: std.metalness,
              transparent: true,
              opacity: std.opacity,
              side: std.side
            });
            bucket = { material: transMat, castShadow: false, geos: [] };
            mergeBuckets.set(key, bucket);
          }
        } else {
          // Opaque non-emissive: 3 surface classes per district (glassMetal / waterGloss / matte)
          const surfaceClass =
            std.metalness > 0.35 ? 'glassMetal' : std.roughness < 0.35 ? 'waterGloss' : 'matte';
          key = `${job.district}|${surfaceClass}|${std.side}`;
          bucket = mergeBuckets.get(key);
          if (!bucket) {
            const sharedMat = new THREE.MeshStandardMaterial({
              name: `Batched_${job.district}_${surfaceClass}`,
              color: '#ffffff',
              vertexColors: true,
              roughness: surfaceClass === 'glassMetal' ? 0.22 : surfaceClass === 'waterGloss' ? 0.14 : 0.80,
              metalness: surfaceClass === 'glassMetal' ? 0.76 : surfaceClass === 'waterGloss' ? 0.08 : 0.06,
              side: std.side
            });
            bucket = {
              material: sharedMat,
              castShadow: surfaceClass !== 'waterGloss',
              geos: []
            };
            mergeBuckets.set(key, bucket);
          }
        }

        bucket.geos.push(prepared);
      });
    })
  );

  for (const [sig, bucket] of mergeBuckets.entries()) {
    if (bucket.geos.length === 0) continue;
    const mergedGeo = bucket.geos.length === 1 ? bucket.geos[0] : mergeGeometries(bucket.geos, false);
    for (const g of bucket.geos) {
      if (g !== mergedGeo) g.dispose();
    }
    if (!mergedGeo) continue;

    mergedGeo.computeBoundingSphere();
    const mergedMesh = new THREE.Mesh(mergedGeo, bucket.material);
    mergedMesh.name = `BatchedHero_${sig}`;
    mergedMesh.castShadow = bucket.castShadow;
    mergedMesh.receiveShadow = true;
    group.add(mergedMesh);
  }

  for (const obj of unmergedObjects) {
    group.add(obj);
  }

  atmosphere.registerEmissivesFromObject(group);

  return {
    group,
    loadedModels,
    missingModels,
    ferrisWheelRotor,
    ferrisRotationAxis
  };
}
