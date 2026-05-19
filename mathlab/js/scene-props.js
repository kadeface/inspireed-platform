/* 场景道具 — 定义、绘制与任务预设 */
'use strict';

/** 与 app.js 一致；须在 app.js 之前加载，不可依赖其 IIFE 内变量 */
const PX_PER_CM = 5;
const GRID_STEP = 50;

const PROP_CATALOG = {
  tape:    { icon: '📏', name: '距离标',  color: '#f97316' },
  cone:    { icon: '🔶', name: '路锥',    color: '#fb923c' },
  flag:    { icon: '🚩', name: '终点旗',  color: '#ef4444' },
  candy:   { icon: '🍬', name: '糖果',    color: '#ec4899' },
  tree:    { icon: '🌳', name: '树',      color: '#22c55e' },
  target:  { icon: '🎯', name: '目标点',  color: '#a855f7' },
  box:     { icon: '📦', name: '障碍物',  color: '#64748b' },
  star:    { icon: '⭐', name: '检查点',  color: '#eab308' }
};

const SceneProps = {
  list: [],
  activeTool: null,
  hover: null,
  _id: 0,

  reset(list) {
    this.list = [];
    this._id = 0;
    (list || []).forEach(p => {
      this.list.push({
        id: ++this._id,
        type: p.type || 'tape',
        x: p.x ?? null,
        y: p.y ?? null,
        atCm: p.atCm ?? null,
        label: p.label || ''
      });
    });
  },

  add(type, x, y, label) {
    const item = {
      id: ++this._id,
      type,
      x,
      y,
      atCm: null,
      label: label || ''
    };
    this.list.push(item);
    return item;
  },

  removeAt(x, y, radius) {
    radius = radius || 22;
    let idx = -1, best = radius;
    this.list.forEach((p, i) => {
      const pos = this.resolve(p, window.__simRef);
      if (!pos) return;
      const d = Math.hypot(pos.x - x, pos.y - y);
      if (d < best) { best = d; idx = i; }
    });
    if (idx >= 0) this.list.splice(idx, 1);
    return idx >= 0;
  },

    resolve(p, sim) {
      if (!sim) return null;
      if (p.atCm != null) {
        let pxPerCm = PX_PER_CM;
        if (sim.scene === SCENE.NUMBERLINE) {
          const unitCm = sim.sceneConfig.unitCm || 20;
          pxPerCm = sim.getNumberLineUnitPx() / unitCm;
        }
        return {
          x: sim.state.startX + p.atCm * pxPerCm,
          y: sim.state.startY
        };
      }
      return { x: p.x, y: p.y };
    },

  resolveAll(sim) {
    return this.list.map(p => {
      const pos = this.resolve(p, sim);
      return pos ? Object.assign({}, p, pos) : null;
    }).filter(Boolean);
  },

  /** 根据任务生成推荐道具 */
  presetsForTask(task, sim) {
    const cfg = task.sceneConfig || {};
    const out = [];

    if (cfg.markers) {
      cfg.markers.forEach((cm, i) => {
        if (cfg.plant && cm > 0) {
          out.push({ type: 'tree', atCm: cm, label: String(i + 1) });
        } else {
          out.push({
            type: 'tape',
            atCm: cm,
            label: cm >= 100 ? (cm / 100) + 'm' : cm + 'cm'
          });
        }
      });
    }
    if (cfg.target && sim) {
      const cell = (cfg.cellCm || 10) * PX_PER_CM;
      const ox = sim.state.startX;
      const oy = sim.state.startY;
      const [tc, tr] = cfg.target;
      out.push({
        type: 'flag',
        x: ox + (tc - 1) * cell + cell / 2,
        y: oy - (tr - 0.5) * cell,
        label: '(' + tc + ',' + tr + ')'
      });
    }
    if (task.scene === SCENE.NUMBERLINE) {
      out.push({ type: 'star', atCm: 100, label: '+5' });
      out.push({ type: 'flag', atCm: 40, label: '+2' });
    }
    if (task.id === 'p2t5') {
      [20, 40, 60].forEach((cm, i) => out.push({ type: 'candy', atCm: cm, label: '份' + (i + 1) }));
    }
    if (task.scene === SCENE.ANGLE) {
      out.push({ type: 'cone', atCm: 0, label: '顶点' });
    }
    if (cfg.props) out.push.apply(out, cfg.props);

    return out;
  },

  draw(ctx, sim) {
    const items = this.resolveAll(sim);
    items.forEach(p => this.drawOne(ctx, p));
    if (this.hover && this.activeTool && this.activeTool !== 'erase') {
      this.drawOne(ctx, Object.assign({}, this.hover, { type: this.activeTool, ghost: true }));
    }
  },

  drawOne(ctx, p) {
    const ghost = p.ghost;
    const x = p.x, y = p.y;
    ctx.save();
    if (ghost) ctx.globalAlpha = 0.45;

    switch (p.type) {
      case 'tape':
        this.drawTape(ctx, x, y, p.label);
        break;
      case 'cone':
        this.drawCone(ctx, x, y);
        break;
      case 'flag':
        this.drawFlag(ctx, x, y, p.label);
        break;
      case 'candy':
        this.drawCandy(ctx, x, y, p.label);
        break;
      case 'tree':
        this.drawTree(ctx, x, y, p.label);
        break;
      case 'target':
        this.drawTarget(ctx, x, y);
        break;
      case 'box':
        this.drawBox(ctx, x, y);
        break;
      case 'star':
        this.drawStar(ctx, x, y, p.label);
        break;
      default:
        break;
    }
    ctx.restore();
  },

  drawTape(ctx, x, y, label) {
    ctx.strokeStyle = '#f97316';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 4]);
    ctx.beginPath();
    ctx.moveTo(x, y - 36);
    ctx.lineTo(x, y + 36);
    ctx.stroke();
    ctx.setLineDash([]);
    if (label) {
      ctx.fillStyle = '#fbbf24';
      ctx.font = '600 10px Outfit, Noto Sans SC, sans-serif';
      ctx.fillText(label, x - 12, y - 42);
    }
  },

  drawCone(ctx, x, y) {
    ctx.fillStyle = '#fb923c';
    ctx.beginPath();
    ctx.moveTo(x, y - 14);
    ctx.lineTo(x - 10, y + 8);
    ctx.lineTo(x + 10, y + 8);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = '#c2410c';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = 'rgba(255,255,255,.35)';
    ctx.beginPath();
    ctx.arc(x - 2, y - 2, 3, 0, Math.PI * 2);
    ctx.fill();
  },

  drawFlag(ctx, x, y, label) {
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, y + 12);
    ctx.lineTo(x, y - 18);
    ctx.stroke();
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.moveTo(x, y - 18);
    ctx.lineTo(x + 18, y - 12);
    ctx.lineTo(x, y - 6);
    ctx.closePath();
    ctx.fill();
    if (label) {
      ctx.fillStyle = '#fca5a5';
      ctx.font = '600 9px sans-serif';
      ctx.fillText(label, x + 4, y + 22);
    }
  },

  drawCandy(ctx, x, y, label) {
    ctx.fillStyle = '#ec4899';
    ctx.beginPath();
    ctx.arc(x, y, 9, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#f9a8d4';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = '#fff';
    ctx.font = '8px sans-serif';
    ctx.fillText('🍬', x - 5, y + 3);
    if (label) {
      ctx.fillStyle = '#fbcfe8';
      ctx.font = '9px sans-serif';
      ctx.fillText(label, x - 8, y + 20);
    }
  },

  drawTree(ctx, x, y, label) {
    ctx.fillStyle = '#15803d';
    ctx.beginPath();
    ctx.arc(x, y, 12, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#22c55e';
    ctx.beginPath();
    ctx.arc(x - 4, y - 3, 5, 0, Math.PI * 2);
    ctx.arc(x + 4, y - 2, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#78350f';
    ctx.fillRect(x - 2, y + 8, 4, 6);
    if (label) {
      ctx.fillStyle = '#86efac';
      ctx.font = '9px sans-serif';
      ctx.fillText('#' + label, x - 6, y - 16);
    }
  },

  drawTarget(ctx, x, y) {
    const colors = ['#ef4444', '#fff', '#ef4444', '#fff', '#ef4444'];
    [18, 14, 10, 6, 3].forEach((r, i) => {
      ctx.fillStyle = colors[i];
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    });
  },

  drawBox(ctx, x, y) {
    ctx.fillStyle = '#475569';
    ctx.fillRect(x - 14, y - 14, 28, 28);
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 2;
    ctx.strokeRect(x - 14, y - 14, 28, 28);
    ctx.strokeStyle = 'rgba(255,255,255,.2)';
    ctx.beginPath();
    ctx.moveTo(x - 14, y - 14);
    ctx.lineTo(x, y);
    ctx.lineTo(x + 14, y - 14);
    ctx.stroke();
  },

  drawStar(ctx, x, y, label) {
    ctx.fillStyle = '#eab308';
    ctx.strokeStyle = '#ca8a04';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let i = 0; i < 5; i++) {
      const a = (i * 4 * Math.PI) / 5 - Math.PI / 2;
      const r = i % 2 === 0 ? 12 : 5;
      const px = x + Math.cos(a) * r;
      const py = y + Math.sin(a) * r;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    if (label) {
      ctx.fillStyle = '#fde047';
      ctx.font = '9px sans-serif';
      ctx.fillText(label, x - 8, y + 22);
    }
  }
};

window.PROP_CATALOG = PROP_CATALOG;
window.SceneProps = SceneProps;
