/* 曲线巡逻拦截 / 伴随行走判定 */
'use strict';

(function () {
  function distance(a, b) {
    return Math.hypot(a.x - b.x, a.y - b.y);
  }

  function robotCm(sim, robot) {
    const ox = robot.state.startX;
    const oy = robot.state.startY;
    const px = sim.getPxPerCm ? sim.getPxPerCm() : 5;
    return {
      x: (robot.state.x - ox) / px,
      y: (oy - robot.state.y) / px
    };
  }

  const CurveTravelValidation = {
    analyze(sim, task) {
      const a = sim.getRobot('A');
      const b = sim.getRobot('B');
      if (!a || !b) {
        return { message: '未找到双车数据', matchPercent: 0, arcLengthCm: 0, parametric: '—' };
      }

      const subtype = task?.travelSubtype || 'meet';
      const cfg = task?.sceneConfig || {};
      const tolCm = cfg.curveMeetValidate?.toleranceCm
        || cfg.companionValidate?.toleranceCm
        || 4;
      const px = sim.getPxPerCm ? sim.getPxPerCm() : 5;
      const tolPx = tolCm * px;

      const samples = [];
      const maxLen = Math.max(a.trail?.length || 0, b.trail?.length || 0);
      for (let i = 0; i < maxLen; i++) {
        const pa = a.trail[Math.min(i, a.trail.length - 1)];
        const pb = b.trail[Math.min(i, b.trail.length - 1)];
        if (pa && pb) samples.push({ t: i, d: distance(pa, pb) / px });
      }

      let best = Infinity;
      let bestIdx = 0;
      samples.forEach((s, i) => {
        if (s.d < best) {
          best = s.d;
          bestIdx = i;
        }
      });
      const finalD = distance(a.state, b.state) / px;
      const met = finalD <= tolCm || best <= tolCm;

      const arcLengthCm = (typeof TrailAnalysis !== 'undefined' && a.trail)
        ? TrailAnalysis.arcLengthCm(a.trail)
        : 0;
      const parametric = typeof TrailAnalysis !== 'undefined' && typeof TrailAnalysis.parametricSummary === 'function'
        ? TrailAnalysis.parametricSummary(sim, 8)
        : '—';

      if (subtype === 'companion') {
        const minOverlap = cfg.companionValidate?.minOverlapSec ?? 2;
        const overlapTol = cfg.companionValidate?.toleranceCm ?? tolCm;
        let streak = 0;
        let maxStreak = 0;
        const stepSec = Math.max(a.state.elapsed, b.state.elapsed) / Math.max(samples.length, 1);
        samples.forEach(s => {
          if (s.d <= overlapTol) {
            streak += stepSec;
            maxStreak = Math.max(maxStreak, streak);
          } else {
            streak = 0;
          }
        });
        const ok = met && maxStreak >= minOverlap * 0.85;
        return {
          mode: 'curveTravel',
          subtype,
          hasTarget: true,
          matchPercent: ok ? 100 : Math.max(0, Math.round((maxStreak / minOverlap) * 70)),
          message: ok ? '伴随行走成功' : `伴随不足（需约 ${minOverlap}s 间距 ≤ ${overlapTol} cm）`,
          nearestDeltaCm: best,
          overlapSec: maxStreak,
          finalDistanceCm: finalD,
          arcLengthCm,
          parametric
        };
      }

      if (!met) {
        return {
          mode: 'curveTravel',
          subtype,
          hasTarget: true,
          matchPercent: Math.max(0, Math.round(100 - (best / Math.max(tolCm, 1)) * 25)),
          message: '尚未在曲线上相遇',
          nearestDeltaCm: best,
          finalDistanceCm: finalD,
          arcLengthCm,
          parametric
        };
      }

      return {
        mode: 'curveTravel',
        subtype,
        hasTarget: true,
        matchPercent: 100,
        message: '曲线拦截相遇成功',
        nearestDeltaCm: best,
        meetIndex: bestIdx,
        finalDistanceCm: finalD,
        arcLengthCm,
        parametric
      };
    }
  };

  window.CurveTravelValidation = CurveTravelValidation;
})();
