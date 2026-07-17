import { api } from './client'

export interface NotificationItem {
  id: string
  user_id: string
  title: string
  content: string
  type: string
  is_read: boolean
  created_at: string
}

export interface NotificationListResponse {
  total: number
  items: NotificationItem[]
}

export interface UnreadCountResponse {
  count: number
}

/** 获取通知列表（支持分页和筛选） */
export function getNotifications(params?: {
  is_read?: boolean
  page?: number
  page_size?: number
}): Promise<NotificationListResponse> {
  return api.get('/notifications', { params }).then(res => res.data)
}

/** 获取未读通知数量 */
export function getUnreadCount(): Promise<UnreadCountResponse> {
  return api.get('/notifications/unread-count').then(res => res.data)
}

/** 标记单条通知为已读 */
export function markAsRead(id: string): Promise<NotificationItem> {
  return api.put(`/notifications/${id}/read`).then(res => res.data)
}

/** 标记所有通知为已读 */
export function markAllAsRead(): Promise<{ message: string }> {
  return api.put('/notifications/read-all').then(res => res.data)
}

/** 删除通知 */
export function deleteNotification(id: string): Promise<void> {
  return api.delete(`/notifications/${id}`).then(() => {})
}
