import { api } from './client'

export interface AchievementItem {
  id: string
  name: string
  description: string
  icon: string | null
  condition_type: string
  condition_value: number
  created_at: string
}

export interface MyAchievementItem {
  achievement: AchievementItem
  unlocked_at: string
}

export interface MyAchievementListResponse {
  total: number
  items: MyAchievementItem[]
}

export interface CheckAchievementResponse {
  newly_unlocked: AchievementItem[]
}

export interface LeaderboardItem {
  user_id: string
  unlocked_count: number
}

export interface LeaderboardResponse {
  items: LeaderboardItem[]
}

/** 获取所有成就列表 */
export function getAchievements(): Promise<AchievementItem[]> {
  return api.get('/achievements').then(res => res.data)
}

/** 获取当前用户已解锁的成就 */
export function getMyAchievements(): Promise<MyAchievementListResponse> {
  return api.get('/achievements/my').then(res => res.data)
}

/** 检查并解锁成就 */
export function checkAchievements(): Promise<CheckAchievementResponse> {
  return api.post('/achievements/check').then(res => res.data)
}

/** 获取排行榜 */
export function getLeaderboard(limit = 20): Promise<LeaderboardResponse> {
  return api.get('/achievements/leaderboard', { params: { limit } }).then(res => res.data)
}
