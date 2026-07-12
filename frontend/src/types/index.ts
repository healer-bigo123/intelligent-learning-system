export interface ModelInfo {
  id: string
  name: string
  provider: string
  description: string
  maxTokens: number
  cost: string
  available: boolean
}

export interface AgentInfo {
  id: string
  name: string
  type: string
  description: string
  icon: string
  color: string
  selectedModel: string
  tools: string[]
  status: 'active' | 'inactive' | 'loading'
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  agentId: string
  images?: string[]
}

export interface AgentSession {
  agentId: string
  messages: ChatMessage[]
  lastActivity: Date
}