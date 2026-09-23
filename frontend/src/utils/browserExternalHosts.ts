/** 常见需在外部标签完成登录 / 下载的域名片段 */
const EXTERNAL_PREFERRED_HOST_FRAGMENTS = [
  'accounts.google.',
  'login.microsoftonline.',
  'login.live.',
  'weixin.qq.com',
  'open.weixin.qq.com',
  'pan.baidu.com',
  'yun.baidu.com',
  'aliyundrive.com',
  'alipan.com',
  'jianguoyun.com',
  'cowtransfer.com',
  'lanzou',
  'github.com/login',
  'oauth',
  'sso.',
  'cas.',
  'auth.',
  'login.',
  'signin.',
]

export function isExternalPreferredUrl(url: string): boolean {
  try {
    const host = new URL(url).hostname.toLowerCase()
    const full = new URL(url).href.toLowerCase()
    return EXTERNAL_PREFERRED_HOST_FRAGMENTS.some(
      (frag) => host.includes(frag) || full.includes(frag)
    )
  } catch {
    return false
  }
}

/**
 * Bilibili 外链播放器在未写 autoplay 时会直接开播。
 * 内嵌预览补上 autoplay=0，等用户点播放器里的播放按钮。
 * 已显式带 autoplay 的地址保持原样。
 */
export function embedIframeSrc(url: string): string {
  let parsed: URL
  try {
    parsed = new URL(url)
  } catch {
    return url
  }
  if (parsed.hostname.toLowerCase() !== 'player.bilibili.com') return url
  if (!parsed.searchParams.has('autoplay')) {
    parsed.searchParams.set('autoplay', '0')
  }
  return parsed.toString()
}

export type BrowserOpenMode = 'auto' | 'external' | 'embed'

/** auto：默认外部打开；仅当教师显式 embed 时才内嵌 */
export function resolveBrowserOpenMode(
  configMode: BrowserOpenMode | undefined,
  url: string | null
): BrowserOpenMode {
  if (configMode === 'embed' || configMode === 'external') return configMode
  if (url && isExternalPreferredUrl(url)) return 'external'
  return 'external'
}
