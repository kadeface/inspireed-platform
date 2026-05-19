/* 轮式机器人数学融合互动教学 — 主应用 */
(function () {
  'use strict';

  const PX_PER_CM = 5;
  const GRID_STEP = 50; // 1 格 = 10 cm（10 × PX_PER_CM）

  function snapGrid(v) {
    return Math.round(v / GRID_STEP) * GRID_STEP;
  }

  let currentTask = null;
  let runStats = { totalDist: 0, totalTime: 0, turns: [], waits: 0 };

  // ─── 机器人模拟器 ───────────────────────────────────────
  const sim = {
    canvas: null, ctx: null, showGrid: true, busy: false,
    trail: [],
    state: {
      x: GRID_STEP, y: GRID_STEP * 4, angle: 0, dist: 0, speed: 10, wheelAngle: 0,
      startX: GRID_STEP, startY: GRID_STEP * 4, elapsed: 0
    },
    scene: SCENE.PATH,
    sceneConfig: {},

    init() {
      this.canvas = document.getElementById('canvas');
      this.ctx = this.canvas.getContext('2d');
      window.__simRef = this;
      document.getElementById('inpSpeed').addEventListener('input', e => {
        this.state.speed = parseFloat(e.target.value) || 10;
      });
      this.draw();
    },

    diameter() { return parseFloat(document.getElementById('inpDiameter').value) || 3; },

    reset() {
      const s = this.state;
      s.x = s.startX; s.y = s.startY; s.angle = 0; s.dist = 0;
      s.wheelAngle = 0; s.elapsed = 0;
      this.trail = [{ x: s.x, y: s.y }];
      this.busy = false;
      runStats = { totalDist: 0, totalTime: 0, turns: [], waits: 0 };
      this.draw();
      this.updateTelemetry();
    },

    setScene(scene, config) {
      this.scene = scene || SCENE.PATH;
      this.sceneConfig = config || {};
      const h = this.canvas.height;
      const w = this.canvas.width;
      const midY = snapGrid(h / 2);

      if (this.scene === SCENE.GRID) {
        // 数对网格原点 (1,1) 落在背景网格交点
        this.state.startX = GRID_STEP;
        this.state.startY = snapGrid(h - GRID_STEP);
      } else if (this.scene === SCENE.NUMBERLINE) {
        this.state.startX = snapGrid(w / 2);
        this.state.startY = midY;
        this.state.angle = 0;
      } else {
        this.state.startX = GRID_STEP;
        this.state.startY = midY;
      }
      this.reset();
    },

    getNumberLineUnitPx() {
      const cfg = this.sceneConfig;
      const min = cfg.min ?? -10;
      const max = cfg.max ?? 10;
      const unitCm = cfg.unitCm || 20;
      const span = max - min;
      const idealUnitPx = (unitCm / 10) * GRID_STEP;
      const available = this.canvas.width - 72;
      return span * idealUnitPx > available ? available / span : idealUnitPx;
    },

    wait(ms) { return new Promise(res => setTimeout(res, ms)); },

    async forward(cm) {
      const s = this.state;
      let pxPerCm = PX_PER_CM;
      if (this.scene === SCENE.NUMBERLINE) {
        const unitCm = this.sceneConfig.unitCm || 20;
        pxPerCm = this.getNumberLineUnitPx() / unitCm;
      }
      const dx = cm * pxPerCm * Math.cos(s.angle);
      const dy = cm * pxPerCm * Math.sin(s.angle);
      const x0 = s.x, y0 = s.y;
      const dur = Math.max(200, (Math.abs(cm) / s.speed) * 1000);
      const t0 = performance.now();
      runStats.totalDist += Math.abs(cm);
      while (true) {
        const p = Math.min(1, (performance.now() - t0) / dur);
        s.x = x0 + dx * p;
        s.y = y0 + dy * p;
        s.dist += Math.abs(cm) * (p - (s._lastP || 0));
        s._lastP = p;
        s.wheelAngle += Math.abs(cm) * PX_PER_CM * 0.06 * Math.sign(cm || 1);
        s.elapsed += dur * (p - (s._lastTp || 0)) / 1000;
        s._lastTp = p;
        if (p > 0.01) this.trail.push({ x: s.x, y: s.y });
        this.draw();
        this.updateTelemetry();
        if (p >= 1) break;
        await this.wait(16);
      }
      s.dist = runStats.totalDist;
      s._lastP = 0; s._lastTp = 0;
      runStats.totalTime += dur / 1000;
      this.draw();
      this.updateTelemetry();
    },

    async backward(cm) { return this.forward(-cm); },

    async turn(deg) {
      const s = this.state;
      const target = s.angle + deg * Math.PI / 180;
      const a0 = s.angle;
      const dur = Math.min(1200, Math.abs(deg) * 8);
      const t0 = performance.now();
      runStats.turns.push(deg);
      while (true) {
        const p = Math.min(1, (performance.now() - t0) / dur);
        s.angle = a0 + (target - a0) * p;
        this.draw();
        if (p >= 1) break;
        await this.wait(16);
      }
      s.elapsed += dur / 1000;
      runStats.totalTime += dur / 1000;
    },

    setSpeed(v) {
      this.state.speed = v;
      document.getElementById('inpSpeed').value = v;
    },

    updateTelemetry() {
      const C = Math.PI * this.diameter();
      const n = C > 0 ? (runStats.totalDist / C).toFixed(2) : '0';
      let html = '<strong>实时数据</strong><br>' +
        '总行进：<strong>' + runStats.totalDist.toFixed(1) + ' cm</strong><br>' +
        '轮周长：' + C.toFixed(2) + ' cm · 约 ' + n + ' 圈';
      if (runStats.totalTime > 0) {
        html += '<br>用时：' + runStats.totalTime.toFixed(1) + ' 秒';
        if (runStats.totalDist > 0) {
          html += ' · 均速：' + (runStats.totalDist / runStats.totalTime).toFixed(1) + ' cm/s';
        }
      }
      if (runStats.turns.length) {
        html += '<br>累计转角：' + runStats.turns.map(t => t + '°').join('、');
      }
      document.getElementById('telemetry').innerHTML = html;
    },

    draw() {
      const { ctx, canvas } = this;
      const r = this.state;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (this.showGrid) this.drawGrid();
      this.drawScene();
      if (typeof SceneProps !== 'undefined') SceneProps.draw(this.ctx, this);
      this.drawTrail();
      this.drawRobot(r);
      if (this.scene === SCENE.TIME) this.drawClock();
    },

    drawGrid() {
      const { ctx, canvas } = this;
      const sx = this.state.startX;
      const sy = this.state.startY;
      ctx.strokeStyle = 'rgba(148,163,184,.2)';
      ctx.lineWidth = 1;
      for (let x = 0; x <= canvas.width; x += GRID_STEP) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
      }
      for (let y = 0; y <= canvas.height; y += GRID_STEP) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
      }
      // 起点标记
      ctx.fillStyle = 'rgba(13,148,136,0.85)';
      ctx.beginPath();
      ctx.arc(sx, sy, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#5eead4';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(sx, sy, 8, 0, Math.PI * 2);
      ctx.stroke();
      ctx.fillStyle = 'rgba(148,163,184,.55)';
      ctx.font = '10px sans-serif';
      if (this.scene !== SCENE.NUMBERLINE) {
        for (let x = GRID_STEP; x < canvas.width; x += GRID_STEP) {
          ctx.fillText((x / PX_PER_CM) + '', x - 6, canvas.height - 4);
        }
      }
      ctx.fillStyle = 'rgba(13,148,136,.75)';
      ctx.font = '600 9px sans-serif';
      ctx.fillText('起点', sx + 10, sy - 10);
    },

    drawScene() {
      const cfg = this.sceneConfig;
      const { ctx, canvas } = this;

      if (this.scene === SCENE.DISTANCE && cfg.markers) {
        const baseY = this.state.startY;
        cfg.markers.forEach(cm => {
          const x = this.state.startX + cm * PX_PER_CM;
          ctx.strokeStyle = '#f97316';
          ctx.lineWidth = 2;
          ctx.setLineDash([4, 4]);
          ctx.beginPath(); ctx.moveTo(x, baseY - 40); ctx.lineTo(x, baseY + 40); ctx.stroke();
          ctx.setLineDash([]);
          ctx.fillStyle = '#fbbf24';
          ctx.font = '600 11px Outfit, sans-serif';
          ctx.fillText(cm + 'cm', x - 14, baseY - 48);
        });
      }

      if (this.scene === SCENE.ANGLE || cfg.showCross) {
        const cx = this.state.startX, cy = this.state.startY;
        ctx.strokeStyle = 'rgba(13,148,136,.5)';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(cx - 50, cy); ctx.lineTo(cx + 50, cy); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(cx, cy - 50); ctx.lineTo(cx, cy + 50); ctx.stroke();
      }

      if (this.scene === SCENE.PERIMETER) {
        if (cfg.square) this.drawRectOutline(cfg.square.side, cfg.square.side, '#06b6d4');
        if (cfg.rect) this.drawRectOutline(cfg.rect.w, cfg.rect.h, '#06b6d4');
      }

      if (this.scene === SCENE.SHAPE && cfg.shape === 'square' && cfg.side) {
        this.drawRectOutline(cfg.side, cfg.side, '#a78bfa');
      }

      if (this.scene === SCENE.GRID) {
        const cols = cfg.cols || 6, rows = cfg.rows || 6;
        const cell = (cfg.cellCm || 10) * PX_PER_CM;
        const ox = this.state.startX;
        const oy = this.state.startY;
        ctx.strokeStyle = 'rgba(148,163,184,.35)';
        for (let c = 0; c <= cols; c++) {
          ctx.beginPath(); ctx.moveTo(ox + c * cell, oy); ctx.lineTo(ox + c * cell, oy - rows * cell); ctx.stroke();
        }
        for (let row = 0; row <= rows; row++) {
          ctx.beginPath(); ctx.moveTo(ox, oy - row * cell); ctx.lineTo(ox + cols * cell, oy - row * cell); ctx.stroke();
        }
        ctx.fillStyle = 'rgba(148,163,184,.6)';
        ctx.font = '10px sans-serif';
        for (let c = 1; c <= cols; c++) ctx.fillText(c, ox + (c - 0.5) * cell - 3, oy + 14);
        for (let row = 1; row <= rows; row++) ctx.fillText(row, ox - 16, oy - (row - 0.5) * cell + 3);
        if (cfg.target) {
          const [tc, tr] = cfg.target;
          ctx.fillStyle = 'rgba(249,115,22,.35)';
          ctx.fillRect(ox + (tc - 1) * cell, oy - tr * cell, cell, cell);
          ctx.fillStyle = '#fbbf24';
          ctx.font = '600 12px sans-serif';
          ctx.fillText('(' + tc + ',' + tr + ')', ox + (tc - 1) * cell + 4, oy - (tr - 0.5) * cell + 4);
        }
      }

      if (this.scene === SCENE.NUMBERLINE) {
        this.drawNumberLine(cfg, canvas);
      }

      if (this.scene === SCENE.CIRCLE) {
        const rad = (cfg.radius || 40) * PX_PER_CM;
        const cx = this.state.startX, cy = this.state.startY;
        ctx.strokeStyle = 'rgba(167,139,250,.45)';
        ctx.lineWidth = 2;
        ctx.setLineDash([6, 4]);
        ctx.beginPath(); ctx.arc(cx, cy, rad, 0, Math.PI * 2); ctx.stroke();
        ctx.setLineDash([]);
      }

      if (this.scene === SCENE.DATA) {
        ctx.fillStyle = 'rgba(255,255,255,.08)';
        ctx.fillRect(12, 12, 140, 60);
        ctx.fillStyle = '#94a3b8';
        ctx.font = '11px sans-serif';
        ctx.fillText('数据统计模式', 20, 32);
        ctx.fillText('运行后查看总距离', 20, 50);
        ctx.fillText('与平均/次数', 20, 66);
      }
    },

    drawNumberLine(cfg, canvas) {
      const ctx = this.ctx;
      const min = cfg.min ?? -10;
      const max = cfg.max ?? 10;
      const unitCm = cfg.unitCm || 20;
      const cy = this.state.startY;
      const originX = this.state.startX;
      const pad = 36;
      const span = max - min;
      const unitPx = this.getNumberLineUnitPx();
      const scaled = unitPx < (unitCm / 10) * GRID_STEP;
      const left = originX + min * unitPx;
      const right = originX + max * unitPx;

      ctx.strokeStyle = '#64748b';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(Math.max(pad, left - 20), cy);
      ctx.lineTo(Math.min(canvas.width - pad, right + 30), cy);
      ctx.stroke();

      ctx.fillStyle = '#94a3b8';
      ctx.beginPath();
      ctx.moveTo(Math.min(canvas.width - pad, right + 30), cy);
      ctx.lineTo(Math.min(canvas.width - pad, right + 30) - 10, cy - 5);
      ctx.lineTo(Math.min(canvas.width - pad, right + 30) - 10, cy + 5);
      ctx.closePath();
      ctx.fill();
      ctx.fillStyle = '#cbd5e1';
      ctx.font = '600 10px sans-serif';
      ctx.fillText('正方向 →', Math.min(canvas.width - pad, right + 34), cy + 4);

      const labelStep = unitPx >= 40 ? 1 : unitPx >= 24 ? 2 : 5;
      ctx.fillStyle = '#e2e8f0';
      ctx.font = '11px Outfit, Noto Sans SC, sans-serif';
      ctx.strokeStyle = '#94a3b8';
      ctx.lineWidth = 1.5;

      for (let i = min; i <= max; i++) {
        const x = originX + i * unitPx;
        if (x < pad - 5 || x > canvas.width - pad + 5) continue;
        const major = i % labelStep === 0 || i === 0;
        const tick = major ? 10 : 6;
        ctx.beginPath();
        ctx.moveTo(x, cy - tick);
        ctx.lineTo(x, cy + tick);
        ctx.stroke();
        if (major) {
          const text = i > 0 ? '+' + i : String(i);
          ctx.fillText(text, x - (i > 9 || i < -9 ? 10 : 6), cy + 24);
        }
      }

      ctx.fillStyle = '#5eead4';
      ctx.font = '600 11px sans-serif';
      ctx.fillText('O 原点', originX - 14, cy - 16);

      ctx.fillStyle = 'rgba(148,163,184,.75)';
      ctx.font = '10px sans-serif';
      const unitLabel = '1 单位 = ' + unitCm + ' cm' + (scaled ? '（显示缩放）' : ' = 2 格');
      ctx.fillText(unitLabel, pad, 18);
    },

    drawRectOutline(wCm, hCm, color) {
      const ox = this.state.startX, oy = this.state.startY;
      const w = wCm * PX_PER_CM, h = hCm * PX_PER_CM;
      this.ctx.strokeStyle = color || '#06b6d4';
      this.ctx.lineWidth = 2;
      this.ctx.setLineDash([8, 5]);
      this.ctx.strokeRect(ox, oy - h, w, h);
      this.ctx.setLineDash([]);
    },

    drawTrail() {
      if (this.trail.length < 2) return;
      const { ctx } = this;
      ctx.beginPath();
      ctx.moveTo(this.trail[0].x, this.trail[0].y);
      for (let i = 1; i < this.trail.length; i++) ctx.lineTo(this.trail[i].x, this.trail[i].y);
      ctx.strokeStyle = '#f97316';
      ctx.lineWidth = 2.5;
      ctx.stroke();
    },

    drawClock() {
      const cx = this.canvas.width - 70, cy = 55, r = 38;
      const { ctx } = this;
      ctx.fillStyle = 'rgba(255,255,255,.12)';
      ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#94a3b8'; ctx.lineWidth = 2;
      ctx.stroke();
      const sec = (runStats.totalTime % 60) / 60 * Math.PI * 2 - Math.PI / 2;
      ctx.strokeStyle = '#f97316'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.cos(sec) * (r - 8), cy + Math.sin(sec) * (r - 8)); ctx.stroke();
      ctx.fillStyle = '#e2e8f0'; ctx.font = '10px sans-serif';
      ctx.fillText(runStats.totalTime.toFixed(1) + 's', cx - 14, cy + r + 14);
    },

    drawWheel(ctx, lx, ly, radius, spin) {
      ctx.save();
      ctx.translate(lx, ly);
      ctx.fillStyle = '#0f172a';
      ctx.beginPath();
      ctx.arc(0, 0, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.rotate(spin);
      ctx.strokeStyle = '#64748b';
      ctx.lineWidth = 1.2;
      for (let i = 0; i < 6; i++) {
        ctx.beginPath();
        ctx.moveTo(radius * 0.35, 0);
        ctx.lineTo(radius * 0.92, 0);
        ctx.stroke();
        ctx.rotate(Math.PI / 3);
      }
      ctx.fillStyle = '#94a3b8';
      ctx.beginPath();
      ctx.arc(0, 0, radius * 0.32, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    },

    roundRect(ctx, x, y, w, h, rad) {
      ctx.beginPath();
      ctx.moveTo(x + rad, y);
      ctx.lineTo(x + w - rad, y);
      ctx.quadraticCurveTo(x + w, y, x + w, y + rad);
      ctx.lineTo(x + w, y + h - rad);
      ctx.quadraticCurveTo(x + w, y + h, x + w - rad, y + h);
      ctx.lineTo(x + rad, y + h);
      ctx.quadraticCurveTo(x, y + h, x, y + h - rad);
      ctx.lineTo(x, y + rad);
      ctx.quadraticCurveTo(x, y, x + rad, y);
      ctx.closePath();
    },

    /** 俯视图轮式机器人（车头朝 +x，差速左右轮） */
    drawRobot(r) {
      const ctx = this.ctx;
      const bodyL = 40;
      const bodyW = 28;
      const wheelR = 7.5;
      const track = 17;

      ctx.save();
      ctx.translate(r.x, r.y);
      ctx.rotate(r.angle);
      ctx.shadowColor = 'rgba(0,0,0,0.45)';
      ctx.shadowBlur = 10;
      ctx.shadowOffsetY = 3;

      // 左右驱动轮（俯视图在车身两侧）
      this.drawWheel(ctx, -5, -track, wheelR, r.wheelAngle);
      this.drawWheel(ctx, -5, track, wheelR, r.wheelAngle);

      ctx.shadowBlur = 0;

      // 底盘
      const g = ctx.createLinearGradient(-bodyL / 2, 0, bodyL / 2, 0);
      g.addColorStop(0, '#0f766e');
      g.addColorStop(0.45, '#14b8a6');
      g.addColorStop(1, '#2dd4bf');
      ctx.fillStyle = g;
      this.roundRect(ctx, -bodyL / 2 + 4, -bodyW / 2, bodyL - 6, bodyW, 7);
      ctx.fill();
      ctx.strokeStyle = '#065f46';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // 前面板
      ctx.fillStyle = '#115e59';
      this.roundRect(ctx, bodyL / 2 - 10, -bodyW / 2 + 2, 8, bodyW - 4, 3);
      ctx.fill();

      // 车头保险杠 + 方向指示
      ctx.fillStyle = '#f97316';
      ctx.beginPath();
      ctx.moveTo(bodyL / 2 + 2, -9);
      ctx.lineTo(bodyL / 2 + 14, 0);
      ctx.lineTo(bodyL / 2 + 2, 9);
      ctx.closePath();
      ctx.fill();

      ctx.fillStyle = 'rgba(251,191,36,0.95)';
      ctx.beginPath();
      ctx.moveTo(bodyL / 2 - 4, 0);
      ctx.lineTo(bodyL / 2 - 16, -6);
      ctx.lineTo(bodyL / 2 - 16, 6);
      ctx.closePath();
      ctx.fill();

      // 前万向轮
      ctx.fillStyle = '#334155';
      ctx.strokeStyle = '#64748b';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(bodyL / 2 - 8, 0, 3.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // 主控/传感器模块（俯视圆盘）
      ctx.fillStyle = '#1e293b';
      ctx.beginPath();
      ctx.arc(0, 0, 9, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.fillStyle = '#22d3ee';
      ctx.beginPath();
      ctx.arc(2, -2, 3.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,0.75)';
      ctx.beginPath();
      ctx.arc(1, -3, 1.2, 0, Math.PI * 2);
      ctx.fill();

      // 尾部装饰条
      ctx.fillStyle = '#64748b';
      ctx.fillRect(-bodyL / 2 + 4, -3, 5, 6);

      ctx.restore();
    },

    async runDemo(name) {
      const d = this.diameter();
      const demos = {
        forward100: () => this.forward(100),
        forward10: () => this.forward(10),
        forward80: () => this.forward(80),
        forward50: () => this.forward(50),
        turn90: () => this.turn(90),
        turn45: () => this.turn(45),
        waitDemo: async () => { await this.wait(3000); await this.forward(30); },
        square40: async () => { for (let i = 0; i < 4; i++) { await this.forward(40); await this.turn(90); } },
        square30: async () => { for (let i = 0; i < 4; i++) { await this.forward(30); await this.turn(90); } },
        oneLap: () => this.forward(Math.PI * d),
        division17: async () => { for (let i = 0; i < 3; i++) await this.forward(20); await this.forward(20); },
        speedRace: async () => { this.setSpeed(10); await this.forward(50); this.reset(); this.setSpeed(20); await this.forward(50); },
        grid32: async () => { await this.forward(20); await this.turn(90); await this.forward(10); },
        grid43: async () => { await this.forward(30); await this.turn(90); await this.forward(20); },
        numberline: async () => { await this.forward(100); await this.backward(60); },
        triangle: async () => { for (let i = 0; i < 3; i++) { await this.forward(40); await this.turn(120); } },
        hexagon: async () => { for (let i = 0; i < 6; i++) { await this.forward(25); await this.turn(60); } },
        planting: async () => { for (let i = 0; i < 5; i++) { await this.forward(20); await this.wait(500); } },
        comprehensive: async () => { await this.forward(50); await this.turn(90); await this.forward(50); await this.turn(90); await this.forward(50); }
      };
      if (demos[name]) await demos[name]();
      else if (name === 'forward100') await this.forward(100);
      else await this.forward(Math.PI * d);
    }
  };

  window.__robot = {
    forward: cm => sim.forward(cm),
    backward: cm => sim.forward(-cm),
    turn: deg => sim.turn(deg),
    turnLeft: deg => sim.turn(-deg),
    turnRight: deg => sim.turn(deg),
    setSpeed: v => { sim.setSpeed(v); },
    wait: sec => { runStats.waits++; return sim.wait(sec * 1000); },
    stop: () => {}
  };

  // ─── Blockly ───────────────────────────────────────────
  const blocklyApp = {
    workspace: null,

    defineBlocks() {
      const J = Blockly.JavaScript;
      Blockly.defineBlocksWithJsonArray([
        { type: 'event_start', message0: '当程序开始时', nextStatement: true, colour: 120, hat: 'cap' },
        { type: 'motion_forward', message0: '前进 %1 厘米', args0: [{ type: 'input_value', name: 'D', check: 'Number' }],
          previousStatement: true, nextStatement: true, colour: 160 },
        { type: 'motion_backward', message0: '后退 %1 厘米', args0: [{ type: 'input_value', name: 'D', check: 'Number' }],
          previousStatement: true, nextStatement: true, colour: 160 },
        { type: 'motion_turn_right', message0: '右转 %1 度', args0: [{ type: 'input_value', name: 'A', check: 'Number' }],
          previousStatement: true, nextStatement: true, colour: 280 },
        { type: 'motion_turn_left', message0: '左转 %1 度', args0: [{ type: 'input_value', name: 'A', check: 'Number' }],
          previousStatement: true, nextStatement: true, colour: 280 },
        { type: 'motion_speed', message0: '设置速度 %1', args0: [{ type: 'input_value', name: 'S', check: 'Number' }],
          previousStatement: true, nextStatement: true, colour: 120 },
        { type: 'motion_wait', message0: '等待 %1 秒', args0: [{ type: 'input_value', name: 'T', check: 'Number' }],
          previousStatement: true, nextStatement: true, colour: 60 },
        { type: 'control_repeat', message0: '重复 %1 次', args0: [{ type: 'input_value', name: 'N', check: 'Number' }],
          message1: '%1', args1: [{ type: 'input_statement', name: 'DO' }],
          previousStatement: true, nextStatement: true, colour: 65 },
        { type: 'control_if', message0: '如果 %1 那么', args0: [{ type: 'input_value', name: 'COND', check: 'Boolean' }],
          message1: '%1', args1: [{ type: 'input_statement', name: 'DO' }],
          previousStatement: true, nextStatement: true, colour: 210 },
        { type: 'robot_logic_compare', message0: '%1 %2 %3',
          args0: [
            { type: 'input_value', name: 'A', check: 'Number' },
            { type: 'field_dropdown', name: 'OP', options: [['=', 'EQ'], ['>', 'GT'], ['<', 'LT']] },
            { type: 'input_value', name: 'B', check: 'Number' }
          ], output: 'Boolean', colour: 210 },
        { type: 'math_num', message0: '%1', args0: [{ type: 'field_number', name: 'N', value: 10 }],
          output: 'Number', colour: 230 },
        { type: 'math_op', message0: '%1 %2 %3',
          args0: [
            { type: 'input_value', name: 'A', check: 'Number' },
            { type: 'field_dropdown', name: 'OP', options: [['+', 'ADD'], ['-', 'MINUS'], ['×', 'MUL'], ['÷', 'DIV']] },
            { type: 'input_value', name: 'B', check: 'Number' }
          ], output: 'Number', colour: 230 },
        { type: 'math_pi', message0: 'π', output: 'Number', colour: 230 }
      ]);

      const gen = (type, fn) => { J.forBlock = J.forBlock || {}; J.forBlock[type] = fn; if (!J[type]) J[type] = fn; };

      gen('event_start', () => '');
      gen('motion_forward', b => `await __robot.forward(${J.valueToCode(b, 'D', J.ORDER_NONE) || 0});\n`);
      gen('motion_backward', b => `await __robot.backward(${J.valueToCode(b, 'D', J.ORDER_NONE) || 0});\n`);
      gen('motion_turn_right', b => `await __robot.turnRight(${J.valueToCode(b, 'A', J.ORDER_NONE) || 0});\n`);
      gen('motion_turn_left', b => `await __robot.turnLeft(${J.valueToCode(b, 'A', J.ORDER_NONE) || 0});\n`);
      gen('motion_speed', b => `__robot.setSpeed(${J.valueToCode(b, 'S', J.ORDER_NONE) || 10});\n`);
      gen('motion_wait', b => `await __robot.wait(${J.valueToCode(b, 'T', J.ORDER_NONE) || 1});\n`);
      gen('control_repeat', b => {
        const n = J.valueToCode(b, 'N', J.ORDER_NONE) || 0;
        return `for (let __i = 0; __i < ${n}; __i++) {\n${J.statementToCode(b, 'DO')}}\n`;
      });
      gen('control_if', b => {
        const c = J.valueToCode(b, 'COND', J.ORDER_NONE) || 'false';
        return `if (${c}) {\n${J.statementToCode(b, 'DO')}}\n`;
      });
      gen('robot_logic_compare', b => {
        const a = J.valueToCode(b, 'A', J.ORDER_NONE) || 0;
        const op = b.getFieldValue('OP');
        const bb = J.valueToCode(b, 'B', J.ORDER_NONE) || 0;
        const map = { EQ: '===', GT: '>', LT: '<' };
        return [`${a} ${map[op]} ${bb}`, J.ORDER_RELATIONAL];
      });
      gen('math_num', b => [String(b.getFieldValue('N')), J.ORDER_ATOMIC]);
      gen('math_op', b => {
        const a = J.valueToCode(b, 'A', J.ORDER_NONE) || 0;
        const bb = J.valueToCode(b, 'B', J.ORDER_NONE) || 0;
        const map = { ADD: '+', MINUS: '-', MUL: '*', DIV: '/' };
        return [`(${a} ${map[b.getFieldValue('OP')]} ${bb})`, J.ORDER_ATOMIC];
      });
      gen('math_pi', () => ['Math.PI', J.ORDER_ATOMIC]);
    },

    chainFromStart() {
      const starts = this.workspace.getBlocksByType('event_start', false);
      if (!starts.length) return '';
      let code = '', block = starts[0].getNextBlock();
      const J = Blockly.JavaScript;
      while (block) {
        const chunk = J.blockToCode(block);
        code += typeof chunk === 'string' ? chunk : chunk[0];
        block = block.getNextBlock();
      }
      return code;
    },

    generate() {
      let code = this.chainFromStart();
      if (!code.trim()) code = Blockly.JavaScript.workspaceToCode(this.workspace).trim();
      return code;
    },

    init() {
      this.defineBlocks();
      this.workspace = Blockly.inject('blockly', {
        toolbox: `<xml>
          <category name="事件" colour="120"><block type="event_start"></block></category>
          <category name="运动" colour="160">
            <block type="motion_forward"><value name="D"><shadow type="math_num"><field name="N">30</field></shadow></value></block>
            <block type="motion_backward"><value name="D"><shadow type="math_num"><field name="N">20</field></shadow></value></block>
            <block type="motion_turn_right"><value name="A"><shadow type="math_num"><field name="N">90</field></shadow></value></block>
            <block type="motion_turn_left"><value name="A"><shadow type="math_num"><field name="N">90</field></shadow></value></block>
          </category>
          <category name="控制" colour="65">
            <block type="control_repeat"><value name="N"><shadow type="math_num"><field name="N">4</field></shadow></value></block>
            <block type="control_if"></block>
            <block type="motion_speed"><value name="S"><shadow type="math_num"><field name="N">10</field></shadow></value></block>
            <block type="motion_wait"><value name="T"><shadow type="math_num"><field name="N">1</field></shadow></value></block>
          </category>
          <category name="逻辑" colour="210"><block type="robot_logic_compare"></block></category>
          <category name="数学" colour="230">
            <block type="math_num"></block>
            <block type="math_op"></block>
            <block type="math_pi"></block>
          </category>
        </xml>`,
        grid: { spacing: 20, length: 3, colour: '#d4dde8', snap: true },
        zoom: { controls: true, wheel: true, startScale: 1, maxScale: 2.5, minScale: 0.4 },
        trashcan: true
      });
      if (typeof Blockly.JavaScript.init === 'function') {
        Blockly.JavaScript.init(this.workspace);
      }
      window.addEventListener('resize', () => Blockly.svgResize(this.workspace));
    },

    loadStarter(task) {
      this.workspace.clear();
      const xmlStr = buildStarterXml(task.starter);
      if (!xmlStr) return;
      const xml = Blockly.utils.xml.textToDom(xmlStr);
      Blockly.Xml.domToWorkspace(xml, this.workspace);
    }
  };

  function canvasPoint(e) {
    const rect = sim.canvas.getBoundingClientRect();
    const sx = sim.canvas.width / rect.width;
    const sy = sim.canvas.height / rect.height;
    return {
      x: snapGrid((e.clientX - rect.left) * sx),
      y: snapGrid((e.clientY - rect.top) * sy)
    };
  }

  function updateCanvasCursor() {
    const c = sim.canvas;
    c.classList.remove('prop-place', 'prop-erase');
    if (SceneProps.activeTool === 'erase') c.classList.add('prop-erase');
    else if (SceneProps.activeTool) c.classList.add('prop-place');
  }

  function selectPropTool(key) {
    SceneProps.activeTool = SceneProps.activeTool === key ? null : key;
    document.querySelectorAll('.prop-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.prop === SceneProps.activeTool);
    });
    updateCanvasCursor();
    if (!SceneProps.activeTool) {
      SceneProps.hover = null;
      sim.draw();
    }
  }

  function loadTaskProps() {
    if (!currentTask) return;
    SceneProps.reset(SceneProps.presetsForTask(currentTask, sim));
    sim.draw();
  }

  function initPropUI() {
    const tools = document.getElementById('propTools');
    Object.entries(PROP_CATALOG).forEach(([key, def]) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'prop-btn';
      btn.dataset.prop = key;
      btn.textContent = def.icon + ' ' + def.name;
      btn.addEventListener('click', () => selectPropTool(key));
      tools.appendChild(btn);
    });
    const erase = document.createElement('button');
    erase.type = 'button';
    erase.className = 'prop-btn erase';
    erase.dataset.prop = 'erase';
    erase.textContent = '🗑 删除';
    erase.addEventListener('click', () => selectPropTool('erase'));
    tools.appendChild(erase);

    sim.canvas.addEventListener('click', e => {
      if (sim.busy) return;
      const pt = canvasPoint(e);
      if (e.shiftKey || SceneProps.activeTool === 'erase') {
        if (SceneProps.removeAt(pt.x, pt.y)) {
          sim.draw();
          setStatus('已删除道具');
        }
        return;
      }
      if (!SceneProps.activeTool) return;
      SceneProps.add(SceneProps.activeTool, pt.x, pt.y);
      sim.draw();
      setStatus('已放置：' + PROP_CATALOG[SceneProps.activeTool].name);
    });

    sim.canvas.addEventListener('mousemove', e => {
      if (!SceneProps.activeTool || SceneProps.activeTool === 'erase' || sim.busy) {
        if (SceneProps.hover) { SceneProps.hover = null; sim.draw(); }
        return;
      }
      SceneProps.hover = canvasPoint(e);
      sim.draw();
    });

    sim.canvas.addEventListener('mouseleave', () => {
      if (SceneProps.hover) {
        SceneProps.hover = null;
        sim.draw();
      }
    });
  }

  // ─── UI ────────────────────────────────────────────────
  function setStatus(msg, type) {
    document.getElementById('statusText').textContent = msg;
    const dot = document.getElementById('statusDot');
    dot.className = 'dot' + (type === 'busy' ? ' busy' : type === 'err' ? ' err' : '');
  }

  function getCurrentTask() {
    const stage = CURRICULUM[document.getElementById('selStage').value];
    const grade = stage.grades[document.getElementById('selGrade').value];
    return grade.tasks[parseInt(document.getElementById('selTask').value, 10)];
  }

  function renderTask(task) {
    currentTask = task;
    document.getElementById('taskTitle').textContent = task.title;
    document.getElementById('taskTags').innerHTML = (task.tags || [])
      .map(t => `<span class="tag">${t}</span>`).join('');
    let body = '';
    if (task.unit) body += `<h4>教材单元</h4><p>${task.unit}</p>`;
    if (task.focus) body += `<h4>探究主线</h4><p>${task.focus}</p>`;
    if (task.goals?.length) {
      body += '<h4>教学目标</h4><ul>' + task.goals.map(g => `<li>${g}</li>`).join('') + '</ul>';
    }
    if (task.hint) body += `<h4>编程提示</h4><p>${task.hint}</p>`;
    document.getElementById('taskBody').innerHTML = body;

    const fArea = document.getElementById('formulaArea');
    fArea.innerHTML = (task.formulas || DEFAULT_FORMULAS)
      .map(f => `<div class="formula"><b>${f.title}</b>${f.tex}</div>`).join('');

    const cBox = document.getElementById('challengeBox');
    const cList = document.getElementById('challengeList');
    if (task.challenges?.length) {
      cBox.style.display = 'block';
      cList.innerHTML = task.challenges.map(c => `<li>${c}</li>`).join('');
    } else {
      cBox.style.display = 'none';
    }

    sim.setScene(task.scene, task.sceneConfig);
    loadTaskProps();
    blocklyApp.loadStarter(task);
    if (window.MathJax?.typesetPromise) MathJax.typesetPromise();
    setStatus('已加载：' + task.title);
  }

  function fillSelectors() {
    const stageSel = document.getElementById('selStage');
    Object.entries(CURRICULUM).forEach(([k, v]) => {
      const o = document.createElement('option');
      o.value = k; o.textContent = v.name; stageSel.appendChild(o);
    });
    stageSel.addEventListener('change', refreshGrades);
    document.getElementById('selGrade').addEventListener('change', refreshTasks);
    document.getElementById('selTask').addEventListener('change', () => renderTask(getCurrentTask()));
    refreshGrades();
  }

  function refreshGrades() {
    const stage = CURRICULUM[document.getElementById('selStage').value];
    const gSel = document.getElementById('selGrade');
    gSel.innerHTML = '';
    Object.entries(stage.grades).forEach(([k, g]) => {
      const o = document.createElement('option');
      o.value = k; o.textContent = g.name; gSel.appendChild(o);
    });
    refreshTasks();
  }

  function refreshTasks() {
    const stage = CURRICULUM[document.getElementById('selStage').value];
    const grade = stage.grades[document.getElementById('selGrade').value];
    const tSel = document.getElementById('selTask');
    tSel.innerHTML = '';
    grade.tasks.forEach((t, i) => {
      const o = document.createElement('option');
      o.value = i; o.textContent = t.title; tSel.appendChild(o);
    });
    renderTask(grade.tasks[0]);
  }

  async function runProgram() {
    if (sim.busy) { setStatus('运行中，请稍候', 'busy'); return; }
    sim.reset();
    const code = blocklyApp.generate();
    document.getElementById('codeOut').textContent = code || '（无代码）';
    document.getElementById('codeOut').classList.add('show');
    if (!code || !/__robot\./.test(code)) {
      setStatus('请把运动积木接在「当程序开始时」下方', 'err');
      return;
    }
    sim.state.speed = parseFloat(document.getElementById('inpSpeed').value) || 10;
    try {
      sim.busy = true;
      setStatus('程序运行中…', 'busy');
      await new Function('return (async () => {\n' + code + '\n})();')();
      setStatus('运行完成 — 总距离 ' + runStats.totalDist.toFixed(1) + ' cm', 'ok');
    } catch (e) {
      setStatus('错误: ' + e.message, 'err');
      console.error(e);
    } finally {
      sim.busy = false;
    }
  }

  async function startDemo() {
    if (sim.busy) return;
    const code = blocklyApp.generate();
    if (code && /__robot\./.test(code)) { await runProgram(); return; }
    sim.reset();
    sim.state.speed = parseFloat(document.getElementById('inpSpeed').value) || 10;
    try {
      sim.busy = true;
      setStatus('演示运行中…', 'busy');
      if (currentTask?.demo) await sim.runDemo(currentTask.demo);
      else await sim.runDemo('oneLap');
      setStatus('演示完成', 'ok');
    } catch (e) {
      setStatus('失败: ' + e.message, 'err');
    } finally {
      sim.busy = false;
    }
  }

  function init() {
    sim.init();
    initPropUI();
    blocklyApp.init();
    fillSelectors();
    document.getElementById('btnRun').onclick = runProgram;
    document.getElementById('btnStart').onclick = startDemo;
    document.getElementById('btnReset').onclick = () => { sim.reset(); setStatus('已重置'); };
    document.getElementById('btnLoadStarter').onclick = () => {
      if (currentTask) blocklyApp.loadStarter(currentTask);
      setStatus('已加载示例程序');
    };
    document.getElementById('btnShowCode').onclick = () => {
      document.getElementById('codeOut').textContent = blocklyApp.generate() || '（无）';
      document.getElementById('codeOut').classList.add('show');
    };
    document.getElementById('btnClear').onclick = () => {
      if (confirm('清空所有积木？')) blocklyApp.workspace.clear();
    };
    document.getElementById('btnGrid').onclick = () => { sim.showGrid = !sim.showGrid; sim.draw(); };
    document.getElementById('btnLoadProps').onclick = () => {
      loadTaskProps();
      setStatus('已加载任务推荐道具');
    };
    document.getElementById('btnClearProps').onclick = () => {
      SceneProps.reset([]);
      sim.draw();
      setStatus('已清空场景道具');
    };
    setStatus('就绪 — 共 ' + countTasks() + ' 个教学任务');
  }

  function countTasks() {
    let n = 0;
    Object.values(CURRICULUM).forEach(s => Object.values(s.grades).forEach(g => { n += g.tasks.length; }));
    return n;
  }

  window.addEventListener('load', init);
})();
