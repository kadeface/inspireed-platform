import { api } from './api'
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '../types/user'

export const authService = {
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    // 不要手动设置Content-Type，让浏览器自动设置multipart/form-data with boundary
    return api.post<TokenResponse>('/auth/login', formData)
  },

  async register(userData: RegisterRequest): Promise<User> {
    return api.post<User>('/auth/register', userData)
  },

  async getCurrentUser(): Promise<User> {
    return api.get<User>('/auth/me')
  },
}

