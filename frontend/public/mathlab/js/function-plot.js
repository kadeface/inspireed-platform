export function evalExpr(expr, vars = {}) {
  const names = Object.keys(vars);
  const fn = new Function(...names, `return (${expr});`);
  return fn(...names.map(k => vars[k]));
}

export function samplePlot(expr, { xMin, xMax, step }) {
  const pts = [];
  for (let x = xMin; x <= xMax + 1e-9; x += step) {
    pts.push({ x, y: evalExpr(expr, { x }) });
  }
  return pts;
}

export function validateTrailAgainstExpr(trail, expr, { originX, originY, pxPerCm, toleranceCm }) {
  if (!trail?.length) return { ok: false, reason: 'empty trail' };
  let maxErr = 0;
  for (const p of trail) {
    const xCm = (p.x - originX) / pxPerCm;
    const yCm = (originY - p.y) / pxPerCm;
    const expected = evalExpr(expr, { x: xCm });
    maxErr = Math.max(maxErr, Math.abs(yCm - expected));
  }
  return { ok: maxErr <= toleranceCm, maxErr };
}
