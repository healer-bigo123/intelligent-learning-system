/**
 * 学习路径 API 接口
 * 对应后端：/api/v1/learning-paths
 */
import { api } from './client'

export interface LearningPathStep {
  title: string
  description?: string
  duration?: number
  status: 'pending' | 'in_progress' | 'completed'
}

export interface LearningPathCreateRequest {
  title: string
  description?: string
  steps: LearningPathStep[]
}

export interface LearningPathUpdateRequest {
  title?: string
  description?: string
  steps?: LearningPathStep[]
  status?: 'active' | 'completed' | 'paused'
}

export interface LearningPathItem {
  id: string
  user_id: string
  title: string
  description: string | null
  steps: string
  status: string
  created_at: string
  updated_at: string
}

export interface LearningPathListResponse {
  total: number
  items: LearningPathItem[]
}

export interface LearningPathProgressStats {
  total_paths: number
  active_paths: number
  completed_paths: number
  total_steps: number
  completed_steps: number
  overall_progress: number
}

export interface LearningPathListParams {
  status?: string
  page?: number
  page_size?: number
}

/** 创建学习路径 */
export const createLearningPath = async (data: LearningPathCreateRequest): Promise<LearningPathItem> => {
  const response = await api.post('/learning-paths', data)
  return response.data
}

/** 查询学习路径列表 */
export const getLearningPaths = async (params?: LearningPathListParams): Promise<LearningPathListResponse> => {
  const response = await api.get('/learning-paths', { params })
  return response.data
}

/** 获取学习路径详情 */
export const getLearningPath = async (pathId: string): Promise<LearningPathItem> => {
  const response = await api.get(`/learning-paths/${pathId}`)
  return response.data
}

/** 更新学习路径 */
export const updateLearningPath = async (
  pathId: string,
  data: LearningPathUpdateRequest
): Promise<LearningPathItem> => {
  const response = await api.put(`/learning-paths/${pathId}`, data)
  return response.data
}

/** 删除学习路径 */
export const deleteLearningPath = async (pathId: string): Promise<void> => {
  await api.delete(`/learning-paths/${pathId}`)
}

/** 完成某个步骤 */
export const completeLearningPathStep = async (
  pathId: string,
  stepIndex: number
): Promise<{ message: string; step_index: number; path_status: string }> => {
  const response = await api.post(`/learning-paths/${pathId}/steps/${stepIndex}/complete`)
  return response.data
}

/** 获取学习进度统计 */
export const getLearningPathProgress = async (): Promise<LearningPathProgressStats> => {
  const response = await api.get('/learning-paths/stats/progress')
  return response.data
}
