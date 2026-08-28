export interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
}

export interface TokenResponse {
  access: string
  refresh: string
}

export interface LoginCredentials {
  username: string
  password: string
}