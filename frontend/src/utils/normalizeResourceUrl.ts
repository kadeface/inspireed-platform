/**
 * 规范化资源URL
 * 将包含localhost或IP地址的完整URL转换为当前服务器的URL
 */
import { getServerBaseUrl } from './url'

export function normalizeResourceUrl(url: string | null | undefined): string {
  if (!url) return ''
  
  const baseURL = getServerBaseUrl()
  
  // 如果已经是相对路径，转换为完整URL
  if (url.startsWith('/uploads/')) {
    return `${baseURL}${url}`
  }
  
  // 如果是完整URL，检查是否需要替换主机名
  if (url.startsWith('http://') || url.startsWith('https://')) {
    try {
      const urlObj = new URL(url)
      
      // 检查是否是资源URL
      if (urlObj.pathname.startsWith('/uploads/')) {
        // 检查主机名是否需要替换
        const urlHost = urlObj.hostname
        const currentHost = window.location.hostname
        const isLocalhost = urlHost === 'localhost' || urlHost === '127.0.0.1'
        const isIPAddress = /^(\d{1,3}\.){3}\d{1,3}$/.test(urlHost)
        const isDifferentHost = urlHost !== currentHost
        
        // 对于资源路径，如果包含IP地址、localhost，或者与当前主机不同，都替换为当前服务器地址
        // 这样可以确保在不同环境间迁移时URL能正确工作
        if (isLocalhost || isIPAddress || isDifferentHost) {
          return `${baseURL}${urlObj.pathname}${urlObj.search}${urlObj.hash}`
        }
      }
      
      // 如果不需要替换，返回原URL
      return url
    } catch (e) {
      console.warn('URL解析失败:', url, e)
      return url
    }
  }
  
  // 其他情况，返回原URL
  return url
}

/**
 * 批量规范化对象中的资源URL
 */
export function normalizeResourceUrls<T extends Record<string, any>>(
  obj: T,
  urlFields: string[] = ['cover_image_url', 'preview_url', 'download_url', 'videoUrl', 'video_url', 'file_url', 'thumbnail_url']
): T {
  const result = { ...obj }
  
  for (const field of urlFields) {
    if (field in result && typeof result[field] === 'string') {
      result[field] = normalizeResourceUrl(result[field])
    }
  }
  
  return result
}

