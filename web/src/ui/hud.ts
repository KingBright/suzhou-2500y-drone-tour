import type { AtmosphereMode, StationConfig, TelemetryStats, WorldLayout } from '../types/world';
import { ACT_LABELS, ATMOSPHERE_LABELS } from '../config/defaults';

export interface HudCallbacks {
  onSelectStation: (index1Based: number) => void;
  onSelectAtmosphere: (mode: AtmosphereMode) => void;
  onTogglePlay: () => void;
  onScrub: (progress: number) => void;
  onToggleFreeFly: () => void;
  onToggleLookDev: () => void;
  onToggleHideUI: () => void;
}

export class CinemaHUD {
  private readonly root: HTMLElement;
  private readonly layout: WorldLayout;
  private readonly cb: HudCallbacks;

  private actEl!: HTMLElement;
  private titleZhEl!: HTMLElement;
  private titleEnEl!: HTMLElement;
  private descEl!: HTMLElement;
  private stationBtns: HTMLButtonElement[] = [];
  private atmosBtns = new Map<AtmosphereMode, HTMLButtonElement>();
  private playBtn!: HTMLButtonElement;
  private freeFlyBtn!: HTMLButtonElement;
  private lookDevBtn!: HTMLButtonElement;
  private scrubber!: HTMLInputElement;
  private timecodeEl!: HTMLElement;
  private statsEl!: HTMLElement;
  private freeFlyHintEl!: HTMLElement;
  private lastStationId = '';
  private isScrubbing = false;

  constructor(root: HTMLElement, layout: WorldLayout, cb: HudCallbacks) {
    this.root = root;
    this.layout = layout;
    this.cb = cb;
    this.render();
  }

  private render(): void {
    const ancientStations = this.layout.stations.filter((s) => s.index <= 7);
    const modernStations = this.layout.stations.filter((s) => s.index >= 8);
    const modes: AtmosphereMode[] = ['auto', 'dawn', 'golden', 'dusk', 'night'];

    this.root.innerHTML = `
      <header class="hud-top">
        <div class="station-card glass">
          <div class="station-meta">
            <span class="act-badge" id="hud-act">第一幕 · 运河古韵</span>
            <span class="brand-tag">SUZHOU 2500Y FPV</span>
          </div>
          <h1 class="station-title-zh" id="hud-title-zh">寒山寺 & 枫桥</h1>
          <div class="station-title-en" id="hud-title-en">Hanshan Temple & Maple Bridge</div>
          <p class="station-desc" id="hud-desc">低空贴大运河水面高速向东北拉升</p>
        </div>

        <div class="controls-cluster">
          <div class="atmos-bar glass" role="group" aria-label="天光模式">
            ${modes
              .map(
                (m) =>
                  `<button class="pill-btn atmos-btn ${m === 'auto' ? 'active' : ''}" data-mode="${m}">${ATMOSPHERE_LABELS[m]}</button>`
              )
              .join('')}
          </div>
          <div class="action-bar glass">
            <button class="pill-btn" id="hud-freefly" title="切换自由飞行 (F)">自动巡航</button>
            <button class="pill-btn" id="hud-lookdev" title="Look-Dev 参数面板 (G)">G 调参</button>
            <button class="pill-btn ghost" id="hud-hide" title="隐藏全部 UI (H)">H 纯净</button>
          </div>
        </div>
      </header>

      <div class="freefly-hint glass hidden" id="hud-freefly-hint">
        自由飞行模式：<strong>W A S D</strong> 移动 · <strong>Q / E</strong> 升降 · <strong>Shift</strong> 加速 · <strong>鼠标拖拽</strong> 环视 · 按 <strong>F</strong> 返回航线
      </div>

      <footer class="hud-bottom">
        <div class="station-dock glass">
          <div class="station-group">
            <span class="group-label ancient">古韵姑苏</span>
            <div class="station-pills">
              ${ancientStations
                .map(
                  (s) =>
                    `<button class="st-btn" data-index="${s.index}" title="${s.nameZh} (${s.nameEn})"><span class="st-num">${String(s.index).padStart(2, '0')}</span><span class="st-name">${this.shortName(s)}</span></button>`
                )
                .join('')}
            </div>
          </div>
          <div class="dock-divider"></div>
          <div class="station-group">
            <span class="group-label modern">现代金鸡湖</span>
            <div class="station-pills">
              ${modernStations
                .map(
                  (s) =>
                    `<button class="st-btn" data-index="${s.index}" title="${s.nameZh} (${s.nameEn})"><span class="st-num">${String(s.index).padStart(2, '0')}</span><span class="st-name">${this.shortName(s)}</span></button>`
                )
                .join('')}
            </div>
          </div>
        </div>

        <div class="transport-bar glass">
          <button class="play-btn" id="hud-play" title="播放 / 暂停 (Space)">❚❚</button>
          <input type="range" class="scrubber" id="hud-scrubber" min="0" max="1000" value="0" aria-label="航线进度" />
          <span class="timecode" id="hud-timecode">00:00 / 01:55</span>
          <div class="stats-pill" id="hud-stats">60 FPS · 0 Calls · 0K Tris · 3 Lights</div>
        </div>
      </footer>
    `;

    this.actEl = this.root.querySelector('#hud-act')!;
    this.titleZhEl = this.root.querySelector('#hud-title-zh')!;
    this.titleEnEl = this.root.querySelector('#hud-title-en')!;
    this.descEl = this.root.querySelector('#hud-desc')!;
    this.playBtn = this.root.querySelector('#hud-play')!;
    this.freeFlyBtn = this.root.querySelector('#hud-freefly')!;
    this.lookDevBtn = this.root.querySelector('#hud-lookdev')!;
    this.scrubber = this.root.querySelector('#hud-scrubber')!;
    this.timecodeEl = this.root.querySelector('#hud-timecode')!;
    this.statsEl = this.root.querySelector('#hud-stats')!;
    this.freeFlyHintEl = this.root.querySelector('#hud-freefly-hint')!;

    this.stationBtns = Array.from(this.root.querySelectorAll<HTMLButtonElement>('.st-btn'));
    for (const btn of this.stationBtns) {
      btn.addEventListener('click', () => {
        const idx = Number(btn.dataset.index || '1');
        this.cb.onSelectStation(idx);
      });
    }

    const atmosNodes = this.root.querySelectorAll<HTMLButtonElement>('.atmos-btn');
    atmosNodes.forEach((btn) => {
      const mode = btn.dataset.mode as AtmosphereMode;
      this.atmosBtns.set(mode, btn);
      btn.addEventListener('click', () => this.cb.onSelectAtmosphere(mode));
    });

    this.playBtn.addEventListener('click', () => this.cb.onTogglePlay());
    this.freeFlyBtn.addEventListener('click', () => this.cb.onToggleFreeFly());
    this.lookDevBtn.addEventListener('click', () => this.cb.onToggleLookDev());
    this.root.querySelector('#hud-hide')!.addEventListener('click', () => this.cb.onToggleHideUI());

    this.scrubber.addEventListener('pointerdown', () => {
      this.isScrubbing = true;
    });
    this.scrubber.addEventListener('pointerup', () => {
      this.isScrubbing = false;
    });
    this.scrubber.addEventListener('input', () => {
      this.cb.onScrub(Number(this.scrubber.value) / 1000);
    });
  }

  private shortName(s: StationConfig): string {
    const map: Record<string, string> = {
      '01-hanshan': '寒山枫桥',
      '02-xiyuan-tigerhill': '西园虎丘',
      '03-lingering': '留园',
      '04-panmen-canglang': '盘门沧浪',
      '05-wangshi-twintowers': '网师双塔',
      '06-beisi-pingjiang': '北寺平江',
      '07-gardens-museum': '拙政苏博',
      '08-gate-of-orient': '东方之门',
      '09-ligongdi': '李公堤',
      '10-moca-eye': '苏州之眼',
      '11-arts-centre': '文艺中心',
      '12-suzhou-ifs': '国金450m'
    };
    return map[s.id] || s.nameZh;
  }

  public update(stats: TelemetryStats, paused: boolean, lookDevOpen: boolean): void {
    const st = this.layout.stations[Math.min(Math.max(stats.currentStation - 1, 0), this.layout.stations.length - 1)];

    if (st && st.id !== this.lastStationId) {
      this.lastStationId = st.id;
      const actInfo = ACT_LABELS[st.act] || ACT_LABELS[1];
      this.actEl.textContent = actInfo.zh;
      this.titleZhEl.textContent = st.nameZh;
      this.titleEnEl.textContent = st.nameEn;
      this.descEl.textContent = st.transitionToNext;

      for (const btn of this.stationBtns) {
        btn.classList.toggle('active', Number(btn.dataset.index) === st.index);
      }
    }

    for (const [m, btn] of this.atmosBtns.entries()) {
      btn.classList.toggle('active', m === stats.atmosphereMode);
    }

    this.playBtn.textContent = paused ? '▶' : '❚❚';
    this.freeFlyBtn.textContent = stats.freeFly ? '自由飞行中' : '自动巡航';
    this.freeFlyBtn.classList.toggle('active', stats.freeFly);
    this.lookDevBtn.classList.toggle('active', lookDevOpen);
    this.freeFlyHintEl.classList.toggle('hidden', !stats.freeFly);

    if (!this.isScrubbing) {
      this.scrubber.value = String(Math.round(stats.progress * 1000));
    }

    const totalSec = 115;
    const curSec = Math.floor(stats.progress * totalSec);
    const mm = String(Math.floor(curSec / 60)).padStart(2, '0');
    const ss = String(curSec % 60).padStart(2, '0');
    this.timecodeEl.textContent = `${mm}:${ss} / 01:55`;

    const trisK = (stats.triangles / 1000).toFixed(0);
    this.statsEl.textContent = `${stats.fps} FPS · ${stats.drawCalls} Calls · ${trisK}K Tris · ${stats.activeLights} Lights`;
  }
}
