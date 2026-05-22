/* 画布标注 — 参考点、线段、圆、测距 */
'use strict';

const ANN_PX_PER_CM = 5;

const Annotations = {
  items: [],
  pending: null,
  hover: null,
  _id: 0,

  reset() {
    this.items = [];
    this.pending = null;
    this.hover = null;
    this._id = 0;
  },

  distCm(x1, y1, x2, y2) {
    return Math.hypot(x2 - x1, y2 - y1) / ANN_PX_PER_CM;
  },

  radiusCm(cx, cy, px, py) {
    return Math.hypot(px - cx, py - cy) / ANN_PX_PER_CM;
  },

  isAnnotTool(tool) {
    return ['refpoint', 'segment', 'circle', 'measure'].includes(tool);
  },

  cancelPending() {
    this.pending = null;
    this.hover = null;
  },

  handleClick(pt, shiftKey) {
    if (shiftKey) {
      const removed = this.removeNear(pt.x, pt.y);
      return removed ? 'deleted' : null;
    }
    const tool = typeof ViewShell !== 'undefined' ? ViewShell.activeTool : null;
    if (!this.isAnnotTool(tool)) return null;

    if (tool === 'refpoint') {
      this.items.push({ id: ++this._id, type: 'point', x: pt.x, y: pt.y });
      return 'point';
    }

    if (!this.pending || this.pending.tool !== tool) {
      this.pending = { tool, clicks: [pt] };
      return 'pending';
    }

    this.pending.clicks.push(pt);
    const clicks = this.pending.clicks;

    if (tool === 'segment' || tool === 'measure') {
      if (clicks.length >= 2) {
        const a = clicks[0], b = clicks[1];
        const cm = this.distCm(a.x, a.y, b.x, b.y);
        this.items.push({
          id: ++this._id,
          type: tool === 'measure' ? 'measure' : 'segment',
          x1: a.x, y1: a.y, x2: b.x, y2: b.y,
          lengthCm: cm
        });
        this.pending = null;
        return 'segment';
      }
    }

    if (tool === 'circle') {
      if (clicks.length >= 2) {
        const c = clicks[0], r = clicks[1];
        const radCm = this.radiusCm(c.x, c.y, r.x, r.y);
        if (radCm < 0.5) {
          this.pending = null;
          return 'too-small';
        }
        this.items.push({
          id: ++this._id,
          type: 'circle',
          cx: c.x, cy: c.y,
          rPx: Math.hypot(r.x - c.x, r.y - c.y),
          radiusCm: radCm
        });
        this.pending = null;
        return 'circle';
      }
    }

    return 'pending';
  },

  removeNear(x, y, radius) {
    radius = radius || 24;
    let idx = -1, best = radius;
    this.items.forEach((it, i) => {
      let d = Infinity;
      if (it.type === 'point') d = Math.hypot(it.x - x, it.y - y);
      else if (it.type === 'segment' || it.type === 'measure') {
        d = Math.min(
          Math.hypot(it.x1 - x, it.y1 - y),
          Math.hypot(it.x2 - x, it.y2 - y),
          this._distToSegment(x, y, it.x1, it.y1, it.x2, it.y2)
        );
      } else if (it.type === 'circle') {
        const dr = Math.abs(Math.hypot(it.cx - x, it.cy - y) - it.rPx);
        d = Math.min(dr, Math.hypot(it.cx - x, it.cy - y));
      }
      if (d < best) { best = d; idx = i; }
    });
    if (idx >= 0) {
      this.items.splice(idx, 1);
      return true;
    }
    return false;
  },

  _distToSegment(px, py, x1, y1, x2, y2) {
    const dx = x2 - x1, dy = y2 - y1;
    const len2 = dx * dx + dy * dy;
    if (len2 < 1e-6) return Math.hypot(px - x1, py - y1);
    let t = ((px - x1) * dx + (py - y1) * dy) / len2;
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
  },

  handleMove(pt) {
    this.hover = pt;
  },

  draw(ctx, sim) {
    const scale = sim.viewport?.scale || 1;
    const fs = Math.max(9, 11 / scale);

    this.items.forEach(it => {
      if (it.type === 'point') this._drawPoint(ctx, it, fs, scale);
      else if (it.type === 'segment') this._drawSegment(ctx, it, '#a78bfa', fs, scale, false);
      else if (it.type === 'measure') this._drawSegment(ctx, it, '#fbbf24', fs, scale, true);
      else if (it.type === 'circle') this._drawCircle(ctx, it, fs, scale);
    });

    if (this.pending && this.hover) {
      const tool = this.pending.tool;
      const a = this.pending.clicks[0];
      const b = this.hover;
      ctx.save();
      ctx.setLineDash([6, 4]);
      ctx.globalAlpha = 0.75;
      if (tool === 'segment' || tool === 'measure') {
        this._strokeLine(ctx, a.x, a.y, b.x, b.y, '#94a3b8', 2 / scale);
        const cm = this.distCm(a.x, a.y, b.x, b.y);
        this._label(ctx, (a.x + b.x) / 2, (a.y + b.y) / 2 - 14 / scale, cm.toFixed(1) + ' cm', fs);
      } else if (tool === 'circle') {
        const r = Math.hypot(b.x - a.x, b.y - a.y);
        ctx.strokeStyle = '#94a3b8';
        ctx.lineWidth = 2 / scale;
        ctx.beginPath();
        ctx.arc(a.x, a.y, r, 0, Math.PI * 2);
        ctx.stroke();
        this._label(ctx, a.x, a.y - r - 12 / scale, 'r = ' + (r / ANN_PX_PER_CM).toFixed(1) + ' cm', fs);
      }
      ctx.restore();
    }
  },

  _drawPoint(ctx, it, fs, scale) {
    ctx.fillStyle = '#c084fc';
    ctx.strokeStyle = '#7c3aed';
    ctx.lineWidth = 2 / scale;
    ctx.beginPath();
    ctx.arc(it.x, it.y, 6 / scale, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    this._label(ctx, it.x + 10 / scale, it.y - 6 / scale, 'P' + it.id, fs);
  },

  _drawSegment(ctx, it, color, fs, scale, isMeasure) {
    this._strokeLine(ctx, it.x1, it.y1, it.x2, it.y2, color, (isMeasure ? 3 : 2) / scale);
    const cm = it.lengthCm ?? this.distCm(it.x1, it.y1, it.x2, it.y2);
    const mx = (it.x1 + it.x2) / 2;
    const my = (it.y1 + it.y2) / 2;
    const label = isMeasure ? 'd = ' + cm.toFixed(1) + ' cm' : cm.toFixed(1) + ' cm';
    this._label(ctx, mx, my - 12 / scale, label, fs, isMeasure ? '#fef3c7' : '#e9d5ff');
    if (isMeasure) {
      ctx.fillStyle = color;
      [ [it.x1, it.y1], [it.x2, it.y2] ].forEach(([x, y]) => {
        ctx.beginPath();
        ctx.arc(x, y, 4 / scale, 0, Math.PI * 2);
        ctx.fill();
      });
    }
  },

  _drawCircle(ctx, it, fs, scale) {
    const r = it.rPx;
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2 / scale;
    ctx.fillStyle = 'rgba(56,189,248,.08)';
    ctx.beginPath();
    ctx.arc(it.cx, it.cy, r, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    const C = 2 * Math.PI * (it.radiusCm ?? r / ANN_PX_PER_CM);
    const S = Math.PI * (it.radiusCm ?? r / ANN_PX_PER_CM) ** 2;
    this._label(ctx, it.cx, it.cy - r - 14 / scale,
      'r=' + (it.radiusCm ?? r / ANN_PX_PER_CM).toFixed(1) + 'cm · C≈' + C.toFixed(1) + ' · S≈' + S.toFixed(0), fs);
    ctx.fillStyle = '#38bdf8';
    ctx.beginPath();
    ctx.arc(it.cx, it.cy, 4 / scale, 0, Math.PI * 2);
    ctx.fill();
  },

  _strokeLine(ctx, x1, y1, x2, y2, color, lw) {
    ctx.strokeStyle = color;
    ctx.lineWidth = lw;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  },

  _label(ctx, x, y, text, fs, bg) {
    ctx.font = '600 ' + fs + 'px Outfit, Noto Sans SC, sans-serif';
    const m = ctx.measureText(text);
    const pad = 3;
    if (bg) {
      ctx.fillStyle = 'rgba(15,23,42,.75)';
      ctx.fillRect(x - pad, y - fs, m.width + pad * 2, fs + pad * 2);
    }
    ctx.fillStyle = bg || '#f1f5f9';
    ctx.fillText(text, x, y);
  },

  toJSON() {
    return JSON.stringify({ items: this.items });
  },

  fromJSON(str) {
    try {
      const data = JSON.parse(str);
      this.items = data.items || [];
      this._id = this.items.reduce((m, it) => Math.max(m, it.id || 0), 0);
    } catch (_) { /* ignore */ }
  }
};

window.Annotations = Annotations;
