/* 路径规划专题 — 巡逻曲线 y=f(x) 与 B 车起点 */
'use strict';

(function () {
  const PRESETS = [
    { label: 'y = 2x（正比例）', expr: '2*x', xMin: 0, xMax: 4 },
    { label: 'y = 0.5x', expr: '0.5*x', xMin: 0, xMax: 5 },
    { label: 'y = 2x + 3', expr: '2*x+3', xMin: 0, xMax: 4 },
    { label: 'y = x²', expr: 'x*x', xMin: 0, xMax: 2.5 },
    { label: 'y = -x² + 8', expr: '-x*x+8', xMin: -2, xMax: 2 },
    { label: 'y = 20/x', expr: '20/x', xMin: 2, xMax: 8 }
  ];

  function tryEval(expr, x) {
    if (window.FunctionPlot?.evalExpr) {
      const y = window.FunctionPlot.evalExpr(expr, { x });
      return Number.isFinite(y) ? y : null;
    }
    try {
      const y = new Function('x', `return (${expr});`)(x);
      return Number.isFinite(y) ? y : null;
    } catch {
      return null;
    }
  }

  function validateExpr(expr, xMin, xMax) {
    if (!expr || !String(expr).trim()) return { ok: false, reason: '请输入表达式' };
    const a = tryEval(expr, xMin);
    const b = tryEval(expr, (xMin + xMax) / 2);
    const c = tryEval(expr, xMax);
    if (a == null || b == null || c == null) {
      return { ok: false, reason: '表达式在区间内无法计算（仅用 x，支持 + - * / 与括号）' };
    }
    return { ok: true };
  }

  function findChaserDef(cfg) {
    const robots = cfg?.robots || [];
    let chaser = robots.find(r => r.role === 'chaser') || robots.find(r => r.id === 'B');
    if (!chaser && robots.length > 1) {
      chaser = robots[1];
      if (!chaser.role) chaser.role = 'chaser';
    }
    return chaser;
  }

  const PlotConfig = {
    PRESETS,

    isEditableTask(task) {
      if (!task || task.mode !== 'curveTravel') return false;
      const up = task.sceneConfig?.userPlot;
      if (up && up.editable === false) return false;
      return up?.editable === true || task.series === 'pathPlan';
    },

    ensureDom() {
      if (this._els) return this._els;
      const bar = document.getElementById('plotConfigBar');
      const expr = document.getElementById('inpPlotExpr');
      const xMin = document.getElementById('inpPlotXMin');
      const xMax = document.getElementById('inpPlotXMax');
      const preset = document.getElementById('selPlotPreset');
      const chaserX = document.getElementById('inpChaserX');
      const chaserY = document.getElementById('inpChaserY');
      const btnOrigin = document.getElementById('btnChaserOrigin');
      const btn = document.getElementById('btnPlotApply');
      if (!bar || !expr) return null;

      preset.innerHTML = '<option value="">— 常用曲线 —</option>'
        + PRESETS.map((p, i) => `<option value="${i}">${p.label}</option>`).join('');

      preset.addEventListener('change', () => {
        const idx = preset.value;
        if (idx === '') return;
        const p = PRESETS[Number(idx)];
        if (!p) return;
        expr.value = p.expr;
        xMin.value = p.xMin;
        xMax.value = p.xMax;
      });

      btnOrigin.addEventListener('click', () => {
        chaserX.value = 0;
        chaserY.value = 0;
        this.applyFromInputs();
      });

      btn.addEventListener('click', () => this.applyFromInputs());

      this._els = { bar, expr, xMin, xMax, preset, chaserX, chaserY, btnOrigin, btn };
      return this._els;
    },

    readInputs() {
      const e = this.ensureDom();
      if (!e) return null;
      return {
        expr: e.expr.value.trim(),
        xMin: parseFloat(e.xMin.value),
        xMax: parseFloat(e.xMax.value),
        chaserX: parseFloat(e.chaserX.value),
        chaserY: parseFloat(e.chaserY.value)
      };
    },

    fillInputs(cfg) {
      const e = this.ensureDom();
      if (!e || !cfg) return;
      const plot = cfg.plot;
      if (plot) {
        e.expr.value = plot.expr || '2*x';
        e.xMin.value = plot.xMin ?? 0;
        e.xMax.value = plot.xMax ?? 4;
        e.preset.value = '';
      }
      const chaser = findChaserDef(cfg);
      e.chaserX.value = chaser?.xCm ?? 0;
      e.chaserY.value = chaser?.yCm ?? 0;
    },

    syncChaserToConfig(cfg, xCm, yCm) {
      if (!cfg.robots) cfg.robots = [];
      let chaser = findChaserDef(cfg);
      if (!chaser) {
        chaser = { id: 'B', label: '拦截车', role: 'chaser', speed: 12, color: '#f97316' };
        cfg.robots.push(chaser);
      }
      chaser.xCm = xCm;
      chaser.yCm = yCm;
      chaser.role = chaser.role || 'chaser';
      return chaser;
    },

    syncPatrolStartToCurve(cfg) {
      if (!window.CurveTravel?.buildPolylineCm || !cfg.plot?.expr) return;
      const pts = window.CurveTravel.buildPolylineCm(cfg.plot, cfg);
      if (!pts.length) return;
      if (!cfg.robots) cfg.robots = [];
      let patrol = cfg.robots.find(r => r.role === 'patrol' || r.id === 'A');
      if (!patrol) {
        patrol = { id: 'A', label: '巡逻车', role: 'patrol', speed: 10, color: '#22d3ee' };
        cfg.robots.push(patrol);
      }
      patrol.xCm = pts[0].x;
      patrol.yCm = pts[0].y;
      patrol.role = patrol.role || 'patrol';
    },

    applyFromInputs() {
      const sim = this._sim;
      if (!sim) return false;
      const raw = this.readInputs();
      if (!raw) return false;
      if (!Number.isFinite(raw.xMin) || !Number.isFinite(raw.xMax) || raw.xMax <= raw.xMin) {
        if (typeof setStatus === 'function') setStatus('x 区间无效：xMax 须大于 xMin', 'err');
        return false;
      }
      const v = validateExpr(raw.expr, raw.xMin, raw.xMax);
      if (!v.ok) {
        if (typeof setStatus === 'function') setStatus(v.reason, 'err');
        return false;
      }
      if (!Number.isFinite(raw.chaserX) || !Number.isFinite(raw.chaserY)) {
        if (typeof setStatus === 'function') setStatus('B 起点坐标请输入有效数字', 'err');
        return false;
      }

      const cfg = sim.sceneConfig || {};
      const plot = cfg.plot || {};
      plot.expr = raw.expr;
      plot.xMin = raw.xMin;
      plot.xMax = raw.xMax;
      plot.label = plot.label?.startsWith('y=') ? `y=${raw.expr}` : raw.expr;
      if (!plot.color) plot.color = '#38bdf8';
      if (!plot.pathStep) plot.pathStep = Math.max(0.2, (raw.xMax - raw.xMin) / 20);
      cfg.plot = plot;
      this.syncChaserToConfig(cfg, raw.chaserX, raw.chaserY);
      this.syncPatrolStartToCurve(cfg);
      sim.sceneConfig = cfg;

      const task = typeof this._getTask === 'function' ? this._getTask() : null;
      const statusMsg = `已应用：y=${raw.expr}，A 在曲线起点 (${cfg.robots?.find(r => r.id === 'A')?.xCm}, ${cfg.robots?.find(r => r.id === 'A')?.yCm})，B (${raw.chaserX}, ${raw.chaserY}) cm`;
      if (sim.busy) {
        if (typeof setStatus === 'function') setStatus('设置已保存（运行结束后演示生效）', 'ok');
      } else {
        if (typeof sim.reloadRobotsFromConfig === 'function') {
          sim.reloadRobotsFromConfig();
        } else {
          sim.reset();
        }
        if (task?.starter?.curveTravelRun && window.__blocklyWorkspace) {
          const hasLegacyGoto = window.__blocklyWorkspace.getBlocksByType('motion_goto_robot', false)
            .some(b => b.getFieldValue('ROBOT') === 'A');
          if (hasLegacyGoto && typeof this._reloadStarter === 'function') {
            this._reloadStarter(task);
            if (typeof setStatus === 'function') {
              setStatus(statusMsg + ' · 已移除旧的 A 顶点 goto，请用「曲线拦截演示」', 'ok');
            }
            return true;
          }
        }
        if (typeof setStatus === 'function') setStatus(statusMsg, 'ok');
      }
      return true;
    },

    bind(sim, getTask, hooks) {
      this._sim = sim;
      this._getTask = getTask;
      this._reloadStarter = hooks?.reloadStarter || null;
      this.ensureDom();
    },

    onTaskLoaded(task) {
      const e = this.ensureDom();
      if (!e) return;
      const show = this.isEditableTask(task);
      e.bar.hidden = !show;
      if (show && task?.sceneConfig) {
        this.fillInputs(task.sceneConfig);
      }
    }
  };

  window.PlotConfig = PlotConfig;
  window.validatePlotExpr = validateExpr;
})();
