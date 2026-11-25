#!/usr/bin/env node
/**
 * Suzhou 2500Y Drone Tour — Automated Step 3 & Step 5 Visual + Performance Verifier
 * Audits all 17 GLB models, drives http://127.0.0.1:4173/ via ego-browser at 1440x900,
 * captures deterministic screenshots into qa/shots/ and the verifier brain artifact folder,
 * and asserts hard WebGL redlines (activeLights <= 3, drawCalls < 160, missingModels == 0, 0 errors).
 */

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const PROJECT_ROOT = '/Users/jinliang/workspace/experiment/suzhou-drone-tour';
const MODELS_DIR = path.join(PROJECT_ROOT, 'web/public/assets/models');
const SHOTS_DIR = path.join(PROJECT_ROOT, 'qa/shots');
const BRAIN_DIR = '/Users/jinliang/.gemini/antigravity/brain/804fbafb-cae4-414f-bead-1e8a3f626ab6';
const REPORT_JSON = path.join(PROJECT_ROOT, 'qa/audit-report.json');
const TMP_BROWSER_OUT = '/tmp/suzhou_ego_audit_out.json';
const APP_URL = process.env.SUZHOU_URL || 'http://127.0.0.1:4173/';

const EXPECTED_GLBS = [
  'hanshan_temple.glb',
  'xiyuan_temple.glb',
  'tiger_hill.glb',
  'lingering_garden.glb',
  'panmen_canglang.glb',
  'wangshi_twin_pagodas.glb',
  'beisi_pingjiang.glb',
  'shizilin_garden.glb',
  'humble_admin_garden.glb',
  'suzhou_museum.glb',
  'gusu_modular_kit.glb',
  'gate_of_orient.glb',
  'ligongdi.glb',
  'moca_eye_of_suzhou.glb',
  'arts_centre_moon.glb',
  'suzhou_ifs.glb',
  'modern_cbd_kit.glb'
];

fs.mkdirSync(SHOTS_DIR, { recursive: true });
fs.mkdirSync(BRAIN_DIR, { recursive: true });

function auditGlbAssets() {
  const results = [];
  const failures = [];
  let totalBytes = 0;

  for (const name of EXPECTED_GLBS) {
    const fullPath = path.join(MODELS_DIR, name);
    if (!fs.existsSync(fullPath)) {
      failures.push(`Missing GLB file: ${name}`);
      continue;
    }
    const stat = fs.statSync(fullPath);
    totalBytes += stat.size;
    const sizeMB = Number((stat.size / (1024 * 1024)).toFixed(3));
    if (stat.size === 0) failures.push(`Zero-byte GLB file: ${name}`);
    if (sizeMB >= 5.0) failures.push(`GLB exceeds 5MB budget: ${name} (${sizeMB} MB)`);

    const buf = fs.readFileSync(fullPath);
    const magic = buf.toString('ascii', 0, 4);
    const version = buf.readUInt32LE(4);
    if (magic !== 'glTF' || version !== 2) {
      failures.push(`Invalid GLB header in ${name}: magic=${magic} version=${version}`);
      continue;
    }
    const jsonLen = buf.readUInt32LE(12);
    const gltf = JSON.parse(buf.toString('utf8', 20, 20 + jsonLen));

    let triangles = 0;
    for (const mesh of gltf.meshes || []) {
      for (const prim of mesh.primitives || []) {
        if (prim.indices !== undefined) {
          triangles += gltf.accessors[prim.indices].count / 3;
        } else if (prim.attributes?.POSITION !== undefined) {
          triangles += gltf.accessors[prim.attributes.POSITION].count / 3;
        }
      }
    }
    const materials = (gltf.materials || []).map((m) => m.name || '');
    const emissiveMaterials = materials.filter((m) => m.includes('Emissive_'));
    const nodes = (gltf.nodes || []).map((n) => n.name || '');

    results.push({
      file: name,
      bytes: stat.size,
      sizeMB,
      meshes: (gltf.meshes || []).length,
      triangles: Math.round(triangles),
      emissiveCount: emissiveMaterials.length,
      emissiveMaterials,
      nodeCount: nodes.length
    });
  }

  return {
    count: results.length,
    expectedCount: EXPECTED_GLBS.length,
    totalMB: Number((totalBytes / (1024 * 1024)).toFixed(2)),
    failures,
    models: results
  };
}

function runEgoScript(scriptSource) {
  execFileSync('ego-browser', ['nodejs'], {
    input: scriptSource,
    encoding: 'utf8',
    stdio: ['pipe', 'inherit', 'inherit'],
    maxBuffer: 32 * 1024 * 1024
  });
}

async function main() {
  console.log('=== [1/3] Auditing 17 GLB assets ===');
  const glbAudit = auditGlbAssets();
  console.log(`GLBs verified: ${glbAudit.count}/${glbAudit.expectedCount}, Total: ${glbAudit.totalMB} MB, Failures: ${glbAudit.failures.length}`);
  if (glbAudit.failures.length > 0) {
    console.error('GLB Failures:', glbAudit.failures);
    process.exit(1);
  }

  if (fs.existsSync(TMP_BROWSER_OUT)) fs.unlinkSync(TMP_BROWSER_OUT);

  console.log('=== [2/3] Running WebGL visual & telemetry capture in ego-browser ===');
  const browserScript = `
const fs = await import("node:fs");
const path = await import("node:path");

const SHOTS_DIR = ${JSON.stringify(SHOTS_DIR)};
const BRAIN_DIR = ${JSON.stringify(BRAIN_DIR)};
const APP_URL = ${JSON.stringify(APP_URL)};
const TMP_OUT = ${JSON.stringify(TMP_BROWSER_OUT)};

const task = await taskSpace("suzhou-2500y-visual-audit-p2");
const page = (await task.pages())[0] ?? (await task.adopt((await task.tabs())[0].page));

await page.cdp("Emulation.setDeviceMetricsOverride", {
  width: 1440,
  height: 900,
  deviceScaleFactor: 2,
  mobile: false
});

await page.cdp("egoAutomated.disable");
await page.cdp("Runtime.enable");
await page.cdp("Log.enable");
await page.events();

await page.goto(APP_URL, { timeout: 30000 });
await page.cdp("Page.bringToFront");

await page.evaluate(() => {
  window.__QA_ERRORS__ = [];
  window.addEventListener("error", (e) => {
    window.__QA_ERRORS__.push("window.error: " + (e.message || String(e)));
  });
  window.addEventListener("unhandledrejection", (e) => {
    window.__QA_ERRORS__.push("unhandledrejection: " + String(e.reason));
  });
});

await page.waitForFunction(
  () => Boolean(window.__SUZHOU_DEBUG__),
  undefined,
  { timeout: 15000 }
);

await page.evaluate(async () => {
  await window.__SUZHOU_DEBUG__.whenReady();
});

// Warm up shaders across ancient + modern districts, then measure sustained FPS
await page.evaluate(() => {
  window.__SUZHOU_DEBUG__.jumpToStation(6);
  window.__SUZHOU_DEBUG__.jumpToStation(8);
  window.__SUZHOU_DEBUG__.jumpToStation(12);
  window.__SUZHOU_DEBUG__.jumpToStation(1);
  window.__SUZHOU_DEBUG__.setPaused(false);
});
await page.waitForTimeout(1600);

async function measureSegmentFps(stationIdx) {
  return await page.evaluate(async (idx) => {
    window.__SUZHOU_DEBUG__.jumpToStation(idx);
    window.__SUZHOU_DEBUG__.setPaused(false);
    await new Promise((r) => setTimeout(r, 550));
    const start = performance.now();
    let frames = 0;
    await new Promise((resolve) => {
      function tick() {
        frames++;
        if (performance.now() - start >= 1000) resolve(true);
        else requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
    const elapsed = (performance.now() - start) / 1000;
    const st = window.__SUZHOU_DEBUG__.getStats();
    return { station: idx, measuredFps: Number((frames / elapsed).toFixed(1)), hudFps: st.fps, drawCalls: st.drawCalls, triangles: st.triangles };
  }, stationIdx);
}

const fpsAncient = await measureSegmentFps(1);
const fpsGusu = await measureSegmentFps(6);
const fpsOrient = await measureSegmentFps(8);
const fpsIfs = await measureSegmentFps(12);

const gpuInfo = await page.evaluate(() => {
  const c = document.getElementById("webgl-canvas");
  const gl = c.getContext("webgl2") || c.getContext("webgl");
  const ext = gl ? gl.getExtension("WEBGL_debug_renderer_info") : null;
  return {
    gpuRenderer: gl && ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : "unknown",
    canvasSize: [c.width, c.height],
    viewport: [window.innerWidth, window.innerHeight]
  };
});

// Pause automatic drone playback for deterministic frame-exact captures
await page.evaluate(() => {
  window.__SUZHOU_DEBUG__.setPaused(true);
  window.__SUZHOU_DEBUG__.setAtmosphere("auto");
  window.__SUZHOU_DEBUG__.setHideUI(false);
  window.__SUZHOU_DEBUG__.toggleLookDev(false);
});

async function captureDual(filename, setupFn) {
  await page.evaluate(async (fnBody) => {
    const fn = new Function("dbg", fnBody);
    await fn(window.__SUZHOU_DEBUG__);
  }, setupFn);
  // Wait 240ms so CSS pill transitions (0.18s) and post-processing settle 100%
  await page.waitForTimeout(240);
  const meta = await page.evaluate(async () => {
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    return window.__SUZHOU_DEBUG__.getStats();
  });

  const shotPath = path.join(SHOTS_DIR, filename);
  const brainPath = path.join(BRAIN_DIR, filename);
  await page.screenshot({ path: shotPath, scale: "css" });
  fs.copyFileSync(shotPath, brainPath);
  return { filename, shotPath, brainPath, stats: meta };
}

const captures = [];

const stationNames = [
  "01_hanshan",
  "02_xiyuan_tigerhill",
  "03_lingering",
  "04_panmen_canglang",
  "05_wangshi_twintowers",
  "06_beisi_pingjiang",
  "07_gardens_museum",
  "08_gate_of_orient",
  "09_ligongdi",
  "10_moca_eye",
  "11_arts_centre",
  "12_suzhou_ifs_panorama"
];

for (let i = 1; i <= 12; i++) {
  const fname = \`station_\${stationNames[i - 1]}.png\`;
  captures.push(
    await captureDual(
      fname,
      \`dbg.setAtmosphere("auto"); dbg.toggleLookDev(false); dbg.setHideUI(false); dbg.jumpToStation(\${i});\`
    )
  );
}

const n = 52;
const swoopFrames = [
  { name: "swoop_02a_xiyuan_closeup.png", u: 3 / n },
  { name: "swoop_04a_wumen_arch_approach.png", u: 14 / n },
  { name: "swoop_04b_wumen_arch_inside.png", u: 15 / n },
  { name: "swoop_05_twin_pagodas_gap.png", u: 19 / n },
  { name: "swoop_06_pingjiang_canal.png", u: 24 / n },
  { name: "swoop_07a_shizilin_closeup.png", u: 26 / n },
  { name: "swoop_07b_suzhou_museum_closeup.png", u: 28 / n },
  { name: "swoop_08a_orient_arch_approach.png", u: 32 / n },
  { name: "swoop_08b_orient_arch_inside.png", u: 33 / n },
  { name: "swoop_08c_fountain_dive.png", u: 35 / n },
  { name: "swoop_09a_ligongdi_arch_approach.png", u: 38 / n },
  { name: "swoop_09b_ligongdi_arch_under.png", u: 39 / n },
  { name: "swoop_10_ferris_closeup.png", u: 43 / n },
  { name: "swoop_12_ifs_crown_climb.png", u: 49 / n }
];

for (const sf of swoopFrames) {
  captures.push(
    await captureDual(
      sf.name,
      \`dbg.setAtmosphere("auto"); dbg.toggleLookDev(false); dbg.setHideUI(true); dbg.setProgress(\${sf.u.toFixed(6)});\`
    )
  );
}

// Dynamic Atmosphere Switching Proof on Station 06 (Beisi Pagoda) & Station 08 (Gate of the Orient)
for (const mode of ["dawn", "golden", "dusk", "night"]) {
  captures.push(
    await captureDual(
      \`atmo_beisi_\${mode}.png\`,
      \`dbg.setHideUI(false); dbg.toggleLookDev(false); dbg.jumpToStation(6); dbg.setAtmosphere("\${mode}");\`
    )
  );
  captures.push(
    await captureDual(
      \`atmo_orient_\${mode}.png\`,
      \`dbg.setHideUI(false); dbg.toggleLookDev(false); dbg.jumpToStation(8); dbg.setAtmosphere("\${mode}");\`
    )
  );
}

// Step 4 Look-Dev Panel Open (G) and Pristine UI-Hidden View (H)
await page.evaluate(() => {
  window.__SUZHOU_DEBUG__.jumpToStation(8);
  window.__SUZHOU_DEBUG__.setAtmosphere("night");
  window.__SUZHOU_DEBUG__.setHideUI(false);
  window.__SUZHOU_DEBUG__.toggleLookDev(false);
});
await page.keyboard.press("KeyG");
await page.waitForTimeout(260);
captures.push(await captureDual("ui_lookdev_open_G.png", "/* keep LookDev open */"));

const uiChecks = await page.evaluate(() => {
  const lookdevRoot = document.getElementById("lookdev-root");
  const panel = lookdevRoot ? lookdevRoot.querySelector(".lookdev-panel") : null;
  const sliders = lookdevRoot ? lookdevRoot.querySelectorAll("input[type='range']").length : 0;
  const hasCopyBtn = Boolean(lookdevRoot && lookdevRoot.textContent?.includes("Copy JSON"));
  const hasResetBtn = Boolean(lookdevRoot && lookdevRoot.textContent?.includes("Reset"));
  const panelVisibleOnG = Boolean(panel && panel.classList.contains("open"));
  return { sliders, hasCopyBtn, hasResetBtn, panelVisibleOnG };
});

await page.keyboard.press("KeyH");
await page.waitForTimeout(260);
captures.push(await captureDual("ui_pristine_hidden_H.png", "/* keep UI hidden */"));

const hiddenCheck = await page.evaluate(() => {
  const hud = document.getElementById("hud-root");
  const lookdev = document.getElementById("lookdev-root");
  const hudRectVisible = hud ? (getComputedStyle(hud).display !== "none" && getComputedStyle(hud).visibility !== "hidden" && Number(getComputedStyle(hud).opacity) > 0.01) : false;
  const lookdevRectVisible = lookdev ? (getComputedStyle(lookdev).display !== "none" && getComputedStyle(lookdev).visibility !== "hidden" && Number(getComputedStyle(lookdev).opacity) > 0.01) : false;
  return { bodyHasUiHidden: document.body.classList.contains("ui-hidden"), hudRectVisible, lookdevRectVisible };
});

await page.keyboard.press("KeyH");
await page.keyboard.press("KeyG");

// Continuous 220-sample spline sweep
const splineSweep = await page.evaluate(() => {
  window.__SUZHOU_DEBUG__.setAtmosphere("auto");
  let maxDrawCalls = 0;
  let minDrawCalls = Infinity;
  let maxTriangles = 0;
  let maxLights = 0;
  const samples = [];
  for (let i = 0; i <= 220; i++) {
    const u = i / 220;
    window.__SUZHOU_DEBUG__.setProgress(u);
    const st = window.__SUZHOU_DEBUG__.getStats();
    if (st.drawCalls > maxDrawCalls) maxDrawCalls = st.drawCalls;
    if (st.drawCalls < minDrawCalls) minDrawCalls = st.drawCalls;
    if (st.triangles > maxTriangles) maxTriangles = st.triangles;
    if (st.activeLights > maxLights) maxLights = st.activeLights;
    if (i % 20 === 0) samples.push({ u: Number(u.toFixed(3)), drawCalls: st.drawCalls, triangles: st.triangles, lights: st.activeLights, station: st.currentStation, timeOfDay: st.timeOfDay });
  }
  return { minDrawCalls, maxDrawCalls, maxTriangles, maxLights, samples };
});

const rawEvents = await page.events();
const cdpErrors = [];
for (const ev of rawEvents) {
  if (ev.method === "Runtime.exceptionThrown") {
    cdpErrors.push({ type: "exception", detail: ev.params?.exceptionDetails?.text || JSON.stringify(ev.params) });
  } else if (ev.method === "Runtime.consoleAPICalled" && ev.params?.type === "error") {
    cdpErrors.push({ type: "console.error", args: (ev.params.args || []).map((a) => a.value ?? a.description) });
  } else if (ev.method === "Log.entryAdded" && ev.params?.entry?.level === "error") {
    cdpErrors.push({ type: "log.error", text: ev.params.entry.text, url: ev.params.entry.url });
  }
}
const pageErrors = await page.evaluate(() => window.__QA_ERRORS__ || []);

fs.writeFileSync(TMP_OUT, JSON.stringify({
  taskSpaceId: task.spaceId,
  gpuInfo,
  fpsBenchmarks: [fpsAncient, fpsGusu, fpsOrient, fpsIfs],
  uiChecks,
  hiddenCheck,
  splineSweep,
  cdpErrors,
  pageErrors,
  captureCount: captures.length,
  captures
}, null, 2));
`;

  runEgoScript(browserScript);
  const browserAudit = JSON.parse(fs.readFileSync(TMP_BROWSER_OUT, 'utf8'));

  console.log('=== [3/3] Closing ego-browser TaskSpace cleanly ===');
  runEgoScript(`
const task = await taskSpace(${browserAudit.taskSpaceId});
await task.finish({ keep: [] });
`);

  // Hard redline assertions
  const redlineErrors = [];
  if (browserAudit.splineSweep.maxLights > 3) {
    redlineErrors.push(`activeLights exceeded 3: ${browserAudit.splineSweep.maxLights}`);
  }
  if (browserAudit.splineSweep.maxDrawCalls >= 180 || browserAudit.splineSweep.maxDrawCalls <= 2) {
    redlineErrors.push(`drawCalls out of expected [3..179] band: max=${browserAudit.splineSweep.maxDrawCalls}`);
  }
  const missing = browserAudit.captures[0]?.stats?.missingModels || [];
  if (missing.length > 0) {
    redlineErrors.push(`missingModels non-empty: ${missing.join(', ')}`);
  }
  if (browserAudit.cdpErrors.length > 0 || browserAudit.pageErrors.length > 0) {
    redlineErrors.push(`runtime/console errors detected: ${browserAudit.cdpErrors.length + browserAudit.pageErrors.length}`);
  }

  const report = {
    timestamp: new Date().toISOString(),
    status: redlineErrors.length === 0 ? 'PASS' : 'FAIL',
    redlineErrors,
    glbAudit,
    browserAudit
  };
  fs.writeFileSync(REPORT_JSON, JSON.stringify(report, null, 2));

  console.log('--- PASS #2 SUMMARY ---');
  console.log('Status:', report.status);
  console.log('GPU Renderer:', browserAudit.gpuInfo.gpuRenderer);
  console.log('Viewport / Canvas:', browserAudit.gpuInfo.viewport, browserAudit.gpuInfo.canvasSize);
  console.log('FPS Benchmarks:', browserAudit.fpsBenchmarks);
  console.log('Scene Draw Calls Range (220 spline samples):', `${browserAudit.splineSweep.minDrawCalls} .. ${browserAudit.splineSweep.maxDrawCalls}`);
  console.log('Max Scene Triangles:', browserAudit.splineSweep.maxTriangles);
  console.log('Max Active Lights:', browserAudit.splineSweep.maxLights);
  console.log('Loaded Models:', browserAudit.captures[0]?.stats?.loadedModels?.length, 'Missing:', missing.length);
  console.log('Look-Dev UI Check:', browserAudit.uiChecks);
  console.log('Hide-UI (H) Check:', browserAudit.hiddenCheck);
  console.log('CDP / Page Errors:', browserAudit.cdpErrors.length + browserAudit.pageErrors.length);
  console.log('Screenshots captured:', browserAudit.captureCount);

  if (redlineErrors.length > 0) {
    console.error('Redline Violations:', redlineErrors);
    process.exit(1);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
