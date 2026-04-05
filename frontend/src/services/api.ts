import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'
import { useUserStore } from '../store/user'
import { productionSameOriginApiV1, sanitizeViteApiUrlForProduction } from '@/utils/runtimeApiBase'

/** 本机或局域网私网 IP（用 5173 开发时也应走 Vite 代理，避免直连 localhost:8000 跨域） */
function isLocalOrPrivateLanHostname(hostname: string): boolean {
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '0.0.0.0') {
    return true
  }
  const m = hostname.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/)
  if (!m) return false
  const a = Number(m[1])
  const b = Number(m[2])
  if (a === 10) return true
  if (a === 192 && b === 168) return true
  if (a === 172 && b >= 16 && b <= 31) return true
  return false
}

/**
 * 动态获取API基础URL
 * 根据当前访问的主机名自动适配后端地址
 */
function getApiBaseUrl(): string {
  // 动态获取当前主机名（优先于环境变量，确保 CloudStudio 环境能正确检测）
  const hostname = window.location.hostname
  // 确保使用与当前页面相同的协议（HTTPS 或 HTTP）
  // 在 CloudStudio 中，前端通常是 HTTPS，后端也应该是 HTTPS
  const protocol = window.location.protocol
  const port = window.location.port

  // 方案 C：本地开发 / Docker 前端一律走代理，避免跨域导致 Authorization 未发送、教案接口 401
  // DEV+5173：Vite 代理；端口 80：Docker 前端 nginx 代理
  const isViteDevPort = port === '5173'
  const isDockerFrontendPort = port === '80' || port === ''
  if (
    isLocalOrPrivateLanHostname(hostname) &&
    (import.meta.env.DEV || isViteDevPort || isDockerFrontendPort)
  ) {
    console.log('📍 [API] 使用代理 /api/v1，避免跨域导致 token 未发送')
    return '/api/v1'
  }

  // 判断是否为生产环境（非 localhost、非 127.0.0.1、非 IP 地址）
  const isProduction = !['localhost', '127.0.0.1'].includes(hostname) && !/^\d+\.\d+\.\d+\.\d+$/.test(hostname)

  if (isProduction) {
    // 生产环境：部署环境，使用相对路径或当前域名
    // 后端通常在同一域名下，通过 Nginx 反向代理
    const apiUrl = `${protocol}//${hostname}/api/v1`
    if (import.meta.env.DEV) {
      console.log('✅ [API] 生产环境，使用当前域名:', apiUrl)
    }
    return apiUrl
  }

  if (import.meta.env.DEV) {
    console.log('🔍 [API] 检测环境 - hostname:', hostname, 'protocol:', protocol, 'port:', port, 'full URL:', window.location.href)
    console.log('🔍 [API] VITE_API_BASE_URL 环境变量:', import.meta.env.VITE_API_BASE_URL)
  }

  // 优先检测 Cloud Studio 环境：如果 hostname 包含 cloudstudio.club 或 coding.net
  // 后端端口通常是 8000，但需要通过 Cloud Studio 分配的 URL 访问
  // 这样可以避免环境变量中的 localhost 覆盖正确的 CloudStudio URL
  if (hostname.includes('cloudstudio.club') || hostname.includes('coding.net')) {
    // Cloud Studio 环境中，URL 格式为：{id}--{port}.{region}.cloudstudio.club
    // 前端 URL 示例：645cf02ac04c45c38ed3f5cceb49231b--5173.ap-shanghai2.cloudstudio.club
    // 后端 URL 应该：645cf02ac04c45c38ed3f5cceb49231b--8000.ap-shanghai2.cloudstudio.club
    // 需要将端口号从 5173 替换为 8000
    // 重要：CloudStudio 使用 HTTPS，必须使用 https:// 协议
    if (hostname.includes('--')) {
      // 将 --5173 或 --其他端口 替换为 --8000
      const backendHostname = hostname.replace(/--\d+/, '--8000')
      // 强制使用 HTTPS（CloudStudio 环境必须使用 HTTPS）
      const apiUrl = `https://${backendHostname}/api/v1`
      if (import.meta.env.DEV) {
        console.log('✅ [API] Cloud Studio 环境检测成功！')
        console.log('   前端地址:', `${protocol}//${hostname}`)
        console.log('   后端地址:', apiUrl)
      }
      return apiUrl
    } else {
      // 如果没有 -- 分隔符，尝试使用标准格式
      const backendHostname = hostname.replace(/5173/, '8000')
      // 强制使用 HTTPS
      const apiUrl = `https://${backendHostname}/api/v1`
      if (import.meta.env.DEV) {
        console.log('✅ [API] Cloud Studio 环境（备用检测），使用后端地址:', apiUrl)
      }
      return apiUrl
    }
  }

  // 如果环境变量中配置了API地址，检查并处理
  if (import.meta.env.VITE_API_BASE_URL) {
    let envApiUrl = import.meta.env.VITE_API_BASE_URL

    // 本机或局域网 IP + 5173 时，若环境变量指向 localhost:8000，强制走代理避免跨域导致 Authorization 未发送
    if (
      import.meta.env.DEV &&
      isLocalOrPrivateLanHostname(hostname) &&
      (isViteDevPort || isDockerFrontendPort)
    ) {
      if (envApiUrl.includes('localhost:8000') || envApiUrl.includes('127.0.0.1:8000')) {
        if (import.meta.env.DEV) {
          console.warn('⚠️ [API] 本地开发已强制使用代理 /api/v1，避免跨域导致 token 未发送')
        }
        return '/api/v1'
      }
    }

    // 在 CloudStudio 环境中，如果环境变量包含 localhost，完全忽略它
    // 重新计算 CloudStudio 的 URL 并返回
    if ((hostname.includes('cloudstudio.club') || hostname.includes('coding.net')) &&
        (envApiUrl.includes('localhost') || envApiUrl.includes('127.0.0.1'))) {
      if (import.meta.env.DEV) {
        console.warn('⚠️ [API] 环境变量包含 localhost，在 CloudStudio 环境中已忽略，使用自动检测的地址')
      }
      // 重新计算 CloudStudio 的 URL
      if (hostname.includes('--')) {
        const backendHostname = hostname.replace(/--\d+/, '--8000')
        const apiUrl = `https://${backendHostname}/api/v1`
        if (import.meta.env.DEV) {
          console.log('✅ [API] 使用 CloudStudio 自动检测的地址:', apiUrl)
        }
        return apiUrl
      } else {
        const backendHostname = hostname.replace(/5173/, '8000')
        const apiUrl = `https://${backendHostname}/api/v1`
        if (import.meta.env.DEV) {
          console.log('✅ [API] 使用 CloudStudio 自动检测的地址（备用）:', apiUrl)
        }
        return apiUrl
      }
    }

    // 如果是 HTTPS 页面，强制使用 HTTPS API（防止混合内容错误）
    if (protocol === 'https:' && envApiUrl.startsWith('http://')) {
      if (import.meta.env.DEV) {
        console.warn('⚠️ [API] 环境变量使用 HTTP，但在 HTTPS 页面中强制转换为 HTTPS')
      }
      envApiUrl = envApiUrl.replace('http://', 'https://')
    }
    if (import.meta.env.DEV) {
      console.log('🔧 [API] 使用环境变量配置的 API 地址:', envApiUrl)
    }
    const sanitized = sanitizeViteApiUrlForProduction(envApiUrl)
    if (sanitized) return sanitized
    return envApiUrl
  }

  // 本地开发环境：使用相对路径 /api/v1，由 Vite 代理到后端 8000，避免 404 和 CORS
  if (import.meta.env.DEV) {
    console.log('📍 [API] 本地开发，使用代理相对路径: /api/v1')
    return '/api/v1'
  }
  // 生产构建：Docker 仅开放 80 时与页面同源，由 Nginx 反代（勿直连 :8000）
  return productionSameOriginApiV1()
}
const API_BASE_URL = getApiBaseUrl()

// 在控制台输出最终的 API 地址，方便调试（仅在开发环境）
if (import.meta.env.DEV) {
  console.log('🚀 [API] 最终使用的 API 基础地址:', API_BASE_URL)
  if (API_BASE_URL.startsWith('http://') && window.location.protocol === 'https:') {
    console.error('❌ [API] 警告：检测到混合内容问题！')
    console.error('   当前页面使用 HTTPS，但 API 地址使用 HTTP')
    console.error('   这会导致浏览器阻止请求')
  }
}

class ApiService {
  private axiosInstance: AxiosInstance

  constructor() {
    // 再次检查并确保在 HTTPS 页面使用 HTTPS API
    let finalBaseURL = API_BASE_URL
    // 运行时兜底：若当前是 localhost:5173 或 :80 但 baseURL 是直连 8000，强制改为代理路径，避免跨域 401
    const hn = window.location.hostname
    const pt = window.location.port
    const useProxyPort = pt === '5173' || pt === '80' || pt === ''
    if (isLocalOrPrivateLanHostname(hn) && useProxyPort &&
        (finalBaseURL.startsWith('http://localhost:8000') || finalBaseURL.startsWith('http://127.0.0.1:8000'))) {
      console.warn('📍 [API] 运行时兜底：强制使用代理 /api/v1，避免跨域导致教案 401')
      finalBaseURL = '/api/v1'
    }
    if (window.location.protocol === 'https:' && finalBaseURL.startsWith('http://')) {
      if (import.meta.env.DEV) {
        console.warn('⚠️ [API] 检测到混合内容，自动将 HTTP 转换为 HTTPS')
      }
      finalBaseURL = finalBaseURL.replace('http://', 'https://')
      if (import.meta.env.DEV) {
        console.log('✅ [API] 修正后的 API 地址:', finalBaseURL)
      }
    }

    // 在 CloudStudio 环境中，强制使用 HTTPS
    if ((window.location.hostname.includes('cloudstudio.club') || window.location.hostname.includes('coding.net')) &&
        finalBaseURL.startsWith('http://')) {
      if (import.meta.env.DEV) {
        console.warn('⚠️ [API] CloudStudio 环境强制使用 HTTPS')
      }
      finalBaseURL = finalBaseURL.replace('http://', 'https://')
      if (import.meta.env.DEV) {
        console.log('✅ [API] CloudStudio 环境修正后的 API 地址:', finalBaseURL)
      }
    }

    if (import.meta.env.DEV) {
      console.log('🔧 [API] ApiService 构造函数 - 最终 baseURL:', finalBaseURL)
    }
    
    this.axiosInstance = axios.create({
      baseURL: finalBaseURL,
      timeout: 120000, // 增加到120秒，适应文档转换等长时间操作
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // 请求拦截器
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // 优先 localStorage，若无则从 store 取（避免登录后首请求时未同步导致 Not authenticated）
        let token = localStorage.getItem('access_token')
        if (!token) {
          try {
            token = useUserStore().token ?? null
          } catch {
            token = null
          }
        }
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // 如果是FormData，删除Content-Type让浏览器自动设置
        if (config.data instanceof FormData) {
          delete config.headers['Content-Type']
        }
        
        // 最后一道防线：在 HTTPS 页面中，确保 baseURL 使用 HTTPS
        if (window.location.protocol === 'https:' && config.baseURL?.startsWith('http://')) {
          if (import.meta.env.DEV) {
            console.error('❌ [API] 请求拦截器检测到 HTTP baseURL！', {
              baseURL: config.baseURL,
              url: config.url,
              fullURL: config.baseURL + (config.url || ''),
              hostname: window.location.hostname,
              protocol: window.location.protocol
            })
            console.warn('⚠️ [API] 请求拦截器自动转换为 HTTPS:', config.baseURL)
          }
          config.baseURL = config.baseURL.replace('http://', 'https://')
          if (import.meta.env.DEV) {
            console.log('✅ [API] 请求拦截器修正后的 baseURL:', config.baseURL)
          }
        }

        // 如果请求 URL 本身是完整的 HTTP URL，也转换为 HTTPS
        if (window.location.protocol === 'https:' && config.url?.startsWith('http://')) {
          if (import.meta.env.DEV) {
            console.error('❌ [API] 请求拦截器检测到 HTTP 完整 URL！', {
              url: config.url,
              baseURL: config.baseURL,
              hostname: window.location.hostname,
              protocol: window.location.protocol
            })
            console.warn('⚠️ [API] 请求拦截器自动转换为 HTTPS:', config.url)
          }
          config.url = config.url.replace('http://', 'https://')
          if (import.meta.env.DEV) {
            console.log('✅ [API] 请求拦截器修正后的 URL:', config.url)
          }
        }

        // 最终检查：确保完整 URL 使用 HTTPS
        const finalURL = (config.baseURL || '') + (config.url || '')
        if (window.location.protocol === 'https:' && finalURL.startsWith('http://')) {
          if (import.meta.env.DEV) {
            console.error('❌ [API] 最终检查：完整 URL 仍然是 HTTP！', {
              finalURL,
              baseURL: config.baseURL,
              url: config.url,
              hostname: window.location.hostname
            })
          }
          // 强制修正
          if (config.baseURL?.startsWith('http://')) {
            config.baseURL = config.baseURL.replace('http://', 'https://')
          }
          if (config.url?.startsWith('http://')) {
            config.url = config.url.replace('http://', 'https://')
          }
          if (import.meta.env.DEV) {
            console.log('✅ [API] 强制修正后的完整 URL:', (config.baseURL || '') + (config.url || ''))
          }
        }
        
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          const requestUrl = error.config?.url ?? ''
          const isAuthRequest = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/register')
          const isSessionCheck = requestUrl.includes('/auth/me')
          // 仅当「会话校验」接口 401 时清除并跳转登录，避免数据接口（如 /lessons）401 导致登录后闪退
          if (!isAuthRequest && isSessionCheck) {
            try {
              useUserStore().logout()
            } catch {
              localStorage.removeItem('access_token')
              localStorage.removeItem('user')
              sessionStorage.removeItem('access_token')
            }
            window.location.href = '/login'
          }
        } else if (error.response?.status === 403) {
          // 403 权限错误，但不自动重定向，让调用方处理
          const errorMessage = error.response?.data?.detail || '需要相应权限'
          console.warn('权限不足:', errorMessage)
          // 可以在这里添加全局错误提示
        }
        return Promise.reject(error)
      }
    )
  }

  /**
   * 与当前 axios baseURL 同源的课堂 WebSocket URL。
   * 访客页等场景若仍用页面 host 拼 WS，在 CloudStudio（前端 --5173 / 后端 --8000）等环境会连错端口，收不到 cell_changed。
   */
  buildClassroomWebSocketUrl(relPath: string): string {
    const base = (this.axiosInstance.defaults.baseURL || '/api/v1').replace(/\/$/, '')
    const rel = relPath.replace(/^\//, '')
    const pageIsSecure = typeof window !== 'undefined' && window.location.protocol === 'https:'
    const fallbackWsProto = pageIsSecure ? 'wss:' : 'ws:'

    if (base.startsWith('http://') || base.startsWith('https://')) {
      const u = new URL(base.endsWith('/') ? base : `${base}/`)
      const wss = u.protocol === 'https:' ? 'wss:' : 'ws:'
      const pathBase = u.pathname.replace(/\/$/, '')
      return `${wss}//${u.host}${pathBase}/${rel}`
    }

    const prefix = base.startsWith('/') ? base : `/${base}`
    return `${fallbackWsProto}//${window.location.host}${prefix}/${rel}`
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    // 确保不使用缓存，特别是对于教案数据
    const noCacheConfig = {
      ...config,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        ...config?.headers,
      },
    }
    const response = await this.axiosInstance.get<T>(url, noCacheConfig)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.post<T>(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.put<T>(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.delete<T>(url, config)
    return response.data
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.patch<T>(url, data, config)
    return response.data
  }

  async downloadFile(url: string, config?: AxiosRequestConfig): Promise<Blob> {
    const response = await this.axiosInstance.get(url, {
      ...config,
      responseType: 'blob'
    })
    return response.data as Blob
  }
}

const api = new ApiService()

export { api }
export default api
