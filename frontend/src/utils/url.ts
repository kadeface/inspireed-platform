/**
 * 获取服务器基础URL（不包含/api/v1）
 * 根据当前访问的主机名自动适配后端地址
 * 这样学生端和教师端都能正确访问服务器资源
 */
export function getServerBaseUrl(): string {
  // 如果环境变量中配置了API地址，优先使用
  if (import.meta.env.VITE_API_BASE_URL) {
    const apiUrl = import.meta.env.VITE_API_BASE_URL
    // 移除 /api/v1 后缀（如果存在）
    if (apiUrl.endsWith('/api/v1')) {
      return apiUrl.replace('/api/v1', '')
    }
    // 如果已经是不带/api/v1的URL，直接返回
    return apiUrl
  }
  
  // 动态获取当前主机名
  const hostname = window.location.hostname
  const protocol = window.location.protocol
  
  // Cloud Studio 环境：如果 hostname 包含 cloudstudio.club 或 coding.net
  // 后端端口通常是 8000，但需要通过 Cloud Studio 分配的 URL 访问
  if (hostname.includes('cloudstudio.club') || hostname.includes('coding.net')) {
    // Cloud Studio 环境中，URL 格式为：{id}--{port}.{region}.cloudstudio.club
    // 前端 URL 示例：645cf02ac04c45c38ed3f5cceb49231b--5173.ap-shanghai2.cloudstudio.club
    // 后端 URL 应该：645cf02ac04c45c38ed3f5cceb49231b--8000.ap-shanghai2.cloudstudio.club
    // 需要将端口号从 5173 替换为 8000
    // 重要：CloudStudio 使用 HTTPS，必须使用 https:// 协议
    if (hostname.includes('--')) {
      // 将 --5173 替换为 --8000
      const backendHostname = hostname.replace(/--\d+/, '--8000')
      // 强制使用 HTTPS（CloudStudio 环境必须使用 HTTPS）
      return `https://${backendHostname}`
    }
  }
  
  // 本地开发环境：前端端口5173 -> 后端端口8000
  return `${protocol}//${hostname}:8000`
}

