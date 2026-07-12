<template>
  <div class="immersive-container">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-left">
        <div class="logo-wrapper">
          <div class="logo-icon" :style="{ background: selectedAgent?.color || '#6366f1' }">
            <component :is="getIcon(selectedAgent?.icon || 'Bot')" class="icon" />
          </div>
          <div class="logo-text">
            <h1 class="app-title">智能体交互中心</h1>
            <p class="app-subtitle">{{ selectedAgent?.name || '选择智能体开始对话' }}</p>
          </div>
        </div>
      </div>
      
      <div class="header-center">
        <div class="stats-bar">
          <div class="stat-item">
            <span class="stat-icon online-icon"></span>
            <span class="stat-value">{{ onlineAgents }}</span>
            <span class="stat-label">在线</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-icon model-icon"></span>
            <span class="stat-value">{{ availableModels }}</span>
            <span class="stat-label">模型</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-icon chat-icon"></span>
            <span class="stat-value">{{ todaySessions }}</span>
            <span class="stat-label">今日会话</span>
          </div>
        </div>
      </div>
      
      <div class="header-right">
        <button class="nav-btn" @click="showConfigPanel = !showConfigPanel">
          <component :is="icons.Settings" class="nav-icon" />
          配置
        </button>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 中间聊天区域 -->
      <section class="chat-area">
        <!-- 聊天消息 -->
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-icon-wrapper">
              <component :is="getIcon(selectedAgent?.icon || 'MessageCircle')" class="empty-icon" />
            </div>
            <h3 class="empty-title">{{ selectedAgent?.name || '智能体' }}等待您的提问</h3>
            <p class="empty-desc">输入您的问题，{{ selectedAgent?.name || '智能体' }}将为您提供专业帮助</p>
            
            <div class="quick-actions">
              <button 
                v-for="question in quickQuestions" 
                :key="question"
                class="quick-btn"
                @click="sendQuickQuestion(question)"
              >
                {{ question }}
              </button>
            </div>
          </div>
          
          <TransitionGroup name="message" tag="div" class="messages-list">
            <div
              v-for="message in messages"
              :key="message.id"
              class="message-item"
              :class="message.role"
            >
              <div class="message-avatar">
                <component 
                  :is="message.role === 'user' ? icons.User : getIcon(selectedAgent?.icon || 'Bot')" 
                  class="avatar-img" 
                />
              </div>
              <div class="message-content">
                <div class="message-bubble">
                  <p class="message-text">{{ message.content }}</p>
                </div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </TransitionGroup>
          
          <div v-if="isLoading" class="typing-indicator">
            <div class="typing-dots">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
            <span class="typing-text">{{ selectedAgent?.name }}正在思考...</span>
          </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="input-container">
          <div class="input-wrapper">
            <!-- 上传的图片预览 -->
            <div v-if="uploadedImages.length > 0" class="uploaded-images">
              <div 
                v-for="(img, index) in uploadedImages" 
                :key="index" 
                class="uploaded-image-item"
              >
                <img :src="img.url" :alt="img.name" class="uploaded-image" />
                <button class="remove-image-btn" @click="removeImage(index)">
                  <component :is="icons.X" class="remove-icon" />
                </button>
              </div>
            </div>
            
            <textarea
              v-model="inputMessage"
              class="message-input"
              placeholder="输入您的问题...或上传图片进行识别批改"
              rows="1"
              @keydown.ctrl.enter="sendMessage"
              @keydown.meta.enter="sendMessage"
            ></textarea>
            
            <div class="select-buttons">
              <!-- 图片上传按钮 -->
              <button class="mini-select-btn upload-btn" @click="triggerImageUpload">
                <component :is="icons.Image" class="select-icon" />
                <span class="select-name">图片</span>
              </button>
              <input 
                type="file" 
                ref="imageInputRef"
                class="image-upload-input"
                accept="image/*"
                multiple
                @change="handleImageUpload"
              />
              
              <!-- 智能体选择按钮 -->
              <button class="mini-select-btn agent-btn" @click="showAgentModal = true">
                <component :is="getIcon(selectedAgent?.icon || 'Bot')" class="select-icon" />
                <span class="select-name">{{ getAgentShortName(selectedAgent?.name) }}</span>
              </button>
              
              <!-- 模型选择按钮 -->
              <button class="mini-select-btn model-btn" @click="showModelModal = true">
                <component :is="icons.Cpu" class="select-icon" />
                <span class="select-name">{{ getModelShortName(currentModelId) }}</span>
              </button>
            </div>
            
            <button 
              class="send-btn"
              :class="{ disabled: (!inputMessage.trim() && uploadedImages.length === 0) || isLoading }"
              :disabled="(!inputMessage.trim() && uploadedImages.length === 0) || isLoading"
              @click="sendMessage"
            >
              <component :is="icons.Send" class="send-icon" />
            </button>
          </div>
          
          <div class="input-hint">
            <span>Ctrl + Enter 发送</span>
            <span class="divider">|</span>
            <span>支持图片上传识别批改</span>
            <span class="divider">|</span>
            <span>{{ selectedAgent?.description }}</span>
          </div>
        </div>
      </section>

      <!-- 右侧配置面板 -->
      <Transition name="slide">
        <aside class="config-sidebar" v-if="showConfigPanel">
          <div class="config-header">
            <h2 class="config-title">
              <component :is="icons.Settings" class="title-icon" />
              系统配置
            </h2>
            <button class="close-btn" @click="showConfigPanel = false">
              <component :is="icons.X" class="close-icon" />
            </button>
          </div>
          <div class="config-content">
            <div class="config-section">
              <h3>参数设置</h3>
              <div class="param-item">
                <label>温度系数</label>
                <input type="range" v-model="modelParams.temperature" min="0" max="1" step="0.1" />
                <span>{{ modelParams.temperature }}</span>
              </div>
              <div class="param-item">
                <label>最大Token</label>
                <input type="number" v-model="modelParams.maxTokens" />
              </div>
            </div>
          </div>
        </aside>
      </Transition>
    </main>

    <!-- 模型选择弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div class="modal-overlay" v-if="showModelModal" @click.self="showModelModal = false">
          <div class="modal-content">
            <div class="modal-header">
              <h3 class="modal-title">
                <component :is="icons.Cpu" class="modal-icon" />
                选择大模型
              </h3>
              <button class="modal-close" @click="showModelModal = false">
                <component :is="icons.X" class="close-icon" />
              </button>
            </div>
            
            <div class="modal-body">
              <div class="model-grid">
                <div
                  v-for="model in models"
                  :key="model.id"
                  class="model-card"
                  :class="{ selected: currentModelId === model.id, disabled: !model.available }"
                  @click="selectModel(model)"
                >
                  <div class="model-radio">
                    <div class="radio-circle" :class="{ checked: currentModelId === model.id }"></div>
                  </div>
                  <div class="model-details">
                    <div class="model-title">{{ model.name }}</div>
                    <div class="model-provider">{{ model.provider }}</div>
                    <div class="model-desc">{{ model.description }}</div>
                  </div>
                  <div class="model-cost" :class="{ premium: model.cost !== '免费' }">
                    {{ model.cost }}
                  </div>
                </div>
              </div>
            </div>
            
            <div class="modal-footer">
              <button class="btn-cancel" @click="showModelModal = false">取消</button>
              <button class="btn-confirm" @click="confirmModel">确认选择</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 智能体选择弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div class="modal-overlay" v-if="showAgentModal" @click.self="showAgentModal = false">
          <div class="modal-content agent-modal">
            <div class="modal-header">
              <h3 class="modal-title">
                <component :is="icons.Bot" class="modal-icon" />
                选择智能体
              </h3>
              <button class="modal-close" @click="showAgentModal = false">
                <component :is="icons.X" class="close-icon" />
              </button>
            </div>
            
            <div class="modal-body">
              <div class="agent-grid">
                <div
                  v-for="agent in agents"
                  :key="agent.id"
                  class="agent-option"
                  :class="{ selected: selectedAgent?.id === agent.id, disabled: agent.status === 'inactive' }"
                  @click="selectAgentFromModal(agent)"
                >
                  <div class="agent-option-avatar" :style="{ background: agent.color }">
                    <component :is="getIcon(agent.icon)" class="avatar-icon" />
                  </div>
                  <div class="agent-option-info">
                    <div class="agent-option-name">{{ agent.name }}</div>
                    <div class="agent-option-status" :class="agent.status">
                      <span class="status-dot"></span>
                      {{ getStatusText(agent.status) }}
                    </div>
                  </div>
                  <div class="agent-option-radio">
                    <div class="radio-circle" :class="{ checked: selectedAgent?.id === agent.id }"></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="modal-footer">
              <button class="btn-cancel" @click="showAgentModal = false">取消</button>
              <button class="btn-confirm" @click="confirmAgent">确认选择</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 背景动效 -->
    <div class="background-effects">
      <div class="bg-blob blob-1"></div>
      <div class="bg-blob blob-2"></div>
      <div class="bg-blob blob-3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, type Component } from 'vue'
import {
  Bot, MessageCircle, Send, User, Settings, Cpu, X,
  HelpCircle, Calendar, CheckSquare, Heart, Star, BarChart, ChevronLeft, ChevronRight,
  Image, Upload, Paperclip
} from 'lucide-vue-next'
import type { AgentInfo, ModelInfo, ChatMessage } from './types'
import { mockAgents, mockModels } from './data/mockData'

const icons = { Bot, MessageCircle, Send, User, Settings, Cpu, X, ChevronLeft, ChevronRight, Image, Upload, Paperclip }

const iconMap: Record<string, Component> = {
  HelpCircle, Calendar, CheckSquare, Heart, Star, BarChart, Bot
}

const getIcon = (iconName: string): Component => {
  return iconMap[iconName] || Bot
}

const agents = ref<AgentInfo[]>(mockAgents)
const models = ref<ModelInfo[]>(mockModels)
const selectedAgent = ref<AgentInfo | null>(agents.value[0])
const currentModelId = ref(selectedAgent.value?.selectedModel || '')
const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const showConfigPanel = ref(false)
const showModelModal = ref(false)
const showAgentModal = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const imageInputRef = ref<HTMLInputElement | null>(null)

interface UploadedImage {
  url: string
  name: string
  file: File
}
const uploadedImages = ref<UploadedImage[]>([])

const todaySessions = ref(12)

const onlineAgents = computed(() => agents.value.filter(a => a.status === 'active').length)
const availableModels = computed(() => models.value.filter(m => m.available).length)

const modelParams = ref({
  temperature: 0.7,
  maxTokens: 2048
})

const quickQuestions = [
  '你好，请问你能帮我做什么？',
  '如何制定学习计划？',
  '推荐一些学习资源',
  '分析我的学习情况'
]

const getAgentResponse = (userInput: string): string => {
  const responses: Record<string, string> = {
    '你好，请问你能帮我做什么？': '你好！我是智能学习助手，可以帮助你解答问题、制定学习计划、批改作业、推荐学习资源等。请问有什么可以帮你的？',
    '如何制定学习计划？': '制定学习计划需要考虑以下几点：\n1. 明确学习目标和时间期限\n2. 评估当前水平和可用时间\n3. 分解任务，制定优先级\n4. 安排每日学习时间\n5. 定期复盘和调整计划\n需要我帮你制定一个具体的计划吗？',
    '推荐一些学习资源': '好的！根据你的学习需求，我可以推荐：\n- 数学：可汗学院、Coursera数学课程\n- 编程：LeetCode、Codecademy\n- 英语：BBC Learning English、Duolingo\n- 物理：MIT OpenCourseWare\n需要更具体的推荐吗？',
    '分析我的学习情况': '当然可以！我可以从以下方面分析你的学习情况：\n- 学习时长和频率\n- 科目分布和进度\n- 任务完成情况\n- 薄弱环节识别\n- 改进建议\n需要我为你生成一份详细的分析报告吗？'
  }
  return responses[userInput] || `我已收到你的问题："${userInput}"。我来为你提供专业的解答和帮助。`
}

watch(selectedAgent, (newAgent) => {
  if (newAgent) {
    currentModelId.value = newAgent.selectedModel
  }
})

const selectAgentFromModal = (agent: AgentInfo) => {
  if (agent.status === 'active') {
    selectedAgent.value = agent
    currentModelId.value = agent.selectedModel
  }
}

const confirmAgent = () => {
  if (selectedAgent.value) {
    messages.value = []
  }
  showAgentModal.value = false
}

const getModelShortName = (modelId: string): string => {
  const model = models.value.find(m => m.id === modelId)
  return model?.name.split(' ')[0] || modelId
}

const getAgentShortName = (agentName?: string): string => {
  if (!agentName) return '智能体'
  return agentName.replace('Agent', '').trim() || agentName
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    active: '在线',
    inactive: '离线',
    loading: '加载中'
  }
  return statusMap[status] || status
}

const formatTime = (timestamp: Date): string => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const selectModel = (model: ModelInfo) => {
  if (model.available) {
    currentModelId.value = model.id
  }
}

const confirmModel = () => {
  if (selectedAgent.value) {
    selectedAgent.value.selectedModel = currentModelId.value
  }
  showModelModal.value = false
}

const triggerImageUpload = () => {
  imageInputRef.value?.click()
}

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files) return
  
  Array.from(files).forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        uploadedImages.value.push({
          url: e.target?.result as string,
          name: file.name,
          file
        })
      }
      reader.readAsDataURL(file)
    }
  })
  
  target.value = ''
}

const removeImage = (index: number) => {
  uploadedImages.value.splice(index, 1)
}

const sendMessage = async () => {
  const content = inputMessage.value.trim()
  if (!content && uploadedImages.value.length === 0) return
  
  isLoading.value = true
  
  const hasImages = uploadedImages.value.length > 0
  let messageContent = content
  
  if (hasImages) {
    messageContent = `${content}\n\n[图片: ${uploadedImages.value.length} 张]`
  }
  
  const userMessage: ChatMessage = {
    id: `msg-${Date.now()}`,
    role: 'user',
    content: messageContent,
    timestamp: new Date(),
    agentId: selectedAgent.value?.id || '',
    images: hasImages ? uploadedImages.value.map(img => img.url) : undefined
  }
  messages.value.push(userMessage)
  inputMessage.value = ''
  uploadedImages.value = []
  
  await nextTick(() => scrollToBottom())
  
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    let responseContent = ''
    if (hasImages) {
      responseContent = '已收到你上传的图片，我来帮你进行识别和批改。\n\n根据图片内容分析：\n- 图像识别完成\n- 内容分析中...\n\n【识别结果】\n我已识别到图片中的内容，以下是我的分析和批改：\n\n1. **内容识别**：图片中显示的是学习相关的内容\n2. **分析结果**：经分析，你的答案是正确的/需要改进...\n3. **建议**：继续努力，保持良好的学习习惯！\n\n如果需要更详细的分析，请提供更多信息。'
    } else {
      responseContent = getAgentResponse(content)
    }
    
    const response: ChatMessage = {
      id: `msg-${Date.now()}-bot`,
      role: 'assistant',
      content: responseContent,
      timestamp: new Date(),
      agentId: selectedAgent.value?.id || ''
    }
    messages.value.push(response)
    
    await nextTick(() => scrollToBottom())
  } catch (error) {
    console.error('发送失败:', error)
  } finally {
    isLoading.value = false
  }
}

const sendQuickQuestion = (question: string) => {
  inputMessage.value = question
  sendMessage()
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style lang="scss">
:root {
  --primary-color: #6366f1;
  --primary-light: #818cf8;
  --primary-dark: #4f46e5;
  --bg-primary: #0a0a0f;
  --bg-secondary: #111118;
  --bg-tertiary: #1a1a24;
  --bg-card: #16161f;
  --text-primary: #ffffff;
  --text-secondary: #a0a0b0;
  --text-muted: #6b7280;
  --border-color: #2a2a3a;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  overflow: hidden;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.immersive-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 背景动效 */
.background-effects {
  position: fixed;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  animation: blobFloat 20s infinite ease-in-out;
}

.blob-1 {
  width: 400px;
  height: 400px;
  background: var(--primary-color);
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.blob-2 {
  width: 300px;
  height: 300px;
  background: #f472b6;
  bottom: -50px;
  right: -50px;
  animation-delay: -7s;
}

.blob-3 {
  width: 250px;
  height: 250px;
  background: #3b82f6;
  top: 50%;
  right: 30%;
  animation-delay: -14s;
}

@keyframes blobFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(50px, 30px) scale(1.1); }
  66% { transform: translate(-30px, 50px) scale(0.9); }
}

/* 顶部导航 */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: rgba(17, 17, 24, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  position: relative;
  z-index: 100;
}

.header-left {
  flex: 1;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  
  .icon {
    width: 24px;
    height: 24px;
    color: white;
  }
}

.logo-text {
  .app-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
  }
  
  .app-subtitle {
    font-size: 12px;
    color: var(--text-muted);
    margin: 2px 0 0;
  }
}

.header-center {
  flex: 2;
  display: flex;
  justify-content: center;
}

.stats-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  background: var(--bg-tertiary);
  padding: 10px 24px;
  border-radius: var(--radius-xl);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .stat-icon {
    width: 16px;
    height: 16px;
    border-radius: 50%;
  }
  
  .online-icon { background: var(--success-color); box-shadow: 0 0 8px var(--success-color); }
  .model-icon { background: var(--primary-color); box-shadow: 0 0 8px var(--primary-color); }
  .chat-icon { background: var(--warning-color); box-shadow: 0 0 8px var(--warning-color); }
  
  .stat-value {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
  }
  
  .stat-label {
    font-size: 12px;
    color: var(--text-muted);
  }
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: var(--border-color);
}

.header-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-card);
    border-color: var(--primary-color);
    color: var(--text-primary);
  }
  
  .nav-icon {
    width: 16px;
    height: 16px;
  }
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
  z-index: 10;
}

/* 左侧智能体面板 */
.agents-sidebar {
  width: 280px;
  background: rgba(22, 22, 31, 0.9);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
}

.agents-sidebar.collapsed {
  width: 80px;
}

.collapse-btn {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 48px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-card);
    border-color: var(--primary-color);
  }
  
  .collapse-icon {
    width: 14px;
    height: 14px;
    color: var(--text-secondary);
  }
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow-y: auto;
}

.sidebar-header {
  margin-bottom: 20px;
  
  .sidebar-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary);
    
    .title-icon {
      width: 18px;
      height: 18px;
    }
  }
}

.agents-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.agent-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: var(--bg-tertiary);
  border: 1px solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    transform: translateX(4px);
    border-color: var(--border-color);
    background: var(--bg-card);
  }
  
  &.active {
    border-color: var(--primary-color);
    background: rgba(99, 102, 241, 0.1);
    
    .agent-glow {
      opacity: 0.3;
    }
  }
  
  .agent-avatar {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    
    .avatar-icon {
      width: 20px;
      height: 20px;
      color: white;
    }
  }
  
  .agent-info {
    flex: 1;
    min-width: 0;
    
    .agent-name {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 4px;
    }
    
    .agent-status {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      color: var(--text-muted);
      
      .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
      }
      
      &.active .status-dot { background: var(--success-color); box-shadow: 0 0 6px var(--success-color); }
      &.inactive .status-dot { background: var(--text-muted); }
      &.loading .status-dot { background: var(--warning-color); animation: pulse 1s infinite; }
    }
  }
  
  .agent-model {
    background: var(--bg-primary);
    padding: 4px 10px;
    border-radius: 10px;
    font-size: 11px;
    color: var(--text-secondary);
    flex-shrink: 0;
  }
  
  .agent-glow {
    position: absolute;
    top: -50%;
    right: -50%;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 中间聊天区域 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: rgba(10, 10, 15, 0.6);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon-wrapper {
  width: 100px;
  height: 100px;
  background: var(--bg-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
  
  .empty-icon {
    width: 48px;
    height: 48px;
    color: var(--primary-color);
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.empty-title {
  font-size: 20px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 24px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.quick-btn {
  padding: 10px 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-card);
    border-color: var(--primary-color);
    color: var(--text-primary);
  }
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  gap: 12px;
  animation: messageIn 0.3s ease-out;
}

@keyframes messageIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  flex-direction: row-reverse;
  
  .message-bubble {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    border-radius: var(--radius-md) var(--radius-md) 0 var(--radius-md);
  }
}

.message-item.assistant {
  .message-bubble {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md) var(--radius-md) var(--radius-md) 0;
  }
}

.message-avatar {
  width: 40px;
  height: 40px;
  background: var(--bg-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  .avatar-img {
    width: 18px;
    height: 18px;
    color: var(--text-secondary);
  }
}

.message-content {
  max-width: 60%;
  
  .message-bubble {
    padding: 14px 18px;
    
    .message-text {
      font-size: 14px;
      line-height: 1.6;
      color: var(--text-primary);
      margin: 0;
      white-space: pre-wrap;
    }
  }
  
  .message-time {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 6px;
    padding: 0 4px;
  }
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  width: fit-content;
  
  .typing-dots {
    display: flex;
    gap: 5px;
    
    .dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--primary-color);
      animation: typing 1.4s infinite ease-in-out;
      
      &:nth-child(1) { animation-delay: 0s; }
      &:nth-child(2) { animation-delay: 0.2s; }
      &:nth-child(3) { animation-delay: 0.4s; }
    }
  }
  
  .typing-text {
    font-size: 13px;
    color: var(--text-secondary);
  }
}

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

/* 输入区域 */
.input-container {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: rgba(17, 17, 24, 0.9);
  backdrop-filter: blur(20px);
}

.input-wrapper {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  flex-wrap: wrap;
}

/* 上传的图片预览 */
.uploaded-images {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  width: 100%;
  margin-bottom: 10px;
}

.uploaded-image-item {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 2px solid var(--border-color);
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--primary-color);
  }
}

.uploaded-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image-btn {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 22px;
  height: 22px;
  background: var(--error-color);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: scale(1.1);
    background: #dc2626;
  }
}

.remove-icon {
  width: 12px;
  height: 12px;
  color: white;
}

/* 图片上传隐藏input */
.image-upload-input {
  display: none;
}

.message-input {
  flex: 1;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 14px 20px;
  color: var(--text-primary);
  font-size: 14px;
  resize: none;
  min-height: 48px;
  max-height: 200px;
  overflow-y: auto;
  transition: all 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
  }
  
  &::placeholder {
    color: var(--text-muted);
  }
}

/* 选择按钮容器 */
.select-buttons {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-right: 8px;
}

/* 迷你选择按钮 */
.mini-select-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 85px;
  
  &:hover {
    background: var(--bg-card);
    border-color: var(--primary-color);
    transform: translateY(-1px);
  }
  
  &.agent-btn {
    .select-icon {
      color: #10b981;
    }
    
    &:hover {
      border-color: #10b981;
    }
  }
  
  &.model-btn {
    .select-icon {
      color: #6366f1;
    }
    
    &:hover {
      border-color: #6366f1;
    }
  }
  
  .select-icon {
    width: 14px;
    height: 14px;
  }
  
  .select-name {
    font-size: 12px;
    color: var(--text-primary);
    font-weight: 500;
  }
}

.send-btn {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  border: none;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover:not(.disabled) {
    transform: scale(1.05);
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
  }
  
  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .send-icon {
    width: 18px;
    height: 18px;
    color: white;
  }
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-muted);
  
  .divider {
    color: var(--border-color);
  }
}

/* 右侧配置面板 */
.config-sidebar {
  width: 320px;
  background: rgba(17, 17, 24, 0.95);
  backdrop-filter: blur(20px);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.config-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  
  .config-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    
    .title-icon {
      width: 20px;
      height: 20px;
      color: var(--primary-color);
    }
  }
  
  .close-btn {
    width: 36px;
    height: 36px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      background: var(--bg-card);
      border-color: var(--primary-color);
    }
    
    .close-icon {
      width: 16px;
      height: 16px;
      color: var(--text-secondary);
    }
  }
}

.config-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.config-section {
  margin-bottom: 24px;
  
  h3 {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 12px;
  }
}

.param-item {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
  
  label {
    width: 80px;
    font-size: 13px;
    color: var(--text-secondary);
  }
  
  input[type="range"] {
    flex: 1;
    height: 6px;
    -webkit-appearance: none;
    background: var(--bg-tertiary);
    border-radius: 3px;
    
    &::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      background: var(--primary-color);
      border-radius: 50%;
      cursor: pointer;
    }
  }
  
  input[type="number"] {
    width: 100px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 8px 12px;
    color: var(--text-primary);
    font-size: 13px;
  }
  
  span {
    width: 40px;
    text-align: right;
    color: var(--primary-color);
    font-size: 13px;
  }
}

/* 模型选择弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  width: 100%;
  max-width: 500px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  overflow: hidden;
  animation: modalIn 0.3s ease-out;
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  
  .modal-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    
    .modal-icon {
      width: 22px;
      height: 22px;
      color: var(--primary-color);
    }
  }
  
  .modal-close {
    width: 36px;
    height: 36px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      background: var(--bg-card);
      border-color: var(--primary-color);
    }
    
    .close-icon {
      width: 16px;
      height: 16px;
      color: var(--text-secondary);
    }
  }
}

.modal-body {
  padding: 20px 24px;
  max-height: 400px;
  overflow-y: auto;
}

.model-grid,
.agent-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.agent-option {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  background: var(--bg-tertiary);
  border: 2px solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover:not(.disabled) {
    border-color: var(--border-color);
    background: var(--bg-card);
  }
  
  &.selected {
    border-color: var(--primary-color);
    background: rgba(99, 102, 241, 0.1);
  }
  
  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.agent-option-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  
  .avatar-icon {
    width: 20px;
    height: 20px;
    color: white;
  }
}

.agent-option-info {
  flex: 1;
  
  .agent-option-name {
    font-size: 15px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
  }
  
  .agent-option-status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: var(--text-muted);
    
    .status-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
    }
    
    &.active .status-dot { background: var(--success-color); box-shadow: 0 0 6px var(--success-color); }
    &.inactive .status-dot { background: var(--text-muted); }
    &.loading .status-dot { background: var(--warning-color); animation: pulse 1s infinite; }
  }
}

.agent-option-radio {
  .radio-circle {
    width: 22px;
    height: 22px;
    border: 2px solid var(--border-color);
    border-radius: 50%;
    position: relative;
    transition: all 0.2s ease;
    
    &.checked {
      border-color: var(--primary-color);
      
      &::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 10px;
        height: 10px;
        background: var(--primary-color);
        border-radius: 50%;
      }
    }
  }
}

.model-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  background: var(--bg-tertiary);
  border: 2px solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover:not(.disabled) {
    border-color: var(--border-color);
    background: var(--bg-card);
  }
  
  &.selected {
    border-color: var(--primary-color);
    background: rgba(99, 102, 241, 0.1);
  }
  
  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.model-radio {
  .radio-circle {
    width: 22px;
    height: 22px;
    border: 2px solid var(--border-color);
    border-radius: 50%;
    position: relative;
    transition: all 0.2s ease;
    
    &.checked {
      border-color: var(--primary-color);
      
      &::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 10px;
        height: 10px;
        background: var(--primary-color);
        border-radius: 50%;
      }
    }
  }
}

.model-details {
  flex: 1;
  
  .model-title {
    font-size: 15px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
  }
  
  .model-provider {
    font-size: 12px;
    color: var(--primary-color);
    margin-bottom: 4px;
  }
  
  .model-desc {
    font-size: 12px;
    color: var(--text-muted);
  }
}

.model-cost {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-color);
  
  &.premium {
    background: rgba(245, 158, 11, 0.15);
    color: var(--warning-color);
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-tertiary);
}

.btn-cancel {
  padding: 10px 24px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-primary);
    border-color: var(--border-color);
  }
}

.btn-confirm {
  padding: 10px 24px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  }
}

/* 过渡动画 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.message-enter-active {
  transition: all 0.3s ease;
}

.message-leave-active {
  transition: all 0.2s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.message-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
  
  &:hover {
    background: var(--text-muted);
  }
}
</style>