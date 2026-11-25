#!/usr/bin/env node
/**
 * Deterministic 30fps HD Cinema Video Renderer for Suzhou 2500Y Drone Tour.
 * Steps WebGL simulation at exact dt = 1/30s via ego-browser CDP and pipes
 * JPEG frames straight into ffmpeg H.264 MP4 (yuv420p + faststart).
 */

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync, spawn } from 'node:child_process';

const PROJECT_ROOT = path.resolve(import.meta.dirname, '..');
const WEB_DIR = path.join(PROJECT_ROOT, 'web');
const OUT_DIR = path.join(PROJECT_ROOT, 'qa/recordings');
const OUT_MP4 = path.join(OUT_DIR, 'suzhou-2500y-drone-tour-720p.mp4');
const PORT = Number(process.env.PORT || 4179);
const APP_URL = `http://127.0.0.1:${PORT}/`;
const WIDTH = 1280;
const HEIGHT = 720;
const FPS = 30;
const SPEED_SCALE = 1.65; // ~70s tight cinematic pacing across all 12 stations

fs.mkdirSync(OUT_DIR, { recursive: true });

function waitForServer(url, timeoutMs = 15000) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const check = async () => {
      try {
        const res = await fetch(url);
        if (res.ok) return resolve();
      } catch {}
      if (Date.now() - start > timeoutMs) {
        return reject(new Error(`Preview server failed to start at ${url}`));
      }
      setTimeout(check, 250);
    };
    check();
  });
}

async function main() {
  console.log(`>>> [1/3] Starting Vite preview server on ${APP_URL}...`);
  const server = spawn('npx', ['vite', 'preview', '--host', '127.0.0.1', '--port', String(PORT), '--strictPort'], {
    cwd: WEB_DIR,
    stdio: ['ignore', 'pipe', 'pipe']
  });

  try {
    await waitForServer(APP_URL);
    console.log(`>>> [2/3] Capturing deterministic ${WIDTH}x${HEIGHT} @ ${FPS}fps frames into ${OUT_MP4}...`);

    const browserScript = `
const { spawn } = await import("node:child_process");
const fs = await import("node:fs");

const APP_URL = ${JSON.stringify(APP_URL)};
const OUT_MP4 = ${JSON.stringify(OUT_MP4)};
const WIDTH = ${WIDTH};
const HEIGHT = ${HEIGHT};
const FPS = ${FPS};
const SPEED_SCALE = ${SPEED_SCALE};

const task = await taskSpace("suzhou-2500y-video-render");
const page = (await task.pages())[0] ?? (await task.adopt((await task.tabs())[0].page));

await page.cdp("Emulation.setDeviceMetricsOverride", {
  width: WIDTH,
  height: HEIGHT,
  deviceScaleFactor: 1,
  mobile: false
});
await page.cdp("egoAutomated.disable");
await page.goto(APP_URL, { timeout: 30000 });
await page.cdp("Page.bringToFront");

await page.waitForFunction(() => Boolean(window.__SUZHOU_DEBUG__), undefined, { timeout: 15000 });
await page.evaluate(async () => {
  await window.__SUZHOU_DEBUG__.whenReady();
});

// Warm up shaders across ancient + modern districts
await page.evaluate(() => {
  const dbg = window.__SUZHOU_DEBUG__;
  dbg.setHideUI(false);
  dbg.toggleLookDev(false);
  dbg.setAtmosphere("auto");
  dbg.jumpToStation(6);
  dbg.jumpToStation(8);
  dbg.jumpToStation(12);
  dbg.setProgress(0.0);
  dbg.setPaused(false);
  dbg.setCaptureMode(true);
});
await page.waitForTimeout(450);

// Hide only the tiny top-right control cluster & telemetry pill during film export,
// while keeping the sleek top-left station title card and bottom 12-station tracker!
await page.evaluate(() => {
  const style = document.createElement("style");
  style.textContent = \`
    .hud-top-right, .stats-pill, #loading-overlay { display: none !important; }
    .hud-top-left { transition: none !important; }
  \`;
  document.head.appendChild(style);
});

const ffmpeg = spawn("ffmpeg", [
  "-y",
  "-f", "image2pipe",
  "-vcodec", "mjpeg",
  "-framerate", String(FPS),
  "-i", "-",
  "-c:v", "libx264",
  "-preset", "medium",
  "-crf", "19",
  "-pix_fmt", "yuv420p",
  "-movflags", "+faststart",
  OUT_MP4
], { stdio: ["pipe", "ignore", "pipe"] });

let ffmpegStderr = "";
ffmpeg.stderr.on("data", (d) => { ffmpegStderr += d.toString(); });
const ffmpegDone = new Promise((resolve, reject) => {
  ffmpeg.on("close", (code) => {
    if (code === 0) resolve();
    else reject(new Error("ffmpeg exited with code " + code + "\\n" + ffmpegStderr.slice(-1500)));
  });
});

async function writeFrame(buf) {
  if (!ffmpeg.stdin.write(buf)) {
    await new Promise((r) => ffmpeg.stdin.once("drain", r));
  }
}

const dt = 1 / FPS;
let simTime = 0;
let frameIdx = 0;
const maxFrames = FPS * 95;
let lastProgress = 0;
let reachedEnd = false;

// 1.5s graceful opening hold on Station 01 Hanshan Temple & Maple Bridge
await page.evaluate(() => window.__SUZHOU_DEBUG__.setPaused(true));
for (let i = 0; i < Math.round(FPS * 1.2); i++) {
  simTime += dt;
  await page.evaluate(([d, t, s]) => window.__SUZHOU_DEBUG__.stepFrame(d, t, s), [dt, simTime, SPEED_SCALE]);
  const shot = await page.cdp("Page.captureScreenshot", { format: "jpeg", quality: 92 });
  await writeFrame(Buffer.from(shot.data, "base64"));
  frameIdx++;
}

// Continuous 12-station drone flight with speed-ramp swoops & dynamic sky morph
await page.evaluate(() => window.__SUZHOU_DEBUG__.setPaused(false));
while (frameIdx < maxFrames) {
  simTime += dt;
  const st = await page.evaluate(([d, t, s]) => window.__SUZHOU_DEBUG__.stepFrame(d, t, s), [dt, simTime, SPEED_SCALE]);
  const shot = await page.cdp("Page.captureScreenshot", { format: "jpeg", quality: 92 });
  await writeFrame(Buffer.from(shot.data, "base64"));
  frameIdx++;

  if (frameIdx % 150 === 0) {
    console.log(\`[render] frame=\${frameIdx} progress=\${(st.progress * 100).toFixed(1)}% station=\${st.currentStation} (\${st.currentStationName})\`);
  }

  // Detect wrap-around or completion near 1.0
  if (lastProgress > 0.96 && (st.progress < 0.1 || st.progress >= 0.999)) {
    reachedEnd = true;
    break;
  }
  lastProgress = st.progress;
}

// 2.5s majestic finale hold at 450m Suzhou IFS panorama looking back west across 2500 years
await page.evaluate(() => {
  window.__SUZHOU_DEBUG__.setProgress(0.9985);
  window.__SUZHOU_DEBUG__.setPaused(true);
});
for (let i = 0; i < Math.round(FPS * 2.5); i++) {
  simTime += dt;
  await page.evaluate(([d, t, s]) => window.__SUZHOU_DEBUG__.stepFrame(d, t, s), [dt, simTime, SPEED_SCALE]);
  const shot = await page.cdp("Page.captureScreenshot", { format: "jpeg", quality: 92 });
  await writeFrame(Buffer.from(shot.data, "base64"));
  frameIdx++;
}

ffmpeg.stdin.end();
await ffmpegDone;

await task.finish({ keep: [] });
console.log(\`[render] DONE! frames=\${frameIdx} duration=\${(frameIdx / FPS).toFixed(1)}s reachedEnd=\${reachedEnd}\`);
`;

    execFileSync('ego-browser', ['nodejs'], {
      input: browserScript,
      encoding: 'utf8',
      stdio: ['pipe', 'inherit', 'inherit'],
      maxBuffer: 32 * 1024 * 1024
    });

    console.log(`>>> [3/3] Video rendered successfully: ${OUT_MP4}`);
  } finally {
    server.kill('SIGTERM');
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
