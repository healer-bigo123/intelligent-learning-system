/**
 * 智能体 API 接口
 * 对应后端：/api/v1/agents
 * 对应页面：src/immersive-agent.vue
 */
import { api } from './client'

// ========== 请求/响应类型 ==========

export interface AgentResponse {
  id: string
  name: string
  description: string
  status: string
  tools?: string[]
}

export interface AgentListResponse {
  agents: AgentResponse[]
  total: number
}

export interface QueryRequest {
  user_input: string
  user_id: string
  session_id?: string
}

export interface QueryResponse {
  session_id: string
  intent: string
  result: Record<string, any>
  tasks_executed: number
  timestamp: string
}

export interface SessionInfo {
  session_id: string
  user_id: string
  task_count: number
  conversation_history_count: number
  created_at: string
  last_active_at: string
}

export interface HealthResponse {
  status: string
  agents_count: number
  sessions_count: number
  timestamp: string
}

export interface IntentResponse {
  intent_type: string
  entities: Record<string, string>
  urgency: 'low' | 'medium' | 'high'
  preferred_agent: string
  emotion_tag: string
  raw_input: string
}

// ========== 智能体管理 ==========

/** 获取智能体列表 */
export const getAgents = async (): Promise<AgentListResponse> => {
  const response = await api.get('/agents/')
  return response.data
}

/** 获取智能体详情 */
export const getAgentById = async (agentId: string): Promise<AgentResponse> => {
  const response = await api.get(`/agents/${agentId}`)
  return response.data
}

// ========== 消息与会话 ==========

/** 向智能体发送查询 */
export const queryAgent = async (data: QueryRequest): Promise<QueryResponse> => {
  const response = await api.post('/agents/query', data)
  return response.data
}

/** 创建会话 */
export const createSession = async (userId: string): Promise<SessionInfo> => {
  const response = await api.post('/agents/sessions', null, {
    params: { user_id: userId }
  })
  return response.data
}

/** 获取会话信息 */
export const getSession = async (sessionId: string): Promise<SessionInfo> => {
  const response = await api.get(`/agents/sessions/${sessionId}`)
  return response.data
}

/** 关闭会话 */
export const closeSession = async (sessionId: string): Promise<void> => {
  await api.delete(`/agents/sessions/${sessionId}`)
}

/** 获取会话任务列表 */
export const getSessionTasks = async (sessionId: string): Promise<any[]> => {
  const response = await api.get(`/agents/sessions/${sessionId}/tasks`)
  return response.data
}

// ========== 意图识别 ==========

/** 意图识别 */
export const recognizeIntent = async (userInput: string, sessionId?: string, userId?: string): Promise<IntentResponse> => {
  const response = await api.post('/agents/intent/recognize', null, {
    params: { user_input: userInput, session_id: sessionId, user_id: userId }
  })
  return response.data
}

// ========== 记忆管理 ==========

/** 添加短期记忆 */
export const addShortTermMemory = async (sessionId: string, content: Record<string, any>): Promise<void> => {
  await api.post('/agents/memory/short-term', content, {
    params: { session_id: sessionId }
  })
}

/** 获取短期记忆 */
export const getShortTermMemory = async (sessionId: string): Promise<any> => {
  const response = await api.get(`/agents/memory/short-term/${sessionId}`)
  return response.data
}

/** 添加长期记忆 */
export const addLongTermMemory = async (userId: string, key: string, value: any): Promise<void> => {
  await api.post('/agents/memory/long-term', null, {
    params: { user_id: userId, key, value: typeof value === 'string' ? value : JSON.stringify(value) }
  })
}

/** 获取长期记忆 */
export const getLongTermMemory = async (userId: string, key?: string): Promise<any> => {
  const response = await api.get(`/agents/memory/long-term/${userId}`, {
    params: { key }
  })
  return response.data
}

// ========== 模型管理 ==========

export interface ModelResponse {
  id: string
  name: string
  provider: string
  description: string
  available: boolean
}

export interface ModelsResponse {
  models: ModelResponse[]
  current_model: string
}

export interface ModelSelectResponse {
  message: string
  current_model: string
}

/** 获取可用模型列表 */
export const getModels = async (): Promise<ModelsResponse> => {
  const response = await api.get('/agents/models')
  return response.data
}

/** 设置当前模型 */
export const selectModel = async (modelId: string): Promise<ModelSelectResponse> => {
  const response = await api.post('/agents/model/select', { model_id: modelId })
  return response.data
}

// ========== 健康检查 ==========

/** 健康检查 */
export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await api.get('/agents/health')
  return response.data
}
