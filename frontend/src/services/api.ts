import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'

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
  
  console.log('🔍 [API] 检测环境 - hostname:', hostname, 'protocol:', protocol, 'port:', port, 'full URL:', window.location.href)
  console.log('🔍 [API] VITE_API_BASE_URL 环境变量:', import.meta.env.VITE_API_BASE_URL)
  
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
      console.log('✅ [API] Cloud Studio 环境检测成功！')
      console.log('   前端地址:', `${protocol}//${hostname}`)
      console.log('   后端地址:', apiUrl)
      return apiUrl
    } else {
      // 如果没有 -- 分隔符，尝试使用标准格式
      const backendHostname = hostname.replace(/5173/, '8000')
      // 强制使用 HTTPS
      const apiUrl = `https://${backendHostname}/api/v1`
      console.log('✅ [API] Cloud Studio 环境（备用检测），使用后端地址:', apiUrl)
      return apiUrl
    }
  }
  
  // 如果环境变量中配置了API地址，检查并处理
  if (import.meta.env.VITE_API_BASE_URL) {
    let envApiUrl = import.meta.env.VITE_API_BASE_URL
    
    // 在 CloudStudio 环境中，如果环境变量包含 localhost，完全忽略它
    // 重新计算 CloudStudio 的 URL 并返回
    if ((hostname.includes('cloudstudio.club') || hostname.includes('coding.net')) && 
        (envApiUrl.includes('localhost') || envApiUrl.includes('127.0.0.1'))) {
      console.warn('⚠️ [API] 环境变量包含 localhost，在 CloudStudio 环境中已忽略，使用自动检测的地址')
      // 重新计算 CloudStudio 的 URL
      if (hostname.includes('--')) {
        const backendHostname = hostname.replace(/--\d+/, '--8000')
        const apiUrl = `https://${backendHostname}/api/v1`
        console.log('✅ [API] 使用 CloudStudio 自动检测的地址:', apiUrl)
        return apiUrl
      } else {
        const backendHostname = hostname.replace(/5173/, '8000')
        const apiUrl = `https://${backendHostname}/api/v1`
        console.log('✅ [API] 使用 CloudStudio 自动检测的地址（备用）:', apiUrl)
        return apiUrl
      }
    }
    
    // 🆕 在局域网环境下，如果环境变量包含 localhost，且当前 hostname 是 IP 地址，自动适配
    // 检测 hostname 是否为 IP 地址（IPv4）
    const isIpAddress = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(hostname)
    if (isIpAddress && (envApiUrl.includes('localhost') || envApiUrl.includes('127.0.0.1'))) {
      console.warn('⚠️ [API] 环境变量包含 localhost，但当前通过 IP 地址访问，自动适配为当前 IP')
      const apiProtocol = protocol === 'https:' ? 'https:' : 'http:'
      const apiUrl = `${apiProtocol}//${hostname}:8000/api/v1`
      console.log('✅ [API] 使用自动适配的地址:', apiUrl)
      return apiUrl
    }
    
    // 如果是 HTTPS 页面，强制使用 HTTPS API（防止混合内容错误）
    if (protocol === 'https:' && envApiUrl.startsWith('http://')) {
      console.warn('⚠️ [API] 环境变量使用 HTTP，但在 HTTPS 页面中强制转换为 HTTPS')
      envApiUrl = envApiUrl.replace('http://', 'https://')
    }
    console.log('🔧 [API] 使用环境变量配置的 API 地址:', envApiUrl)
    return envApiUrl
  }
  
  // 本地开发环境：前端端口5173 -> 后端端口8000
  // 注意：在 CloudStudio 中，如果 hostname 不包含 cloudstudio.club，也会走到这里
  // 但这种情况应该很少见
  // 如果页面是 HTTPS，也使用 HTTPS API
  const apiProtocol = protocol === 'https:' ? 'https:' : 'http:'
  const apiUrl = `${apiProtocol}//${hostname}:8000/api/v1`
  console.log('📍 [API] 本地环境，使用后端地址:', apiUrl)
  return apiUrl
}
const API_BASE_URL = getApiBaseUrl()

// 在控制台输出最终的 API 地址，方便调试
console.log('🚀 [API] 最终使用的 API 基础地址:', API_BASE_URL)
if (API_BASE_URL.startsWith('http://') && window.location.protocol === 'https:') {
  console.error('❌ [API] 警告：检测到混合内容问题！')
  console.error('   当前页面使用 HTTPS，但 API 地址使用 HTTP')
  console.error('   这会导致浏览器阻止请求')
}

class ApiService {
  private axiosInstance: AxiosInstance

  constructor() {
    // 再次检查并确保在 HTTPS 页面使用 HTTPS API
    let finalBaseURL = API_BASE_URL
    if (window.location.protocol === 'https:' && finalBaseURL.startsWith('http://')) {
      console.warn('⚠️ [API] 检测到混合内容，自动将 HTTP 转换为 HTTPS')
      finalBaseURL = finalBaseURL.replace('http://', 'https://')
      console.log('✅ [API] 修正后的 API 地址:', finalBaseURL)
    }
    
    // 在 CloudStudio 环境中，强制使用 HTTPS
    if ((window.location.hostname.includes('cloudstudio.club') || window.location.hostname.includes('coding.net')) && 
        finalBaseURL.startsWith('http://')) {
      console.warn('⚠️ [API] CloudStudio 环境强制使用 HTTPS')
      finalBaseURL = finalBaseURL.replace('http://', 'https://')
      console.log('✅ [API] CloudStudio 环境修正后的 API 地址:', finalBaseURL)
    }
    
    console.log('🔧 [API] ApiService 构造函数 - 最终 baseURL:', finalBaseURL)
    
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
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        
        // 如果是FormData，删除Content-Type让浏览器自动设置
        if (config.data instanceof FormData) {
          delete config.headers['Content-Type']
        }
        
        // 最后一道防线：在 HTTPS 页面中，确保 baseURL 使用 HTTPS
        if (window.location.protocol === 'https:' && config.baseURL?.startsWith('http://')) {
          console.error('❌ [API] 请求拦截器检测到 HTTP baseURL！', {
            baseURL: config.baseURL,
            url: config.url,
            fullURL: config.baseURL + (config.url || ''),
            hostname: window.location.hostname,
            protocol: window.location.protocol
          })
          console.warn('⚠️ [API] 请求拦截器自动转换为 HTTPS:', config.baseURL)
          config.baseURL = config.baseURL.replace('http://', 'https://')
          console.log('✅ [API] 请求拦截器修正后的 baseURL:', config.baseURL)
        }
        
        // 如果请求 URL 本身是完整的 HTTP URL，也转换为 HTTPS
        if (window.location.protocol === 'https:' && config.url?.startsWith('http://')) {
          console.error('❌ [API] 请求拦截器检测到 HTTP 完整 URL！', {
            url: config.url,
            baseURL: config.baseURL,
            hostname: window.location.hostname,
            protocol: window.location.protocol
          })
          console.warn('⚠️ [API] 请求拦截器自动转换为 HTTPS:', config.url)
          config.url = config.url.replace('http://', 'https://')
          console.log('✅ [API] 请求拦截器修正后的 URL:', config.url)
        }
        
        // 最终检查：确保完整 URL 使用 HTTPS
        const finalURL = (config.baseURL || '') + (config.url || '')
        if (window.location.protocol === 'https:' && finalURL.startsWith('http://')) {
          console.error('❌ [API] 最终检查：完整 URL 仍然是 HTTP！', {
            finalURL,
            baseURL: config.baseURL,
            url: config.url,
            hostname: window.location.hostname
          })
          // 强制修正
          if (config.baseURL?.startsWith('http://')) {
            config.baseURL = config.baseURL.replace('http://', 'https://')
          }
          if (config.url?.startsWith('http://')) {
            config.url = config.url.replace('http://', 'https://')
          }
          console.log('✅ [API] 强制修正后的完整 URL:', (config.baseURL || '') + (config.url || ''))
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

          if (!isAuthRequest) {
            localStorage.removeItem('access_token')
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
