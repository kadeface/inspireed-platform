/* travel mode validation helpers */
'use strict';

(function () {
  function distance(a, b) {
    return Math.hypot(a.x - b.x, a.y - b.y);
  }

  const TravelValidation = {
    analyze(sim, task) {
      const a = sim.getRobot('A');
      const b = sim.getRobot('B');
      if (!a || !b) return { message: '未找到双车数据', matchPercent: 0, arcLengthCm: 0, parametric: '—' };

      const subtype = task?.travelSubtype || 'meet';
      const cfg = task?.sceneConfig || {};
      const travel = sim.travelSamples || [];
      const pxPerCm = sim.getPxPerCm ? sim.getPxPerCm() : 5;
      const tolCm = cfg.meetValidate?.toleranceCm || cfg.chaseValidate?.toleranceCm || 5;
      const tolPx = tolCm * pxPerCm;

      let best = Infinity;
      let bestSample = null;
      travel.forEach(s => {
        const d = Math.abs((s.sA || 0) - (s.sB || 0));
        if (d < best) {
          best = d;
          bestSample = s;
        }
      });
      const finalD = distance(a.state, b.state);
      const met = finalD <= tolPx || best <= tolCm;
      const arcLengthCm = (typeof TrailAnalysis !== 'undefined' && a.trail)
        ? TrailAnalysis.arcLengthCm(a.trail)
        : 0;
      const parametric = typeof TrailAnalysis !== 'undefined' && typeof TrailAnalysis.parametricSummary === 'function'
        ? TrailAnalysis.parametricSummary(sim, 8)
        : '—';

      if (subtype === 'apart') {
        return {
          mode: 'travel',
          subtype,
          hasTarget: true,
          matchPercent: 100,
          message: '背向而行完成，可根据 d(t) 观察距离变化',
          finalDistanceCm: finalD / pxPerCm,
          arcLengthCm,
          parametric
        };
      }

      if (!met) {
        return {
          mode: 'travel',
          subtype,
          hasTarget: true,
          matchPercent: Math.max(0, Math.round(100 - (best / Math.max(tolCm, 1)) * 20)),
          message: '尚未达到交会阈值',
          nearestDeltaCm: best,
          nearestTimeSec: bestSample?.t ?? null,
          arcLengthCm,
          parametric
        };
      }

      return {
        mode: 'travel',
        subtype,
        hasTarget: true,
        matchPercent: 100,
        message: subtype === 'chase' ? '追及成功' : subtype === 'dock' ? '交会对接判定成功' : '相遇成功',
        meetTimeSec: bestSample?.t ?? null,
        meetPositionCm: bestSample ? { a: bestSample.sA, b: bestSample.sB } : null,
        finalDistanceCm: finalD / pxPerCm,
        arcLengthCm,
        parametric
      };
    }
  };

  window.TravelValidation = TravelValidation;
})();
