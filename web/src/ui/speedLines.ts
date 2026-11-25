/**
 * Subtle radial FPV speed-lines & kinetic shimmer drawn on a lightweight 2D overlay canvas
 * ONLY during high-speed inter-landmark swoops (intensity > 0.12).
 */
export class SpeedLinesOverlay {
  private readonly canvas: HTMLCanvasElement;
  private readonly ctx: CanvasRenderingContext2D | null;
  private width = 0;
  private height = 0;
  private readonly rays: Array<{ angle: number; phase: number; speed: number; width: number }> = [];

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    for (let i = 0; i < 44; i++) {
      this.rays.push({
        angle: (i / 44) * Math.PI * 2 + (i % 3) * 0.03,
        phase: (i * 0.37) % 1,
        speed: 1.4 + (i % 5) * 0.32,
        width: 0.8 + (i % 3) * 0.55
      });
    }
    this.resize();
  }

  public resize(): void {
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    this.width = window.innerWidth;
    this.height = window.innerHeight;
    this.canvas.width = Math.floor(this.width * dpr);
    this.canvas.height = Math.floor(this.height * dpr);
    this.ctx?.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  public render(elapsed: number, speedIntensity: number, nightFactor: number, uiHidden: boolean): void {
    const ctx = this.ctx;
    if (!ctx) return;

    ctx.clearRect(0, 0, this.width, this.height);
    if (uiHidden || speedIntensity < 0.14) return;

    const alphaScale = Math.min((speedIntensity - 0.14) / 0.86, 1) * 0.34;
    const cx = this.width * 0.5;
    const cy = this.height * 0.5;
    const maxR = Math.hypot(cx, cy) * 1.05;

    ctx.save();
    ctx.lineCap = 'round';

    const warmStroke = nightFactor > 0.55 ? '110, 224, 255' : '255, 212, 148';
    const altStroke = nightFactor > 0.55 ? '255, 215, 138' : '255, 244, 224';

    for (let i = 0; i < this.rays.length; i++) {
      const r = this.rays[i];
      const prog = (r.phase + elapsed * r.speed * (0.7 + speedIntensity)) % 1;
      const innerR = maxR * (0.48 + prog * 0.36);
      const outerR = innerR + maxR * (0.14 + speedIntensity * 0.16);
      const cos = Math.cos(r.angle);
      const sin = Math.sin(r.angle);

      const x1 = cx + cos * innerR;
      const y1 = cy + sin * innerR;
      const x2 = cx + cos * outerR;
      const y2 = cy + sin * outerR;

      const grad = ctx.createLinearGradient(x1, y1, x2, y2);
      const col = i % 3 === 0 ? altStroke : warmStroke;
      grad.addColorStop(0, `rgba(${col}, 0)`);
      grad.addColorStop(0.65, `rgba(${col}, ${alphaScale.toFixed(3)})`);
      grad.addColorStop(1, `rgba(${col}, 0)`);

      ctx.strokeStyle = grad;
      ctx.lineWidth = r.width;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }

    ctx.restore();
  }
}
