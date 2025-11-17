/**
 * 获取当前用户的 JWT Token
 */
export function getAuthToken(): string | null {
  // 从 localStorage 获取 Token
  const token = localStorage.getItem('auth_token')
  
  // 或者从 sessionStorage 获取
  if (!token) {
    return sessionStorage.getItem('auth_token')
  }
  
  return token
}

/**
 * 设置认证 Token
 */
export function setAuthToken(token: string) {
  localStorage.setItem('auth_token', token)
}

/**
 * 清除认证 Token
 */
export function clearAuthToken() {
  localStorage.removeItem('auth_token')
  sessionStorage.removeItem('auth_token')
}

