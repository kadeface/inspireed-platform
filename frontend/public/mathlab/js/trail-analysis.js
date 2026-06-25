/* 轨迹分析 — 弧长、参数化摘要、与目标图形重合度 */
'use strict';

const TrailAnalysis = {
  PX_PER_CM: 5,

  pxPerCm(sim) {
    return sim?.getPxPerCm ? sim.getPxPerCm() : this.PX_PER_CM;
  },

  arcLengthCm(trail, pxPerCm) {
    if (!trail || trail.length < 2) return 0;
    const px = pxPerCm ?? this.PX_PER_CM;
    let len = 0;
    for (let i = 1; i < trail.length; i++) {
      if (trail[i].break) continue;
      len += Math.hypot(trail[i].x - trail[i - 1].x, trail[i].y - trail[i - 1].y);
    }
    return len / px;
  },

  toCm(sim, x, y) {
    const ox = sim.state.startX;
    const oy = sim.state.startY;
    const px = this.pxPerCm(sim);
    return {
      x: (x - ox) / px,
      y: (oy - y) / px
    };
  },

  parametricSummary(sim, maxVerts) {
    maxVerts = maxVerts || 8;
    const trail = sim.trail || [];
    if (trail.length < 2) return '—';
    const indices = [];
    if (trail.length <= maxVerts) {
      trail.forEach((_, i) => indices.push(i));
    } else {
      const step = (trail.length - 1) / (maxVerts - 1);
      for (let i = 0; i < maxVerts; i++) {
        indices.push(Math.min(trail.length - 1, Math.round(i * step)));
      }
    }
    return indices.map(i => {
      const c = this.toCm(sim, trail[i].x, trail[i].y);
      return '(' + c.x.toFixed(0) + ',' + c.y.toFixed(0) + ')';
    }).join(' → ');
  },

  getTargetPolyline(sim) {
    const cfg = sim.sceneConfig || {};
    const ox = sim.state.startX;
    const oy = sim.state.startY;
    const px = this.PX_PER_CM;

    if (sim.scene === SCENE.CIRCLE && cfg.radius) {
      const r = cfg.radius * px;
      const pts = [];
      for (let i = 0; i <= 48; i++) {
        const t = (i / 48) * Math.PI * 2;
        pts.push({ x: ox + r * Math.cos(t), y: oy + r * Math.sin(t) });
      }
      return { kind: 'circle', points: pts, perimeterCm: 2 * Math.PI * cfg.radius };
    }

    let wCm, hCm;
    if (sim.scene === SCENE.SHAPE && cfg.shape === 'square' && cfg.side) {
      wCm = hCm = cfg.side;
    } else if (sim.scene === SCENE.PERIMETER) {
      if (cfg.square) wCm = hCm = cfg.square.side;
      else if (cfg.rect) { wCm = cfg.rect.w; hCm = cfg.rect.h; }
    }

    if (wCm && hCm) {
      const w = wCm * px, h = hCm * px;
      return {
        kind: 'rect',
        points: [
          { x: ox, y: oy },
          { x: ox + w, y: oy },
          { x: ox + w, y: oy - h },
          { x: ox, y: oy - h },
          { x: ox, y: oy }
        ],
        perimeterCm: 2 * (wCm + hCm)
      };
    }

    if (sim.scene === SCENE.SHAPE && cfg.shape === 'hexagon' && cfg.side) {
      const s = cfg.side * px;
      const pts = [];
      for (let i = 0; i <= 6; i++) {
        const t = (i / 6) * Math.PI * 2 - Math.PI / 6;
        pts.push({ x: ox + s * Math.cos(t), y: oy + s * Math.sin(t) });
      }
      return { kind: 'hexagon', points: pts, perimeterCm: 6 * cfg.side };
    }

    const tri = cfg.trigTriangle;
    if (tri && typeof sim.resolveTrigSides === 'function') {
      const { adj, opp, hyp } = sim.resolveTrigSides(tri);
      const ax = ox;
      const ay = oy;
      const bx = ox + adj * px;
      const by = oy;
      const cx = bx;
      const cy = oy - opp * px;
      return {
        kind: 'triangle',
        points: [
          { x: ax, y: ay },
          { x: bx, y: by },
          { x: cx, y: cy },
          { x: ax, y: ay }
        ],
        perimeterCm: adj + opp + hyp
      };
    }

    return null;
  },

  distToPolyline(px, py, poly) {
    let best = Infinity;
    for (let i = 0; i < poly.length - 1; i++) {
      const a = poly[i], b = poly[i + 1];
      const d = this._distToSegment(px, py, a.x, a.y, b.x, b.y);
      if (d < best) best = d;
    }
    return best;
  },

  _distToSegment(px, py, x1, y1, x2, y2) {
    const dx = x2 - x1, dy = y2 - y1;
    const len2 = dx * dx + dy * dy;
    if (len2 < 1e-6) return Math.hypot(px - x1, py - y1);
    let t = ((px - x1) * dx + (py - y1) * dy) / len2;
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
  },

  analyze(sim) {
    const trail = sim.trail || [];
    const px = this.pxPerCm(sim);
    const arcCm = this.arcLengthCm(trail, px);
    const param = this.parametricSummary(sim, 6);
    const target = this.getTargetPolyline(sim);

    const base = {
      arcLengthCm: arcCm,
      parametric: param,
      hasTarget: !!target,
      matchPercent: null,
      meanDevCm: null,
      perimeterCm: null,
      closeGapCm: null,
      message: '弧长 L ≈ ' + arcCm.toFixed(1) + ' cm'
    };

    if (trail.length < 2) {
      base.message = '轨迹过短，无法分析';
      return base;
    }

    const closePx = Math.hypot(
      trail[trail.length - 1].x - trail[0].x,
      trail[trail.length - 1].y - trail[0].y
    );
    base.closeGapCm = closePx / px;

    if (!target) {
      base.message = 'L ≈ ' + arcCm.toFixed(1) + ' cm · 闭合间隙 ' + base.closeGapCm.toFixed(1) + ' cm';
      return base;
    }

    base.perimeterCm = target.perimeterCm;
    const sample = [];
    const step = Math.max(1, Math.floor(trail.length / 60));
    for (let i = 0; i < trail.length; i += step) sample.push(trail[i]);
    sample.push(trail[trail.length - 1]);

    let sumDev = 0;
    sample.forEach(p => { sumDev += this.distToPolyline(p.x, p.y, target.points); });
    base.meanDevCm = (sumDev / sample.length) / px;

    const devScore = Math.max(0, 100 - base.meanDevCm * 15);
    const lenRatio = target.perimeterCm > 0 ? arcCm / target.perimeterCm : 1;
    const lenScore = Math.max(0, 100 - Math.abs(1 - Math.min(lenRatio, 1.2)) * 70);
    const closeScore = base.closeGapCm < 3 ? 100 : Math.max(0, 100 - base.closeGapCm * 8);
    base.matchPercent = Math.round(devScore * 0.55 + lenScore * 0.25 + closeScore * 0.2);

    if (base.matchPercent >= 85) {
      base.message = '轨迹与目标吻合度 <strong>' + base.matchPercent + '%</strong> · 很好';
    } else if (base.matchPercent >= 60) {
      base.message = '吻合度 <strong>' + base.matchPercent + '%</strong> · 偏差 ' + base.meanDevCm.toFixed(1) + ' cm';
    } else {
      base.message = '吻合度 <strong>' + base.matchPercent + '%</strong> · 可调整程序或原点';
    }
    return base;
  }
};

window.TrailAnalysis = TrailAnalysis;
