import { api } from './client'

export interface Goal {
  id: string
  user_id: string
  title: string
  description: string | null
  color: string
  icon: string
  progress: number
  deadline: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface GoalCreateData {
  title: string
  description?: string
  color?: string
  icon?: string
  progress?: number
  deadline?: string
}

export interface GoalUpdateData {
  title?: string
  description?: string
  color?: string
  icon?: string
  progress?: number
  deadline?: string
  status?: string
}

export interface GoalListResponse {
  total: number
  items: Goal[]
}

// 获取学习目标列表
export function getGoals(status?: string) {
  return api.get<GoalListResponse>('/goals', { params: status ? { status } : {} })
}

// 创建学习目标
export function createGoal(data: GoalCreateData) {
  return api.post<Goal>('/goals', data)
}

// 更新学习目标
export function updateGoal(goalId: string, data: GoalUpdateData) {
  return api.put<Goal>(`/goals/${goalId}`, data)
}

// 删除学习目标
export function deleteGoal(goalId: string) {
  return api.delete(`/goals/${goalId}`)
}