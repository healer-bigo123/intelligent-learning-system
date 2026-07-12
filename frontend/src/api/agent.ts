/**
 * 前端智能体页面 API 接口
 * 备注：此文件包含智能体交互中心页面使用的所有 API 接口定义
 * 对应页面：src/immersive-agent.vue
 */

import type { AgentInfo, ModelInfo, ChatMessage } from '../types'

// 智能体列表
export const getAgents = async (): Promise<AgentInfo[]> => {
  const response = await fetch('/api/v1/agents/')
  return response.json()
}

// 获取智能体详情
export const getAgentById = async (agentId: string): Promise<AgentInfo> => {
  const response = await fetch(`/api/v1/agents/${agentId}`)
  return response.json()
}

// 向智能体发送消息
export const sendMessageToAgent = async (
  agentId: string,
  message: string,
  sessionId?: string
): Promise<ChatMessage> => {
  const response = await fetch('/api/v1/agents/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      agent_id: agentId,
      message,
      session_id: sessionId
    })
  })
  return response.json()
}

// 创建会话
export const createSession = async (agentId: string): Promise<{ session_id: string }> => {
  const response = await fetch('/api/v1/agents/sessions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ agent_id: agentId })
  })
  return response.json()
}

// 获取会话详情
export const getSession = async (sessionId: string): Promise<{
  session_id: string
  agent_id: string
  messages: ChatMessage[]
}> => {
  const response = await fetch(`/api/v1/agents/sessions/${sessionId}`)
  return response.json()
}

// 关闭会话
export const closeSession = async (sessionId: string): Promise<void> => {
  await fetch(`/api/v1/agents/sessions/${sessionId}`, {
    method: 'DELETE'
  })
}

// 意图识别
export const recognizeIntent = async (query: string): Promise<{
  intent_type: string
  entities: Record<string, string>
  urgency: 'low' | 'medium' | 'high'
  preferred_agent: string
  emotion_tag: string
}> => {
  const response = await fetch('/api/v1/agents/intent/recognize', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query })
  })
  return response.json()
}

// 获取可用模型列表
export const getModels = async (): Promise<ModelInfo[]> => {
  const response = await fetch('/api/v1/agents/models')
  return response.json()
}

// 设置当前模型
export const setCurrentModel = async (modelId: string): Promise<void> => {
  await fetch('/api/v1/agents/model/select', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ model_id: modelId })
  })
}

// 健康检查
export const checkHealth = async (): Promise<{
  status: 'healthy' | 'unhealthy'
  agents: number
  models: number
}> => {
  const response = await fetch('/api/v1/agents/health')
  return response.json()
}

// 添加短期记忆
export const addShortTermMemory = async (content: string): Promise<void> => {
  await fetch('/api/v1/agents/memory/short-term', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ content })
  })
}

// 添加长期记忆
export const addLongTermMemory = async (
  key: string,
  value: string | Record<string, unknown>
): Promise<void> => {
  await fetch('/api/v1/agents/memory/long-term', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ key, value })
  })
}