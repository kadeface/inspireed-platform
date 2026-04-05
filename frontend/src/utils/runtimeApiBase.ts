/**
 * 生产构建且页面经 Nginx 仅开放 80/443：API 与当前页同源（/api/v1），由 Nginx 反代到 backend。
 */
export function productionSameOriginApiV1(): string {
  return `${window.location.origin}/api/v1`
}

/** 构建时若误配直连 :8000，生产环境外网通常不可达，改为同源 */
export function sanitizeViteApiUrlForProduction(url: string): string | null {
  if (import.meta.env.DEV) return null
  if (/(^|\/\/)[^/?#]*:8000(?:\/|$|\?|#)/.test(url)) {
    return productionSameOriginApiV1()
  }
  return null
}
