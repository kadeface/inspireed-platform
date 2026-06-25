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

export function collectTrailVertices(trail) {
  if (!trail?.length) return [];
  const indices = new Set([0, trail.length - 1]);
  trail.forEach((p, i) => {
    if (p?.break) indices.add(i);
  });
  return [...indices].sort((a, b) => a - b).map(i => ({ point: trail[i], trailIndex: i }));
}

function pointErrorCm(p, expr, { originX, originY, pxPerCm }) {
  const xCm = (p.x - originX) / pxPerCm;
  const yCm = (originY - p.y) / pxPerCm;
  const expected = evalExpr(expr, { x: xCm });
  return Math.abs(yCm - expected);
}

export function validateTrailAgainstExpr(trail, expr, { originX, originY, pxPerCm, toleranceCm }) {
  if (!trail?.length) return { ok: false, reason: 'empty trail', maxErr: Infinity };
  let maxErr = 0;
  for (const p of trail) {
    if (p?.x == null || p?.y == null) continue;
    maxErr = Math.max(maxErr, pointErrorCm(p, expr, { originX, originY, pxPerCm }));
  }
  return { ok: maxErr <= toleranceCm, maxErr };
}

export function validateTrailVertices(trail, expr, { originX, originY, pxPerCm, toleranceCm }) {
  const vertices = collectTrailVertices(trail);
  if (!vertices.length) return { ok: false, reason: 'empty trail', maxErr: Infinity, vertexCount: 0 };
  let maxErr = 0;
  let worstVertex = 1;
  vertices.forEach((v, vi) => {
    const err = pointErrorCm(v.point, expr, { originX, originY, pxPerCm });
    if (err > maxErr) {
      maxErr = err;
      worstVertex = vi + 1;
    }
  });
  return {
    ok: maxErr <= toleranceCm,
    maxErr,
    vertexCount: vertices.length,
    worstVertex
  };
}

export function validatePlotTrail(trail, config, simOpts) {
  const opts = { ...simOpts, toleranceCm: config.toleranceCm ?? 1 };
  if (config.mode === 'vertices') {
    return validateTrailVertices(trail, config.expr, opts);
  }
  return validateTrailAgainstExpr(trail, config.expr, opts);
}
