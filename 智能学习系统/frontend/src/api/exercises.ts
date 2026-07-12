/**
 * 练习测试 API 接口
 * 对应后端：/api/v1/exercises
 */
import { api } from './client'

// ========== 请求/响应类型 ==========

export interface ExerciseCreateRequest {
  subject: string
  type: 'choice' | 'fill_blank' | 'short_answer' | 'programming'
  question: string
  options?: string[]
  correct_answer: string
  explanation?: string
  knowledge_point?: string
  difficulty?: number
}

export interface ExerciseItem {
  id: string
  user_id: string
  subject: string
  type: string
  question: string
  options: string | null
  correct_answer: string
  explanation: string | null
  knowledge_point: string | null
  difficulty: number
  source: string
  status: string
  created_at: string
}

export interface ExerciseListResponse {
  total: number
  items: ExerciseItem[]
}

export interface ExerciseListParams {
  subject?: string
  type?: string
  difficulty?: number
  knowledge_point?: string
  page?: number
  page_size?: number
}

export interface ExerciseSubmitRequest {
  user_answer: string
  time_spent?: number
}

export interface ExerciseSubmitResponse {
  is_correct: boolean
  correct_answer: string
  explanation: string | null
  score: number
}

export interface ExerciseHistoryItem {
  record_id: string
  exercise_id: string
  question: string
  subject: string
  type: string
  user_answer: string | null
  correct_answer: string
  is_correct: boolean
  score: number
  time_spent: number
  created_at: string
}

export interface ExerciseHistoryResponse {
  total: number
  items: ExerciseHistoryItem[]
}

export interface ExerciseSessionCreateRequest {
  title?: string
  subject: string
  exercise_count?: number
  difficulty?: number
}

export interface ExerciseSessionItem {
  id: string
  user_id: string
  title: string | null
  subject: string
  exercise_ids: string
  total_count: number
  correct_count: number
  score: number
  status: string
  created_at: string
  completed_at: string | null
}

export interface ExerciseSessionResponse {
  total: number
  items: ExerciseSessionItem[]
}

export interface GenerateSessionResponse {
  session: ExerciseSessionItem
  exercises: Array<{
    id: string
    type: string
    question: string
    options: string[] | null
    difficulty: number
    knowledge_point: string | null
  }>
}

export interface SessionDetailResponse {
  session: ExerciseSessionItem
  exercises: Array<{
    id: string
    type: string
    question: string
    options: string[] | null
    difficulty: number
    knowledge_point: string | null
  }>
}

export interface CompleteSessionResponse {
  session: ExerciseSessionItem
  summary: {
    total: number
    correct: number
    wrong: number
    score: number
  }
}

// ========== 接口实现 ==========

/** 创建练习题 */
export const createExercise = async (data: ExerciseCreateRequest): Promise<ExerciseItem> => {
  const response = await api.post('/exercises', data)
  return response.data
}

/** 查询练习题列表 */
export const getExercises = async (params?: ExerciseListParams): Promise<ExerciseListResponse> => {
  const response = await api.get('/exercises', { params })
  return response.data
}

/** 获取练习历史 */
export const getExerciseHistory = async (params?: {
  subject?: string
  page?: number
  page_size?: number
}): Promise<ExerciseHistoryResponse> => {
  const response = await api.get('/exercises/history/list', { params })
  return response.data
}

/** 生成练习会话 */
export const generateExerciseSession = async (data: ExerciseSessionCreateRequest): Promise<GenerateSessionResponse> => {
  const response = await api.post('/exercises/sessions/generate', data)
  return response.data
}

/** 获取练习会话历史 */
export const getSessionHistory = async (params?: {
  subject?: string
  page?: number
  page_size?: number
}): Promise<ExerciseSessionResponse> => {
  const response = await api.get('/exercises/sessions/history/list', { params })
  return response.data
}

/** 获取练习会话详情 */
export const getExerciseSession = async (sessionId: string): Promise<SessionDetailResponse> => {
  const response = await api.get(`/exercises/sessions/${sessionId}`)
  return response.data
}

/** 完成练习会话 */
export const completeExerciseSession = async (sessionId: string): Promise<CompleteSessionResponse> => {
  const response = await api.post(`/exercises/sessions/${sessionId}/complete`)
  return response.data
}

/** 获取练习题详情（答题用，不含答案） */
export const getExercise = async (exerciseId: string): Promise<any> => {
  const response = await api.get(`/exercises/${exerciseId}`)
  return response.data
}

/** 获取练习题完整信息（含答案和解析） */
export const getExerciseFull = async (exerciseId: string): Promise<ExerciseItem> => {
  const response = await api.get(`/exercises/${exerciseId}/full`)
  return response.data
}

/** 提交答案 */
export const submitAnswer = async (exerciseId: string, data: ExerciseSubmitRequest): Promise<ExerciseSubmitResponse> => {
  const response = await api.post(`/exercises/${exerciseId}/submit`, data)
  return response.data
}
