/*
 * MotionScheduler — 单次动作列表的并行调度（如「同时 A/B 前进 N cm」）。
 *
 * 与上层并行的分工：
 * - MotionScheduler.run(jobs) / __parallel(jobs)：一组离散 motion job 同时执行。
 * - sim.runRobotsParallel(fnA, fnB)：两段完整 async 程序并行。
 *
 * 底层动画均由 MotionClock 统一 tick：所有 ActiveMotion 在同一 rAF 循环推进，每帧一次 draw。
 */
'use strict';

(function () {
  const MotionScheduler = {
    async run(sim, jobs) {
      const list = Array.isArray(jobs) ? jobs.filter(Boolean) : [];
      if (!list.length) return;
      const tasks = list.map(job => this.runJob(sim, job));
      await Promise.all(tasks);
    },

    async runJob(sim, job) {
      const robotId = job.robot || 'A';
      const action = job.action || 'forward';
      if (action === 'forward') return sim.forward(job.cm || 0, robotId);
      if (action === 'backward') return sim.forward(-(job.cm || 0), robotId);
      if (action === 'turn') return sim.turn(job.deg || 0, robotId);
      if (action === 'move2d') return sim.movePolar(job.angle || 0, job.cm || 0, robotId);
      if (action === 'goto') return sim.gotoCm(job.x || 0, job.y || 0, robotId);
      if (action === 'face') return sim.faceAngle(job.angle || 0, robotId);
      if (action === 'wait') return sim.wait((job.sec || 0) * 1000, robotId);
      return Promise.resolve();
    }
  };

  window.MotionScheduler = MotionScheduler;
})();
