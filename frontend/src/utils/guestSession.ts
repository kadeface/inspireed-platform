/** 访客接入码：供外部浏览返回 /guest 时恢复会话 */

const GUEST_ACCESS_CODE_KEY = 'inspireed_guest_access_code'

export function saveGuestAccessCode(code: string) {
  const normalized = code?.trim().toUpperCase()
  if (!normalized || normalized.length < 6) return
  try {
    sessionStorage.setItem(GUEST_ACCESS_CODE_KEY, normalized)
  } catch {
    /* private mode / quota */
  }
}

export function readGuestAccessCode(): string | null {
  try {
    const raw = sessionStorage.getItem(GUEST_ACCESS_CODE_KEY)
    if (!raw?.trim()) return null
    return raw.trim().toUpperCase()
  } catch {
    return null
  }
}

export function clearGuestAccessCode() {
  try {
    sessionStorage.removeItem(GUEST_ACCESS_CODE_KEY)
  } catch {
    /* ignored */
  }
}

const LOOPBACK_HOSTS = new Set(['localhost', '127.0.0.1', '::1'])

/** 教师用回环地址打开时，改成手机能访问的局域网 IP；已是域名或局域网 IP 时不动。 */
export function guestJoinOrigin(pageOrigin: string, lanHost: string | null | undefined): string {
  const trimmed = pageOrigin.trim()
  let url: URL
  try {
    url = new URL(trimmed)
  } catch {
    return trimmed.replace(/\/+$/, '')
  }
  const host = lanHost?.trim()
  if (host && LOOPBACK_HOSTS.has(url.hostname)) {
    url.hostname = host
  }
  return url.origin
}

export function buildGuestJoinUrl(origin: string, code: string): string {
  const base = origin.trim().replace(/\/+$/, '')
  const normalized = code.trim().toUpperCase()
  if (!base || !normalized) {
    throw new Error('guest join url requires origin and code')
  }
  return `${base}/guest?code=${encodeURIComponent(normalized)}`
}
