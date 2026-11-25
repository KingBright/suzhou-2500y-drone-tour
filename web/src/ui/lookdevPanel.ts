import type { AtmosphereMode, LookDevState } from '../types/world';
import { ATMOSPHERE_LABELS } from '../config/defaults';

export interface LookDevCallbacks {
  onAtmosphereMode: (mode: AtmosphereMode) => void;
  onTimeOfDayScrub: (t: number) => void;
  onManualOverride: (group: 'lights' | 'fog' | 'water') => void;
  onResetDefaults: () => void;
}

export class LookDevPanel {
  private readonly root: HTMLElement;
  private readonly state: LookDevState;
  private readonly cb: LookDevCallbacks;
  public open = false;

  private panelEl!: HTMLElement;
  private toastEl!: HTMLElement;
  private syncInputs: Array<() => void> = [];

  constructor(root: HTMLElement, state: LookDevState, cb: LookDevCallbacks) {
    this.root = root;
    this.state = state;
    this.cb = cb;
    this.render();
  }

  public setOpen(open: boolean): void {
    this.open = open;
    this.panelEl.classList.toggle('open', open);
    if (open) this.refreshValues();
  }

  public toggle(): void {
    this.setOpen(!this.open);
  }

  public refreshValues(): void {
    if (!this.open) return;
    for (let i = 0; i < this.syncInputs.length; i++) {
      this.syncInputs[i]();
    }
  }

  private render(): void {
    this.root.innerHTML = `
      <aside class="lookdev-panel glass" id="lookdev-panel" aria-label="Look-Dev 控制面板">
        <div class="ld-header">
          <div>
            <div class="ld-title">Look-Dev 调参面板</div>
            <div class="ld-sub">Step 4 Fine-Grained Visual Controls (G)</div>
          </div>
          <button class="ld-close" id="ld-close" title="关闭 (G)">✕</button>
        </div>
        <div class="ld-body" id="ld-body"></div>
        <div class="ld-footer">
          <button class="ld-action primary" id="ld-copy">Copy JSON</button>
          <button class="ld-action" id="ld-reset">Reset Defaults</button>
        </div>
        <div class="ld-toast" id="ld-toast">已复制 Look-Dev JSON 到剪贴板</div>
      </aside>
    `;

    this.panelEl = this.root.querySelector('#lookdev-panel')!;
    this.toastEl = this.root.querySelector('#ld-toast')!;
    const body = this.root.querySelector('#ld-body')!;

    this.root.querySelector('#ld-close')!.addEventListener('click', () => this.setOpen(false));
    this.root.querySelector('#ld-copy')!.addEventListener('click', () => this.copyJson());
    this.root.querySelector('#ld-reset')!.addEventListener('click', () => {
      this.cb.onResetDefaults();
      this.refreshValues();
      this.showToast('已恢复默认电影视觉参数');
    });

    // Section 1: Atmosphere & Sky
    const secAtmos = this.createSection('大气与天光 Atmosphere', true);
    this.addSelect(
      secAtmos,
      '天光模式 Mode',
      (['auto', 'dawn', 'golden', 'dusk', 'night'] as AtmosphereMode[]).map((m) => ({
        value: m,
        label: ATMOSPHERE_LABELS[m]
      })),
      () => this.state.atmosphere.mode,
      (val) => this.cb.onAtmosphereMode(val as AtmosphereMode)
    );
    this.addSlider(
      secAtmos,
      '连续时间 Time-of-Day',
      0,
      1,
      0.01,
      () => this.state.atmosphere.timeOfDay,
      (v) => this.cb.onTimeOfDayScrub(v)
    );
    this.addColor(
      secAtmos,
      '雾色 Fog Color',
      () => this.state.atmosphere.fogColor,
      (v) => {
        this.state.atmosphere.fogColor = v;
        this.cb.onManualOverride('fog');
      }
    );
    this.addSlider(
      secAtmos,
      '雾浓度 Fog Density',
      0.00005,
      0.0014,
      0.00002,
      () => this.state.atmosphere.fogDensity,
      (v) => {
        this.state.atmosphere.fogDensity = v;
        this.cb.onManualOverride('fog');
      },
      5
    );
    this.addSlider(
      secAtmos,
      '天空散射辉光 Sky Glow',
      0.1,
      2.2,
      0.05,
      () => this.state.atmosphere.skyGlow,
      (v) => {
        this.state.atmosphere.skyGlow = v;
        this.cb.onManualOverride('fog');
      }
    );
    body.appendChild(secAtmos);

    // Section 2: Lights (<= 3 lights!)
    const secLights = this.createSection('实时光照 Lights (≤3)', true);
    this.addColor(secLights, '主光色 Sun/Moon', () => this.state.lights.sunColor, (v) => {
      this.state.lights.sunColor = v;
      this.cb.onManualOverride('lights');
    });
    this.addSlider(secLights, '主光强度 Sun Intensity', 0, 5, 0.05, () => this.state.lights.sunIntensity, (v) => {
      this.state.lights.sunIntensity = v;
      this.cb.onManualOverride('lights');
    });
    this.addSlider(secLights, '主光仰角 Elevation°', 2, 78, 0.5, () => this.state.lights.sunElevation, (v) => {
      this.state.lights.sunElevation = v;
      this.cb.onManualOverride('lights');
    });
    this.addSlider(secLights, '主光方位 Azimuth°', 0, 360, 1, () => this.state.lights.sunAzimuth, (v) => {
      this.state.lights.sunAzimuth = v;
      this.cb.onManualOverride('lights');
    });
    this.addColor(secLights, '天光色 Hemi Sky', () => this.state.lights.hemiSkyColor, (v) => {
      this.state.lights.hemiSkyColor = v;
      this.cb.onManualOverride('lights');
    });
    this.addColor(secLights, '地面反光 Hemi Ground', () => this.state.lights.hemiGroundColor, (v) => {
      this.state.lights.hemiGroundColor = v;
      this.cb.onManualOverride('lights');
    });
    this.addSlider(secLights, '半球强度 Hemi Intensity', 0, 2.5, 0.05, () => this.state.lights.hemiIntensity, (v) => {
      this.state.lights.hemiIntensity = v;
      this.cb.onManualOverride('lights');
    });
    this.addColor(secLights, '补光色 Fill Light', () => this.state.lights.fillColor, (v) => {
      this.state.lights.fillColor = v;
      this.cb.onManualOverride('lights');
    });
    this.addSlider(secLights, '补光强度 Fill Intensity', 0, 2.0, 0.05, () => this.state.lights.fillIntensity, (v) => {
      this.state.lights.fillIntensity = v;
      this.cb.onManualOverride('lights');
    });
    body.appendChild(secLights);

    // Section 3: Emissives
    const secEmissive = this.createSection('建筑自发光 Emissives', true);
    this.addSlider(secEmissive, '暖金古建 Emissive_Warm', 0, 3.0, 0.05, () => this.state.emissives.warm, (v) => {
      this.state.emissives.warm = v;
    });
    this.addSlider(secEmissive, '璀璨金光 Emissive_Gold', 0, 3.0, 0.05, () => this.state.emissives.gold, (v) => {
      this.state.emissives.gold = v;
    });
    this.addSlider(secEmissive, '现代青蓝 Emissive_Cyan', 0, 3.0, 0.05, () => this.state.emissives.cyan, (v) => {
      this.state.emissives.cyan = v;
    });
    this.addSlider(secEmissive, '霓虹点缀 Emissive_Accent', 0, 3.0, 0.05, () => this.state.emissives.accent, (v) => {
      this.state.emissives.accent = v;
    });
    body.appendChild(secEmissive);

    // Section 4: Water & Materials
    const secWater = this.createSection('水体材质 Water Shader', false);
    this.addColor(secWater, '浅水色 Shallow Color', () => this.state.materials.waterColor, (v) => {
      this.state.materials.waterColor = v;
      this.cb.onManualOverride('water');
    });
    this.addColor(secWater, '深水色 Deep Color', () => this.state.materials.waterDeepColor, (v) => {
      this.state.materials.waterDeepColor = v;
      this.cb.onManualOverride('water');
    });
    this.addSlider(secWater, '水面粗糙 Roughness', 0.03, 0.65, 0.01, () => this.state.materials.waterRoughness, (v) => {
      this.state.materials.waterRoughness = v;
    });
    this.addSlider(secWater, '波纹密度 Wave Scale', 0.3, 2.5, 0.05, () => this.state.materials.waveScale, (v) => {
      this.state.materials.waveScale = v;
    });
    this.addSlider(secWater, '水流速度 Wave Speed', 0.0, 2.5, 0.05, () => this.state.materials.waveSpeed, (v) => {
      this.state.materials.waveSpeed = v;
    });
    this.addSlider(secWater, '高光闪烁 Shimmer', 0.0, 2.8, 0.05, () => this.state.materials.waterShimmer, (v) => {
      this.state.materials.waterShimmer = v;
      this.cb.onManualOverride('water');
    });
    body.appendChild(secWater);

    // Section 5: Drone Cinema
    const secDrone = this.createSection('无人机运镜 Drone FPV', false);
    this.addSlider(secDrone, '飞行速度 Speed Scale', 0.2, 2.5, 0.05, () => this.state.drone.speedScale, (v) => {
      this.state.drone.speedScale = v;
    });
    this.addSlider(secDrone, '基础视角 Base FOV°', 38, 65, 1, () => this.state.drone.baseFov, (v) => {
      this.state.drone.baseFov = v;
    });
    this.addSlider(secDrone, '冲刺广角 Swoop FOV+', 0, 40, 1, () => this.state.drone.swoopFovBoost, (v) => {
      this.state.drone.swoopFovBoost = v;
    });
    this.addSlider(secDrone, '压弯倾角 Roll Strength', 0, 1.8, 0.05, () => this.state.drone.rollStrength, (v) => {
      this.state.drone.rollStrength = v;
    });
    body.appendChild(secDrone);

    // Section 6: Post-Processing
    const secPost = this.createSection('后期辉光 Post-Processing', false);
    this.addSlider(secPost, 'ACES 曝光 Exposure', 0.5, 1.8, 0.02, () => this.state.postProcessing.exposure, (v) => {
      this.state.postProcessing.exposure = v;
      this.cb.onManualOverride('fog');
    });
    this.addToggle(secPost, '启用辉光 Bloom', () => this.state.postProcessing.bloomEnabled, (v) => {
      this.state.postProcessing.bloomEnabled = v;
    });
    this.addSlider(secPost, '辉光阈值 Threshold', 0.3, 1.2, 0.02, () => this.state.postProcessing.bloomThreshold, (v) => {
      this.state.postProcessing.bloomThreshold = v;
      this.cb.onManualOverride('fog');
    });
    this.addSlider(secPost, '辉光强度 Strength', 0.0, 1.4, 0.02, () => this.state.postProcessing.bloomStrength, (v) => {
      this.state.postProcessing.bloomStrength = v;
      this.cb.onManualOverride('fog');
    });
    this.addSlider(secPost, '辉光半径 Radius', 0.0, 1.0, 0.02, () => this.state.postProcessing.bloomRadius, (v) => {
      this.state.postProcessing.bloomRadius = v;
    });
    this.addSlider(secPost, '电影暗角 Vignette', 0.0, 0.75, 0.02, () => this.state.postProcessing.vignetteIntensity, (v) => {
      this.state.postProcessing.vignetteIntensity = v;
    });
    body.appendChild(secPost);
  }

  private createSection(title: string, defaultOpen: boolean): HTMLDetailsElement {
    const det = document.createElement('details');
    det.className = 'ld-section';
    det.open = defaultOpen;
    const sum = document.createElement('summary');
    sum.textContent = title;
    det.appendChild(sum);
    return det;
  }

  private addSlider(
    parent: HTMLElement,
    label: string,
    min: number,
    max: number,
    step: number,
    getter: () => number,
    setter: (v: number) => void,
    decimals = 2
  ): void {
    const row = document.createElement('div');
    row.className = 'ld-row';
    const top = document.createElement('div');
    top.className = 'ld-row-top';
    const lbl = document.createElement('span');
    lbl.textContent = label;
    const valEl = document.createElement('span');
    valEl.className = 'ld-val';
    top.append(lbl, valEl);

    const input = document.createElement('input');
    input.type = 'range';
    input.min = String(min);
    input.max = String(max);
    input.step = String(step);
    input.value = String(getter());
    valEl.textContent = getter().toFixed(decimals);

    input.addEventListener('input', () => {
      const n = Number(input.value);
      valEl.textContent = n.toFixed(decimals);
      setter(n);
    });

    this.syncInputs.push(() => {
      if (document.activeElement === input) return;
      const cur = getter();
      input.value = String(cur);
      valEl.textContent = cur.toFixed(decimals);
    });

    row.append(top, input);
    parent.appendChild(row);
  }

  private addColor(
    parent: HTMLElement,
    label: string,
    getter: () => string,
    setter: (v: string) => void
  ): void {
    const row = document.createElement('div');
    row.className = 'ld-row inline';
    const lbl = document.createElement('span');
    lbl.textContent = label;
    const input = document.createElement('input');
    input.type = 'color';
    input.value = getter();
    input.addEventListener('input', () => setter(input.value));
    this.syncInputs.push(() => {
      if (document.activeElement === input) return;
      input.value = getter();
    });
    row.append(lbl, input);
    parent.appendChild(row);
  }

  private addToggle(
    parent: HTMLElement,
    label: string,
    getter: () => boolean,
    setter: (v: boolean) => void
  ): void {
    const row = document.createElement('div');
    row.className = 'ld-row inline';
    const lbl = document.createElement('span');
    lbl.textContent = label;
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.checked = getter();
    input.addEventListener('change', () => setter(input.checked));
    this.syncInputs.push(() => {
      input.checked = getter();
    });
    row.append(lbl, input);
    parent.appendChild(row);
  }

  private addSelect(
    parent: HTMLElement,
    label: string,
    options: Array<{ value: string; label: string }>,
    getter: () => string,
    setter: (v: string) => void
  ): void {
    const row = document.createElement('div');
    row.className = 'ld-row inline';
    const lbl = document.createElement('span');
    lbl.textContent = label;
    const sel = document.createElement('select');
    for (const o of options) {
      const opt = document.createElement('option');
      opt.value = o.value;
      opt.textContent = o.label;
      sel.appendChild(opt);
    }
    sel.value = getter();
    sel.addEventListener('change', () => setter(sel.value));
    this.syncInputs.push(() => {
      sel.value = getter();
    });
    row.append(lbl, sel);
    parent.appendChild(row);
  }

  private async copyJson(): Promise<void> {
    const json = JSON.stringify(this.state, null, 2);
    try {
      await navigator.clipboard.writeText(json);
      this.showToast('已复制 Look-Dev JSON 到剪贴板');
    } catch {
      // Fallback textarea copy
      const ta = document.createElement('textarea');
      ta.value = json;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
      this.showToast('已复制 Look-Dev JSON');
    }
  }

  private showToast(msg: string): void {
    this.toastEl.textContent = msg;
    this.toastEl.classList.add('show');
    window.setTimeout(() => this.toastEl.classList.remove('show'), 2100);
  }
}
