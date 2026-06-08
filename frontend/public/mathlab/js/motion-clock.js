/*
 * MotionClock — 统一运动时钟：单 rAF 循环推进所有 ActiveMotion，每帧一次 draw。
 * 供多车并行（runRobotsParallel）、MotionScheduler 与单车动画共用。
 */
'use strict';

(function () {
  function createTranslate(robot, dx, dy, cm, endAngle, sim) {
    const s = robot.state;
    const stats = robot.stats;
    const dur = Math.max(200, (Math.abs(cm) / (s.speed || 10)) * 1000);
    stats.totalDist += Math.abs(cm);
    sim.syncPrimaryStats?.(robot);
    return {
      type: 'translate',
      robot,
      x0: s.x,
      y0: s.y,
      dx,
      dy,
      cm,
      dur,
      endAngle,
      elapsed: 0,
      lastP: 0,
      step(dt, simRef) {
        this.elapsed += dt;
        const p = Math.min(1, this.elapsed / this.dur);
        const prevP = this.lastP;
        s.x = this.x0 + this.dx * p;
        s.y = this.y0 + this.dy * p;
        s.dist += Math.abs(this.cm) * (p - prevP);
        this.lastP = p;
        const px = simRef.getPxPerCm();
        s.wheelAngle += Math.abs(this.cm) * px * 0.06 * Math.sign(this.cm || 1) * (p - prevP);
        s.elapsed += this.dur * (p - prevP) / 1000;
        if (p > 0.01 && p - prevP > 0.0001) simRef.pushTrailPoint(robot, s.x, s.y);
        simRef.sampleMotion(robot);
        simRef.syncPrimaryStats?.(robot);
        if (p >= 1) {
          if (this.endAngle != null) s.angle = this.endAngle;
          s.dist = stats.totalDist;
          stats.totalTime += this.dur / 1000;
          simRef.syncPrimaryStats?.(robot);
          simRef.sampleMotion(robot);
          return true;
        }
        return false;
      }
    };
  }

  function createRotate(robot, deg, sim) {
    const s = robot.state;
    const stats = robot.stats;
    const target = s.angle + deg * Math.PI / 180;
    const a0 = s.angle;
    const dur = Math.min(1200, Math.abs(deg) * 8) || 1;
    stats.turns.push(deg);
    sim.syncPrimaryStats?.(robot);
    return {
      type: 'rotate',
      robot,
      a0,
      target,
      dur,
      elapsed: 0,
      step(dt, simRef) {
        this.elapsed += dt;
        const p = Math.min(1, this.elapsed / this.dur);
        s.angle = this.a0 + (this.target - this.a0) * p;
        if (p >= 1) {
          s.elapsed += this.dur / 1000;
          stats.totalTime += this.dur / 1000;
          simRef.syncPrimaryStats?.(robot);
          return true;
        }
        return false;
      }
    };
  }

  function createWait(robot, ms) {
    return {
      type: 'wait',
      robot,
      ms: Math.max(0, ms || 0),
      elapsed: 0,
      step(dt, simRef) {
        this.elapsed += dt;
        if (this.robot) {
          this.robot.state.elapsed += dt / 1000;
          if (this.robot.stats) this.robot.stats.totalTime = this.robot.state.elapsed;
          simRef.syncPrimaryStats?.(this.robot);
        }
        return this.elapsed >= this.ms;
      }
    };
  }

  function createWaitUntilNear(robot, otherRobot, epsilonCm, sim) {
    const eps = Math.max(0.1, Number(epsilonCm) || 5);
    return {
      type: 'waitUntilNear',
      robot,
      otherRobot,
      epsilonCm: eps,
      elapsed: 0,
      maxMs: 120000,
      step(dt, simRef) {
        this.elapsed += dt;
        if (this.robot) {
          this.robot.state.elapsed += dt / 1000;
          if (this.robot.stats) this.robot.stats.totalTime = this.robot.state.elapsed;
          simRef.syncPrimaryStats?.(this.robot);
        }
        const dist = simRef.robotDistanceCm(this.robot, this.otherRobot);
        if (dist <= this.epsilonCm) return true;
        if (this.elapsed >= this.maxMs) return true;
        return false;
      }
    };
  }

  const MotionClock = {
    sim: null,
    queue: [],
    running: false,
    rafId: 0,
    lastTs: 0,

    attach(sim) {
      this.sim = sim;
    },

    activeCount() {
      return this.queue.length;
    },

    cancelAll(err) {
      const e = err || Object.assign(new Error('程序已停止'), { code: 'PROGRAM_STOPPED' });
      for (const m of this.queue) {
        try { m._reject?.(e); } catch (_) { /* ignore */ }
      }
      this.queue = [];
      this.running = false;
      if (this.rafId) cancelAnimationFrame(this.rafId);
      this.rafId = 0;
    },

    enqueue(motion) {
      if (!this.sim) return Promise.resolve();
      return new Promise((resolve, reject) => {
        motion._resolve = resolve;
        motion._reject = reject;
        this.queue.push(motion);
        this._kick();
      });
    },

    _kick() {
      if (this.running) return;
      this.running = true;
      this.lastTs = performance.now();
      this._tick();
    },

    _tick() {
      const sim = this.sim;
      if (!sim || !this.queue.length) {
        this.running = false;
        this.rafId = 0;
        return;
      }
      try {
        sim.checkAborted();
      } catch (e) {
        this.cancelAll(e);
        return;
      }

      const now = performance.now();
      const dt = Math.min(48, Math.max(0, now - this.lastTs));
      this.lastTs = now;

      const pending = [];
      for (const m of this.queue) {
        if (m.step(dt, sim)) m._resolve?.();
        else pending.push(m);
      }
      this.queue = pending;

      sim.sampleTravel();
      sim.draw();
      sim.updateTelemetry();
      if (typeof ViewShell !== 'undefined') {
        const panel = document.getElementById('trailPanel');
        if (panel && !panel.hidden) ViewShell.refreshTrailPanel();
      }

      if (this.queue.length) {
        this.rafId = requestAnimationFrame(() => this._tick());
      } else {
        this.running = false;
        this.rafId = 0;
        sim.draw();
        sim.updateTelemetry();
      }
    },

    runTranslate(sim, robot, opts) {
      return this.enqueue(createTranslate(robot, opts.dx, opts.dy, opts.cm, opts.endAngle, sim));
    },

    runRotate(sim, robot, deg) {
      return this.enqueue(createRotate(robot, deg, sim));
    },

    runWait(sim, ms, robotOrId) {
      const robot = robotOrId ? sim.resolveRobot(robotOrId) : null;
      return this.enqueue(createWait(robot, ms));
    },

    runWaitUntilNear(sim, robot, otherRobot, epsilonCm) {
      if (!robot || !otherRobot || robot.id === otherRobot.id) return Promise.resolve();
      return this.enqueue(createWaitUntilNear(robot, otherRobot, epsilonCm, sim));
    },

    /** @internal test hooks */
    _createTranslate: createTranslate,
    _createRotate: createRotate,
    _createWait: createWait,
    _createWaitUntilNear: createWaitUntilNear
  };

  window.MotionClock = MotionClock;
})();
