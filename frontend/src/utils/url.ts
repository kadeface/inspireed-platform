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
  
  // 根据主机名构建服务器地址
  // 前端端口5173 -> 后端端口8000
  return `${protocol}//${hostname}:8000`
}

