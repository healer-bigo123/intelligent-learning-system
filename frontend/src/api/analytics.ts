import { api } from './client'

export interface OverviewData {
  total_exercises: number
  correct_count: number
  accuracy_rate: number
  total_mistakes: number
  unsolved_mistakes: number
  streak_days: number
}

export interface SubjectTrendItem {
  subject: string
  total_exercises: number
  correct_count: number
  accuracy_rate: number
}

export interface WeakPointItem {
  knowledge_point: string
  total_attempts: number
  wrong_count: number
  error_rate: number
}

export interface ReportData {
  id: string
  content: string
  created_at: string
}

// 获取学习概览
export function getOverview() {
  return api.get<OverviewData>('/analytics/overview')
}

// 获取各科成绩趋势
export function getSubjectTrends() {
  return api.get<{ items: SubjectTrendItem[] }>('/analytics/subjects')
}

// 获取薄弱知识点
export function getWeakPoints() {
  return api.get<{ items: WeakPointItem[] }>('/analytics/weak-points')
}

// 生成评估报告
export function generateReport() {
  return api.post<ReportData>('/analytics/report/generate')
}

// 获取最新评估报告
export function getLatestReport() {
  return api.get<ReportData>('/analytics/report/latest')
}
