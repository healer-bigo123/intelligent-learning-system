import { api } from './client'

export interface UserInfo {
  id: string
  username: string
  email: string
  phone: string
  nickname: string
  avatar: string | null
  role: string
  created_at: string
}

export interface UpdateProfileData {
  nickname?: string
  email?: string
  phone?: string
  avatar?: string
}

// 获取当前用户信息
export function getProfile() {
  return api.get<UserInfo>('/auth/me')
}

// 更新用户资料（后端使用 query params）
export function updateProfile(data: UpdateProfileData) {
  return api.put('/auth/profile', null, { params: data })
}

// 修改密码
export function changePassword(oldPassword: string, newPassword: string) {
  return api.put('/auth/password', {
    old_password: oldPassword,
    new_password: newPassword
  })
}
