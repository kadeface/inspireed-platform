/**
 * 获取当前用户的 JWT Token
 * 注意：与 User Store 保持一致，使用 'access_token' 作为 key
 */
export function getAuthToken(): string | null {
  // 从 localStorage 获取 Token（与 User Store 一致）
  const token = localStorage.getItem('access_token')
  
  // 或者从 sessionStorage 获取
  if (!token) {
    return sessionStorage.getItem('access_token')
  }
  
  return token
}

/**
 * 设置认证 Token
 * 注意：与 User Store 保持一致，使用 'access_token' 作为 key
 */
export function setAuthToken(token: string) {
  localStorage.setItem('access_token', token)
}

/**
 * 清除认证 Token
 * 注意：与 User Store 保持一致，使用 'access_token' 作为 key
 */
export function clearAuthToken() {
  localStorage.removeItem('access_token')
  sessionStorage.removeItem('access_token')
}

