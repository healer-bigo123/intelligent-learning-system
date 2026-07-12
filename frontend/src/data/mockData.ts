import type { AgentInfo, ModelInfo } from '@/types'

export const mockModels: ModelInfo[] = [
  {
    id: 'doubao-3.5',
    name: '豆包 3.5',
    provider: '字节跳动',
    description: '中文理解能力强，响应速度快',
    maxTokens: 4096,
    cost: '免费',
    available: true
  },
  {
    id: 'qwen-turbo',
    name: '通义千问 Turbo',
    provider: '阿里云',
    description: '代码能力强，长上下文支持',
    maxTokens: 8192,
    cost: '按量计费',
    available: true
  },
  {
    id: 'ernie-4.0',
    name: '文心一言 4.0',
    provider: '百度',
    description: '知识问答能力强',
    maxTokens: 4096,
    cost: '按量计费',
    available: true
  },
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4o Mini',
    provider: 'OpenAI',
    description: '通用能力强，多模态支持',
    maxTokens: 16384,
    cost: '按量计费',
    available: false
  },
  {
    id: 'deepseek-v3',
    name: 'DeepSeek V3',
    provider: '深度求索',
    description: '长上下文处理能力强',
    maxTokens: 251201,
    cost: '按量计费',
    available: true
  },
  {
    id: 'spark-3.5',
    name: '讯飞星火 3.5',
    provider: '科大讯飞',
    description: '语音交互能力强',
    maxTokens: 8192,
    cost: '按量计费',
    available: true
  }
]

export const mockAgents: AgentInfo[] = [
  {
    id: 'qa',
    name: '答疑Agent',
    type: 'qa',
    description: '回答学科问题、解释概念、梳理解题思路',
    icon: 'HelpCircle',
    color: '#6366f1',
    selectedModel: 'doubao-3.5',
    tools: ['知识库检索', '题库检索', '公式渲染'],
    status: 'active'
  },
  {
    id: 'planning',
    name: '规划Agent',
    type: 'planning',
    description: '制定日/周/月学习计划，动态调整优先级',
    icon: 'Calendar',
    color: '#10b981',
    selectedModel: 'qwen-turbo',
    tools: ['学生画像', '资源推荐', '时间分析'],
    status: 'active'
  },
  {
    id: 'grading',
    name: '批改Agent',
    type: 'grading',
    description: '批改主观题、作文、代码，给出评分与改进建议',
    icon: 'CheckSquare',
    color: '#f59e0b',
    selectedModel: 'ernie-4.0',
    tools: ['图像识别', '代码执行', '评分标准'],
    status: 'active'
  },
  {
    id: 'companion',
    name: '陪伴Agent',
    type: 'companion',
    description: '情感支持、学习动力激励、焦虑缓解',
    icon: 'Heart',
    color: '#ef4444',
    selectedModel: 'doubao-3.5',
    tools: ['情绪识别', '正向反馈', '成长可视化'],
    status: 'active'
  },
  {
    id: 'recommendation',
    name: '推荐Agent',
    type: 'recommendation',
    description: '推荐学习资源、同类题、拓展阅读、学习搭子',
    icon: 'Sparkles',
    color: '#3b82f6',
    selectedModel: 'deepseek-v3',
    tools: ['协同过滤', '内容匹配', '画像相似度'],
    status: 'active'
  },
  {
    id: 'analytics',
    name: '分析Agent',
    type: 'analytics',
    description: '学情分析、知识图谱构建、学习效果归因',
    icon: 'BarChart3',
    color: '#8b5cf6',
    selectedModel: 'qwen-turbo',
    tools: ['数据聚合', '知识图谱', '统计模型'],
    status: 'active'
  }
]