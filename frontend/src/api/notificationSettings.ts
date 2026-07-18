import { api } from './client'

export interface NotificationSettings {
  id: string
  user_id: string
  study_reminder: boolean
  task_reminder: boolean
  achievement_notice: boolean
  system_notice: boolean
  email_notice: boolean
  push_notice: boolean
  created_at: string
  updated_at: string
}

export type NotificationSettingsUpdate = Partial<Omit<NotificationSettings, 'id' | 'user_id' | 'created_at' | 'updated_at'>>

// 获取通知设置
export function getNotificationSettings() {
  return api.get<NotificationSettings>('/notification-settings')
}

// 更新通知设置
export function updateNotificationSettings(data: NotificationSettingsUpdate) {
  return api.put<NotificationSettings>('/notification-settings', data)
}
