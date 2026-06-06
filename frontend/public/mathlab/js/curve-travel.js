/* 曲线巡逻、原点拦截相遇与伴随行走 — 路径规划 */
'use strict';

(function () {
  function evalExpr(expr, x) {
    if (window.FunctionPlot?.evalExpr) return window.FunctionPlot.evalExpr(expr, { x });
    return new Function('x', `return (${expr});`)(x);
  }

  function cellCm(cfg) {
    return cfg?.cellCm ?? 10;
  }

  function buildPolylineCm(plot, cfg) {
    const cm = cellCm(cfg);
    const step = plot.pathStep ?? 0.5;
    const pts = [];
    const xMin = plot.xMin ?? 0;
    const xMax = plot.xMax ?? 3;
    for (let x = xMin; x <= xMax + 1e-9; x += step) {
      const y = evalExpr(plot.expr, x);
      pts.push({ x: x * cm, y: y * cm });
    }
    return pts;
  }

  function segmentLengths(pts) {
    const seg = [];
    let total = 0;
    for (let i = 1; i < pts.length; i++) {
      const len = Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y);
      seg.push(len);
      total += len;
    }
    return { seg, total };
  }

  function pointAtArc(pts, s) {
    if (!pts.length) return { x: 0, y: 0, angleDeg: 0, s: 0 };
    if (pts.length === 1 || s <= 0) {
      const n = pts.length > 1 ? pts[1] : pts[0];
      const ang = Math.atan2(n.y - pts[0].y, n.x - pts[0].x) * 180 / Math.PI;
      return { x: pts[0].x, y: pts[0].y, angleDeg: ang, s: 0 };
    }
    const { seg, total } = segmentLengths(pts);
    let left = Math.min(s, total);
    for (let i = 0; i < seg.length; i++) {
      if (left <= seg[i] + 1e-9) {
        const t = seg[i] > 0 ? left / seg[i] : 0;
        const a = pts[i];
        const b = pts[i + 1];
        const x = a.x + (b.x - a.x) * t;
        const y = a.y + (b.y - a.y) * t;
        const angleDeg = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI;
        let arc = 0;
        for (let j = 0; j < i; j++) arc += seg[j];
        arc += left;
        return { x, y, angleDeg, s: arc };
      }
      left -= seg[i];
    }
    const last = pts[pts.length - 1];
    const prev = pts[pts.length - 2];
    return {
      x: last.x,
      y: last.y,
      angleDeg: Math.atan2(last.y - prev.y, last.x - prev.x) * 180 / Math.PI,
      s: total
    };
  }

  function projectOntoPolyline(pts, x, y) {
    if (!pts.length) return { s: 0, dist: Infinity };
    let best = { s: 0, dist: Infinity };
    let arc = 0;
    for (let i = 0; i < pts.length - 1; i++) {
      const a = pts[i];
      const b = pts[i + 1];
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const len2 = dx * dx + dy * dy;
      const t = len2 > 0
        ? Math.max(0, Math.min(1, ((x - a.x) * dx + (y - a.y) * dy) / len2))
        : 0;
      const px = a.x + dx * t;
      const py = a.y + dy * t;
      const d = Math.hypot(x - px, y - py);
      const sHere = arc + Math.sqrt(len2) * t;
      if (d < best.dist) best = { s: sHere, dist: d };
      arc += Math.sqrt(len2);
    }
    return best;
  }

  function gotoJobsFromPolyline(robot, pts, cycles) {
    const jobs = [];
    const n = Math.max(1, cycles || 1);
    for (let c = 0; c < n; c++) {
      for (let i = 1; i < pts.length; i++) {
        jobs.push({ robot, action: 'goto', x: pts[i].x, y: pts[i].y });
      }
      if (c < n - 1) {
        jobs.push({ robot, action: 'goto', x: pts[0].x, y: pts[0].y });
      }
    }
    return jobs;
  }

  /** A 沿折线走到弧长 sTarget（交汇点） */
  function gotoJobsUntilArc(robot, pts, sTarget) {
    const meet = pointAtArc(pts, sTarget);
    const jobs = [];
    let arc = 0;
    for (let i = 1; i < pts.length; i++) {
      const segLen = Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y);
      if (arc + segLen >= sTarget - 1e-6) {
        jobs.push({ robot, action: 'goto', x: meet.x, y: meet.y });
        return jobs;
      }
      jobs.push({ robot, action: 'goto', x: pts[i].x, y: pts[i].y });
      arc += segLen;
    }
    jobs.push({ robot, action: 'goto', x: meet.x, y: meet.y });
    return jobs;
  }

  /** 交汇后 A 走完本圈剩余路程并循环（不含回到交汇点） */
  function gotoJobsLoopAfterMeet(robot, pts, sMeet, cycles, loop) {
    const jobs = [];
    if (!loop) return jobs;
    const extraLaps = Math.max(1, (cycles ?? 2) - 1);
    let arc = 0;
    for (let i = 1; i < pts.length; i++) {
      const segLen = Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y);
      const segEnd = arc + segLen;
      if (segEnd <= sMeet + 1e-6) {
        arc = segEnd;
        continue;
      }
      jobs.push({ robot, action: 'goto', x: pts[i].x, y: pts[i].y });
      arc = segEnd;
    }
    jobs.push({ robot, action: 'goto', x: pts[0].x, y: pts[0].y });
    for (let c = 0; c < extraLaps; c++) {
      for (let i = 1; i < pts.length; i++) {
        jobs.push({ robot, action: 'goto', x: pts[i].x, y: pts[i].y });
      }
      jobs.push({ robot, action: 'goto', x: pts[0].x, y: pts[0].y });
    }
    return jobs;
  }

  /** B 交汇后沿曲线伴随（假定已在交汇点，不再从原点重走整条） */
  function gotoJobsCompanionFollow(robot, pts, sFrom, cycles, loop) {
    return gotoJobsLoopAfterMeet(robot, pts, sFrom, cycles, loop);
  }

  function resolvePatrolCycles(cfg) {
    const p = cfg.patrol || {};
    if (p.loop === false) return 1;
    return Math.max(2, p.cycles ?? 2);
  }

  function findChaser(cfg) {
    const robots = cfg?.robots || [];
    return robots.find(r => r.role === 'chaser') || robots.find(r => r.id === 'B') || robots[1];
  }

  /** B 车起点（cm，相对坐标原点） */
  function chaserStartCm(cfg) {
    const chaser = findChaser(cfg);
    return { x: chaser?.xCm ?? 0, y: chaser?.yCm ?? 0 };
  }

  function planMeet(cfg) {
    const plot = cfg.plot || cfg.plots?.[0];
    if (!plot) return null;
    const pts = buildPolylineCm(plot, cfg);
    const { total } = segmentLengths(pts);
    if (total < 1) return null;

    const robots = cfg.robots || [];
    const patrol = robots.find(r => r.role === 'patrol') || robots.find(r => r.id === 'A') || robots[0];
    const chaser = findChaser(cfg);
    const b0 = chaserStartCm(cfg);
    const vA = patrol?.speed ?? 10;
    const vB = chaser?.speed ?? 12;
    const frac = cfg.patrol?.arcMeetFraction ?? 0.55;
    const sMeet = Math.min(total * frac, total - 0.01);
    const meet = pointAtArc(pts, sMeet);
    const tMeet = sMeet / vA;
    const dB = Math.hypot(meet.x - b0.x, meet.y - b0.y);
    const tB = dB / Math.max(vB, 0.1);
    const waitB = Math.max(0, tMeet - tB);
    const cycles = resolvePatrolCycles(cfg);
    const loop = cfg.patrol?.loop !== false;
    const patrolId = patrol?.id || 'A';
    const chaserId = chaser?.id || 'B';
    const patrolJobsToMeet = gotoJobsUntilArc(patrolId, pts, sMeet);
    const patrolJobsLoop = gotoJobsLoopAfterMeet(patrolId, pts, sMeet, cycles, loop);
    const chaserJobs = [
      ...(waitB > 0.05 ? [{ robot: chaserId, action: 'wait', sec: waitB }] : []),
      { robot: chaserId, action: 'goto', x: meet.x, y: meet.y }
    ];

    return {
      polyline: pts,
      meet,
      chaserStart: b0,
      sMeet,
      tMeet,
      waitB,
      patrolJobsToMeet,
      patrolJobsLoop,
      patrolJobs: patrolJobsToMeet.concat(patrolJobsLoop),
      chaserJobs
    };
  }

  function planCompanion(cfg) {
    const meetPlan = planMeet(cfg);
    if (!meetPlan) return null;
    const chaser = findChaser(cfg);
    const chaserId = chaser?.id || 'B';
    const lagSec = cfg.companion?.lagSec ?? 0.8;
    const cycles = resolvePatrolCycles(cfg);
    const loop = cfg.patrol?.loop !== false;
    const follow = gotoJobsCompanionFollow(chaserId, meetPlan.polyline, meetPlan.sMeet, cycles, loop);
    return {
      ...meetPlan,
      chaserJobs: [
        ...meetPlan.chaserJobs,
        { robot: chaserId, action: 'wait', sec: lagSec },
        ...follow
      ]
    };
  }

  function planForTask(cfg, subtype) {
    if (subtype === 'companion') return planCompanion(cfg);
    return planMeet(cfg);
  }

  function patrolArcCm(robot, cfg, pxPerCm) {
    const plot = cfg.plot || cfg.plots?.[0];
    if (!plot) return 0;
    const pts = buildPolylineCm(plot, cfg);
    const ox = robot.state.startX;
    const oy = robot.state.startY;
    const px = pxPerCm || robot._pxPerCm || 5;
    const xCm = (robot.state.x - ox) / px;
    const yCm = (oy - robot.state.y) / px;
    return projectOntoPolyline(pts, xCm, yCm).s;
  }

  function chaserDistCm(robot, pxPerCm) {
    const ox = robot.state.startX;
    const oy = robot.state.startY;
    const px = pxPerCm || robot._pxPerCm || 5;
    const xCm = (robot.state.x - ox) / px;
    const yCm = (oy - robot.state.y) / px;
    return Math.hypot(xCm, yCm);
  }

  const CurveTravel = {
    buildPolylineCm,
    pointAtArc,
    projectOntoPolyline,
    findChaser,
    chaserStartCm,
    gotoJobsUntilArc,
    gotoJobsLoopAfterMeet,
    planMeet,
    planCompanion,
    planForTask,
    patrolArcCm,
    chaserDistCm,
    allDemoJobs(cfg, subtype) {
      const plan = planForTask(cfg, subtype);
      if (!plan) return [];
      return [...(plan.patrolJobs || []), ...(plan.chaserJobs || [])];
    }
  };

  window.CurveTravel = CurveTravel;
  window.curveTravelPlanMeet = planMeet;
})();
