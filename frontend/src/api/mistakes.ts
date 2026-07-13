/**
 * 错题题库 API 接口
 * 对应后端：/api/v1/mistakes
 */
import { api } from './client'

// ========== 请求/响应类型 ==========

export interface MistakeCreateRequest {
  subject: string
  question: string
  correct_answer: string
  user_answer?: string
  analysis?: string
  knowledge_point?: string
  tags?: string[]
  source?: string
  difficulty?: number
}

export interface MistakeUpdateRequest {
  subject?: string
  question?: string
  correct_answer?: string
  user_answer?: string
  analysis?: string
  knowledge_point?: string
  tags?: string[]
  source?: string
  difficulty?: number
  status?: string
}

export interface MistakeItem {
  id: string
  user_id: string
  subject: string
  question: string
  correct_answer: string
  user_answer: string | null
  analysis: string | null
  knowledge_point: string | null
  tags: string
  source: string | null
  difficulty: number
  status: string
  review_count: number
  last_review_at: string | null
  created_at: string
  updated_at: string
}

export interface MistakeListResponse {
  total: number
  items: MistakeItem[]
}

export interface MistakeStatsResponse {
  total: number
  unsolved: number
  reviewing: number
  mastered: number
  by_subject: Record<string, number>
}

export interface MistakeListParams {
  subject?: string
  status?: string
  knowledge_point?: string
  keyword?: string
  page?: number
  page_size?: number
}

// ========== 接口实现 ==========

/** 添加错题 */
export const createMistake = async (data: MistakeCreateRequest): Promise<MistakeItem> => {
  const response = await api.post('/mistakes', data)
  return response.data
}

/** 查询错题列表（支持筛选和分页） */
export const getMistakes = async (params?: MistakeListParams): Promise<MistakeListResponse> => {
  const response = await api.get('/mistakes', { params })
  return response.data
}

/** 获取错题详情 */
export const getMistake = async (mistakeId: string): Promise<MistakeItem> => {
  const response = await api.get(`/mistakes/${mistakeId}`)
  return response.data
}

/** 更新错题 */
export const updateMistake = async (mistakeId: string, data: MistakeUpdateRequest): Promise<MistakeItem> => {
  const response = await api.put(`/mistakes/${mistakeId}`, data)
  return response.data
}

/** 删除错题 */
export const deleteMistake = async (mistakeId: string): Promise<void> => {
  await api.delete(`/mistakes/${mistakeId}`)
}

/** 复习错题 */
export const reviewMistake = async (mistakeId: string): Promise<{
  message: string
  review_count: number
  status: string
}> => {
  const response = await api.post(`/mistakes/${mistakeId}/review`)
  return response.data
}

/** 错题统计概览 */
export const getMistakeStats = async (): Promise<MistakeStatsResponse> => {
  const response = await api.get('/mistakes/stats/overview')
  return response.data
}
