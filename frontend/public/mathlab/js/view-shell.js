/* MathLab UI shell — drawers, toolbar, viewport, algebra bar */
'use strict';

const ViewShell = {
  sim: null,
  activeTool: 'pan',
  openDrawer: null,
  _panning: false,
  _panStart: null,
  _dragOrigin: false,

  init(sim) {
    this.sim = sim;
    this.bindDrawers();
    this.bindToolbar();
    this.bindModeToggle();
    this.bindCanvas();
    this.bindTrailPanel();
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
    if (typeof ResizeObserver !== 'undefined') {
      const ro = new ResizeObserver(() => this.resizeCanvas());
      const wrap = document.getElementById('canvasWrap');
      if (wrap) ro.observe(wrap);
    }
  },

  resizeCanvas() {
    const wrap = document.getElementById('canvasWrap');
    const canvas = this.sim?.canvas;
    if (!wrap || !canvas) return;
    const w = Math.max(320, wrap.clientWidth);
    const h = Math.max(240, wrap.clientHeight);
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
      this.sim.draw();
    }
    if (typeof Blockly !== 'undefined' && window.__blocklyWorkspace) {
      Blockly.svgResize(window.__blocklyWorkspace);
    }
  },

  bindDrawers() {
    const open = (name) => {
      const isCode = name === 'code';
      const drawer = document.getElementById(isCode ? 'drawerCode' : 'drawerLesson');
      const backdrop = document.getElementById(isCode ? 'backdropCode' : 'backdropLesson');
      const willOpen = this.openDrawer !== name;
      this.closeDrawers();
      if (willOpen) {
        drawer.classList.add('open');
        drawer.setAttribute('aria-hidden', 'false');
        backdrop.hidden = false;
        this.openDrawer = name;
        if (isCode) {
          setTimeout(() => {
            if (typeof Blockly !== 'undefined' && window.__blocklyWorkspace) {
              Blockly.svgResize(window.__blocklyWorkspace);
            }
          }, 280);
        }
      }
    };

    document.getElementById('btnDrawerCode')?.addEventListener('click', () => open('code'));
    document.getElementById('btnDrawerLesson')?.addEventListener('click', () => open('lesson'));
    document.querySelectorAll('.drawer-close').forEach(btn => {
      btn.addEventListener('click', () => this.closeDrawers());
    });
    document.getElementById('backdropCode')?.addEventListener('click', () => this.closeDrawers());
    document.getElementById('backdropLesson')?.addEventListener('click', () => this.closeDrawers());

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        if (typeof Annotations !== 'undefined' && Annotations.pending) {
          Annotations.cancelPending();
          this.sim.draw();
          return;
        }
        this.closeDrawers();
      }
    });
  },

  closeDrawers() {
    ['drawerCode', 'drawerLesson'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.classList.remove('open');
        el.setAttribute('aria-hidden', 'true');
      }
    });
    ['backdropCode', 'backdropLesson'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.hidden = true;
    });
    this.openDrawer = null;
  },

  bindModeToggle() {
    const setMode = (mode) => {
      this.sim.renderMode = mode;
      document.getElementById('btnModeCar')?.classList.toggle('active', mode === 'car');
      document.getElementById('btnModePoint')?.classList.toggle('active', mode === 'point');
      this.sim.draw();
    };
    document.getElementById('btnModeCar')?.addEventListener('click', () => setMode('car'));
    document.getElementById('btnModePoint')?.addEventListener('click', () => setMode('point'));
  },

  bindTrailPanel() {
    document.getElementById('btnTrailClose')?.addEventListener('click', () => {
      const panel = document.getElementById('trailPanel');
      if (panel) panel.hidden = true;
      document.querySelector('[data-tool="trailList"]')?.classList.remove('active');
    });
  },

  toggleTrailPanel() {
    const panel = document.getElementById('trailPanel');
    if (!panel) return;
    panel.hidden = !panel.hidden;
    document.querySelector('[data-tool="trailList"]')?.classList.toggle('active', !panel.hidden);
    if (!panel.hidden) this.refreshTrailPanel();
  },

  refreshTrailPanel() {
    const sim = this.sim;
    const tbody = document.getElementById('trailTableBody');
    const countEl = document.getElementById('trailCount');
    if (!tbody || !sim) return;

    const ox = sim.state.startX;
    const oy = sim.state.startY;
    const PX = 5;
    const raw = sim.trail || [];
    const maxRows = 40;
    let indices = [];
    if (raw.length <= maxRows) {
      indices = raw.map((_, i) => i);
    } else {
      const step = (raw.length - 1) / (maxRows - 1);
      for (let i = 0; i < maxRows; i++) {
        indices.push(Math.min(raw.length - 1, Math.round(i * step)));
      }
    }

    tbody.innerHTML = indices.map((idx, row) => {
      const p = raw[idx];
      const x = ((p.x - ox) / PX).toFixed(1);
      const y = ((oy - p.y) / PX).toFixed(1);
      return '<tr><td>' + (row + 1) + '</td><td>' + x + '</td><td>' + y + '</td></tr>';
    }).join('');

    if (countEl) countEl.textContent = raw.length + ' 点' + (raw.length > maxRows ? '（抽样显示）' : '');

    if (typeof TrailAnalysis !== 'undefined') {
      const analysis = sim.lastAnalysis || {
        arcLengthCm: TrailAnalysis.arcLengthCm(raw),
        parametric: TrailAnalysis.parametricSummary(sim, 6),
        message: ''
      };
      this.refreshAnalysisUI(analysis);
    }
  },

  bindToolbar() {
    const pop = document.getElementById('propPopover');
    document.querySelectorAll('.tool-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const tool = btn.dataset.tool;
        if (tool === 'grid') {
          this.sim.showGrid = !this.sim.showGrid;
          this.sim.draw();
          return;
        }
        if (tool === 'axes') {
          this.sim.showAxes = !this.sim.showAxes;
          this.sim.draw();
          return;
        }
        if (tool === 'trail') {
          this.sim.clearTrail();
          this.refreshTrailPanel();
          return;
        }
        if (tool === 'fit') {
          this.sim.resetViewport();
          return;
        }
        if (tool === 'clearAnn') {
          if (typeof Annotations !== 'undefined') Annotations.reset();
          this.sim.draw();
          return;
        }
        if (tool === 'trailList') {
          this.toggleTrailPanel();
          return;
        }
        if (tool === 'props') {
          const show = pop.hidden;
          pop.hidden = !show;
          if (!show) {
            this.setActiveTool('pan');
          } else {
            if (typeof Annotations !== 'undefined') Annotations.cancelPending();
            this.setActiveTool('props');
          }
          return;
        }
        if (pop) pop.hidden = true;
        if (typeof SceneProps !== 'undefined') SceneProps.activeTool = null;
        document.querySelectorAll('.prop-btn').forEach(b => b.classList.remove('active'));
        if (typeof Annotations !== 'undefined' && !Annotations.isAnnotTool(tool)) {
          Annotations.cancelPending();
        }
        this.setActiveTool(tool);
      });
    });
  },

  setActiveTool(tool) {
    this.activeTool = tool;
    const annotate = typeof Annotations !== 'undefined' && Annotations.isAnnotTool(tool);
    document.querySelectorAll('.tool-btn').forEach(b => {
      const t = b.dataset.tool;
      if (t === 'trailList') return;
      b.classList.toggle('active', t === tool);
    });
    const canvas = this.sim.canvas;
    canvas.classList.remove('tool-pan', 'tool-annotate', 'tool-origin', 'dragging');
    if (tool === 'pan') canvas.classList.add('tool-pan');
    if (annotate) canvas.classList.add('tool-annotate');
    if (tool === 'origin') canvas.classList.add('tool-origin');
  },

  _eventWorldPoint(e) {
    if (typeof window.__canvasPoint === 'function') {
      return window.__canvasPoint(e);
    }
    const canvas = this.sim.canvas;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const screenX = (e.clientX - rect.left) * scaleX;
    const screenY = (e.clientY - rect.top) * scaleY;
    return this.sim.screenToWorld(screenX, screenY);
  },

  bindCanvas() {
    const canvas = this.sim.canvas;

    canvas.addEventListener('wheel', e => {
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
      const my = (e.clientY - rect.top) * (canvas.height / rect.height);
      const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
      this.sim.zoomAt(mx, my, factor);
    }, { passive: false });

    canvas.addEventListener('mousedown', e => {
      if (e.button !== 0) return;
      if (this.sim.busy) return;
      if (SceneProps.activeTool) return;
      if (typeof Annotations !== 'undefined' && Annotations.isAnnotTool(this.activeTool)) return;

      const raw = this._eventWorldPoint(e);
      if (this.activeTool === 'origin' || (this.activeTool === 'pan' && this.sim.isNearOrigin(raw.x, raw.y))) {
        if (this.activeTool === 'pan' && !this.sim.isNearOrigin(raw.x, raw.y)) {
          /* fall through to pan */
        } else {
          this._dragOrigin = true;
          canvas.classList.add('dragging');
          return;
        }
      }

      if (this.activeTool !== 'pan') return;
      this._panning = true;
      this._panStart = { x: e.clientX, y: e.clientY, ox: this.sim.viewport.offsetX, oy: this.sim.viewport.offsetY };
      canvas.classList.add('dragging');
    });

    canvas.addEventListener('click', e => {
      if (this.sim.busy) return;
      if (SceneProps.activeTool) return;
      if (typeof Annotations === 'undefined' || !Annotations.isAnnotTool(this.activeTool)) return;

      const raw = this._eventWorldPoint(e);
      const GRID = 50;
      const pt = {
        x: Math.round(raw.x / GRID) * GRID,
        y: Math.round(raw.y / GRID) * GRID
      };
      const result = Annotations.handleClick(pt, e.shiftKey);
      this.sim.draw();

      const status = document.getElementById('statusText');
      if (result === 'deleted' && status) status.textContent = '已删除标注';
      else if (result === 'point' && status) status.textContent = '已添加参考点';
      else if (result === 'segment' && status) status.textContent = '已添加线段';
      else if (result === 'circle' && status) status.textContent = '已添加圆';
      else if (result === 'too-small' && status) status.textContent = '半径过小';
      else if (result === 'pending' && status) {
        const need = this.activeTool === 'circle' ? '圆心已选，请点击半径' : '已选起点，请点击终点';
        status.textContent = need;
      }
    });

    canvas.addEventListener('mousemove', e => {
      if (this.sim.busy) return;
      if (SceneProps.activeTool) return;

      if (typeof Annotations !== 'undefined' && Annotations.isAnnotTool(this.activeTool)) {
        const raw = this._eventWorldPoint(e);
        const GRID = 50;
        Annotations.handleMove({
          x: Math.round(raw.x / GRID) * GRID,
          y: Math.round(raw.y / GRID) * GRID
        });
        if (Annotations.pending || Annotations.hover) this.sim.draw();
      }
    });

    window.addEventListener('mousemove', e => {
      if (this._dragOrigin) {
        const raw = this._eventWorldPoint(e);
        const GRID = 50;
        this.sim.setOrigin(
          Math.round(raw.x / GRID) * GRID,
          Math.round(raw.y / GRID) * GRID
        );
        return;
      }
      if (!this._panning || !this._panStart) return;
      const dx = e.clientX - this._panStart.x;
      const dy = e.clientY - this._panStart.y;
      this.sim.viewport.offsetX = this._panStart.ox + dx;
      this.sim.viewport.offsetY = this._panStart.oy + dy;
      this.sim.draw();
    });

    window.addEventListener('mouseup', () => {
      if (this._dragOrigin) {
        this._dragOrigin = false;
        this.sim.runAnalysis();
        canvas.classList.remove('dragging');
        const st = document.getElementById('statusText');
        if (st) st.textContent = '原点已更新';
      }
      if (this._panning) {
        this._panning = false;
        this._panStart = null;
        canvas.classList.remove('dragging');
      }
    });

    canvas.addEventListener('mouseleave', () => {
      if (typeof Annotations !== 'undefined' && Annotations.hover) {
        Annotations.hover = null;
        if (Annotations.pending) this.sim.draw();
      }
    });
  },

  setTaskSummary(title) {
    const el = document.getElementById('taskSummary');
    if (el) {
      el.textContent = title || '选择课程任务…';
      el.title = title || '';
    }
  },

  refreshAlgebraBar() {
    const s = this.sim?.state;
    if (!s) return;
    const ox = s.startX;
    const oy = s.startY;
    const PX = 5;
    const xCm = ((s.x - ox) / PX).toFixed(1);
    const yCm = ((oy - s.y) / PX).toFixed(1);
    const deg = ((s.angle * 180 / Math.PI) % 360 + 360) % 360;
    const set = (id, v) => {
      const el = document.getElementById(id);
      if (el) el.textContent = v;
    };
    set('algX', xCm);
    set('algY', yCm);
    set('algTheta', deg.toFixed(0));
    if (typeof runStats !== 'undefined') {
      set('algS', runStats.totalDist.toFixed(1));
    }
    if (typeof TrailAnalysis !== 'undefined') {
      const L = this.sim.lastAnalysis
        ? this.sim.lastAnalysis.arcLengthCm
        : TrailAnalysis.arcLengthCm(this.sim.trail);
      set('algL', L.toFixed(1));
    }
    this.refreshTrailPanel();
  },

  refreshAnalysisUI(analysis) {
    const a = analysis || this.sim?.lastAnalysis;
    const arcEl = document.getElementById('trailArcLen');
    const paramEl = document.getElementById('trailParam');
    const matchEl = document.getElementById('trailMatch');
    if (!arcEl) return;
    if (!a) {
      arcEl.textContent = '—';
      if (paramEl) paramEl.textContent = '—';
      if (matchEl) matchEl.innerHTML = '';
      return;
    }
    arcEl.textContent = a.arcLengthCm.toFixed(1) + ' cm';
    if (paramEl) paramEl.textContent = a.parametric || '—';
    if (matchEl) {
      if (a.matchPercent != null) {
        const cls = a.matchPercent >= 85 ? 'good' : a.matchPercent >= 60 ? 'ok' : 'low';
        matchEl.className = 'trail-match ' + cls;
        matchEl.innerHTML = a.message;
      } else {
        matchEl.className = 'trail-match';
        matchEl.textContent = a.message;
      }
    }
  },

  setAlgebraExtra(html) {
    const el = document.getElementById('algExtra');
    if (el) el.innerHTML = html;
  }
};

window.ViewShell = ViewShell;
