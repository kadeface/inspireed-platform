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
