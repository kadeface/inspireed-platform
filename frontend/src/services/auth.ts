import { api } from './api'
import type {
  LoginRequest,
  RegisterRegionOption,
  RegisterRequest,
  RegisterSchoolOption,
  TokenResponse,
  User,
} from '../types/user'

export const authService = {
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    return api.post<TokenResponse>('/auth/login', formData)
  },

  async register(userData: RegisterRequest): Promise<User> {
    return api.post<User>('/auth/register', userData)
  },

  async getRegisterSchools(search?: string): Promise<RegisterSchoolOption[]> {
    return api.get<RegisterSchoolOption[]>('/auth/register/schools', {
      params: search ? { search } : undefined,
    })
  },

  async getRegisterRegions(): Promise<RegisterRegionOption[]> {
    return api.get<RegisterRegionOption[]>('/auth/register/regions')
  },

  async getCurrentUser(): Promise<User> {
    return api.get<User>('/auth/me')
  },
}
