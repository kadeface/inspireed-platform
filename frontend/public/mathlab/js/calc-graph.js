export function interpolateV(samples, t) {
  if (!samples?.length) return 0;
  if (t <= samples[0].t) return samples[0].v ?? 0;
  const last = samples[samples.length - 1];
  if (t >= last.t) return last.v ?? 0;
  for (let i = 1; i < samples.length; i++) {
    const p1 = samples[i];
    if (t <= p1.t) {
      const p0 = samples[i - 1];
      const dt = p1.t - p0.t;
      if (Math.abs(dt) < 1e-9) return p0.v ?? 0;
      const u = (t - p0.t) / dt;
      return (p0.v ?? 0) + u * ((p1.v ?? 0) - (p0.v ?? 0));
    }
  }
  return last.v ?? 0;
}

export function interpolateS(samples, t) {
  if (!samples?.length) return 0;
  if (t <= samples[0].t) return samples[0].s ?? 0;
  const last = samples[samples.length - 1];
  if (t >= last.t) return last.s ?? 0;
  for (let i = 1; i < samples.length; i++) {
    const p1 = samples[i];
    if (t <= p1.t) {
      const p0 = samples[i - 1];
      const dt = p1.t - p0.t;
      if (Math.abs(dt) < 1e-9) return p0.s ?? 0;
      const u = (t - p0.t) / dt;
      return (p0.s ?? 0) + u * ((p1.s ?? 0) - (p0.s ?? 0));
    }
  }
  return last.s ?? 0;
}

export function slopeBetween(p0, p1) {
  const dt = p1.t - p0.t;
  if (Math.abs(dt) < 1e-9) return null;
  return (p1.s - p0.s) / dt;
}

export function riemannSum(samples, { t0, t1, n }) {
  const dt = (t1 - t0) / n;
  let sum = 0;
  for (let i = 0; i < n; i++) {
    const t = t0 + i * dt;
    const v = interpolateV(samples, t);
    sum += v * dt;
  }
  return sum;
}
