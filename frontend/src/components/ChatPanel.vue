<template>
  <div class="chat-panel">
    <div class="chat-header" v-if="agent">
      <div class="agent-avatar" :style="{ background: agent.color }">
        <component :is="getIcon(agent.icon)" class="icon" />
      </div>
      <div class="agent-info">
        <h2 class="agent-name">{{ agent.name }}</h2>
        <div class="agent-status-bar">
          <span class="status-indicator" :class="agent.status"></span>
          <span class="status-text">{{ getStatusText(agent.status) }}</span>
          <span class="model-indicator">{{ getModelName(agent.selectedModel) }}</span>
        </div>
      </div>
      <div class="header-actions">
        <el-button size="small" @click="handleClear">
          <component :is="icons.Trash2" class="btn-icon" />
          清空
        </el-button>
      </div>
    </div>
    
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="empty-state">
        <component :is="icons.MessageCircle" class="empty-icon" />
        <p class="empty-text">开始与 {{ agent?.name || '智能体' }} 对话</p>
        <p class="empty-hint">输入您的问题，智能体将为您提供帮助</p>
      </div>
      
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-item"
        :class="message.role"
      >
        <div class="message-avatar">
          <component 
            :is="message.role === 'user' ? icons.User : getIcon(agent?.icon || 'HelpCircle')" 
            class="avatar-icon" 
          />
        </div>
        <div class="message-content">
          <div class="message-bubble">
            <p class="message-text">{{ message.content }}</p>
          </div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <div v-if="loading" class="typing-indicator">
        <div class="typing-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
        <span class="typing-text">{{ agent?.name }} 正在思考...</span>
      </div>
    </div>
    
    <div class="chat-input-area">
      <div class="input-actions">
        <el-button 
          size="small" 
          type="text" 
          @click="handleQuickQuestion('help')"
          class="quick-btn"
        >
          <component :is="icons.Lightbulb" class="action-icon" />
          快速提问
        </el-button>
        <el-button 
          size="small" 
          type="text" 
          @click="showModelSelector = !showModelSelector"
          class="quick-btn"
        >
          <component :is="icons.Settings" class="action-icon" />
          切换模型
        </el-button>
      </div>
      
      <div class="input-wrapper">
        <textarea
          v-model="inputMessage"
          class="message-input"
          placeholder="输入您的问题..."
          rows="3"
          @keydown.ctrl.enter="handleSend"
          @keydown.meta.enter="handleSend"
        ></textarea>
        <el-button 
          type="primary" 
          class="send-btn"
          :disabled="!inputMessage.trim() || loading"
          @click="handleSend"
        >
          <component :is="icons.Send" class="send-icon" />
          发送
        </el-button>
      </div>
      
      <div class="input-hint">
        <span class="hint-text">Ctrl + Enter 发送</span>
        <span class="divider">|</span>
        <span class="hint-text">{{ agent?.description }}</span>
      </div>
    </div>
    
    <div class="model-quick-select" v-if="showModelSelector">
      <div class="quick-select-header">
        <span class="title">选择模型</span>
        <el-button size="small" @click="showModelSelector = false">关闭</el-button>
      </div>
      <div class="model-list">
        <div
          v-for="model in availableModels"
          :key="model.id"
          class="model-option"
          :class="{ selected: localSelectedModel === model.id }"
          @click="handleModelChange(model.id)"
        >
          <div class="model-radio">
            <input
              type="radio"
              :value="model.id"
              :checked="localSelectedModel === model.id"
              @change="handleModelChange(model.id)"
              class="radio-input"
            />
          </div>
          <div class="model-info">
            <span class="model-name">{{ model.name }}</span>
            <span class="model-provider">{{ model.provider }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed, watch, type Component } from 'vue'
import { 
  MessageCircle, Send, User, Trash2, Settings, Lightbulb,
  HelpCircle, Calendar, CheckSquare, Heart, Star, BarChart 
} from 'lucide-vue-next'
import type { AgentInfo, ModelInfo, ChatMessage } from '@/types'

const props = defineProps<{
  agent: AgentInfo | null
  messages: ChatMessage[]
  models: ModelInfo[]
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'send', content: string): void
  (e: 'clear'): void
  (e: 'modelChange', modelId: string): void
}>()

const icons = { MessageCircle, Send, User, Trash2, Settings, Lightbulb }

const iconMap: Record<string, Component> = {
  HelpCircle,
  Calendar,
  CheckSquare,
  Heart,
  Star,
  BarChart
}

const inputMessage = ref('')
const showModelSelector = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const localSelectedModel = ref(props.agent?.selectedModel || '')

watch(() => props.agent?.selectedModel, (newVal) => {
  if (newVal) {
    localSelectedModel.value = newVal
  }
})

const availableModels = computed(() => {
  return props.models.filter(m => m.available)
})

const getIcon = (iconName: string): Component => {
  return iconMap[iconName] || HelpCircle
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    active: '在线',
    inactive: '离线',
    loading: '加载中'
  }
  return statusMap[status] || status
}

const getModelName = (modelId: string): string => {
  const model = props.models.find(m => m.id === modelId)
  return model?.name || modelId
}

const formatTime = (timestamp: Date): string => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const handleSend = () => {
  const content = inputMessage.value.trim()
  if (content && !props.loading) {
    emit('send', content)
    inputMessage.value = ''
    scrollToBottom()
  }
}

const handleClear = () => {
  emit('clear')
}

const handleModelChange = (modelId: string) => {
  localSelectedModel.value = modelId
  emit('modelChange', modelId)
}

const handleQuickQuestion = (type: string) => {
  const questions: Record<string, string> = {
    help: '请问你能帮我做什么？'
  }
  inputMessage.value = questions[type]
}
</script>

<style lang="scss" scoped>
@import '@/style/index.scss';

.chat-panel {
  background: $bg-card;
  border-radius: $radius-lg;
  border: 1px solid $border-color;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  border-bottom: 1px solid $border-color;
  background: $bg-tertiary;
}

.agent-avatar {
  width: 50px;
  height: 50px;
  border-radius: $radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  .icon {
    width: 24px;
    height: 24px;
    color: white;
  }
}

.agent-info {
  flex: 1;
  
  .agent-name {
    font-size: 18px;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 6px;
  }
}

.agent-status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: $success-color;
  
  &.inactive {
    background: $text-muted;
  }
  
  &.loading {
    background: $warning-color;
    animation: pulse 1s infinite;
  }
}

.status-text {
  font-size: 12px;
  color: $text-secondary;
}

.model-indicator {
  background: $bg-card;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  color: $primary-color;
}

.header-actions {
  .btn-icon {
    width: 14px;
    height: 14px;
    margin-right: 4px;
  }
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  
  .empty-icon {
    width: 64px;
    height: 64px;
    color: $text-muted;
    margin-bottom: 16px;
  }
  
  .empty-text {
    font-size: 16px;
    color: $text-primary;
    margin-bottom: 8px;
  }
  
  .empty-hint {
    font-size: 13px;
    color: $text-muted;
  }
}

.message-item {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  
  &.user {
    flex-direction: row-reverse;
    
    .message-bubble {
      background: linear-gradient(135deg, $primary-color 0%, $primary-dark 100%);
      border-radius: $radius-md $radius-md 0 $radius-md;
    }
    
    .message-content {
      align-items: flex-end;
    }
  }
  
  &.assistant {
    .message-bubble {
      background: $bg-tertiary;
      border-radius: $radius-md $radius-md $radius-md 0;
      border: 1px solid $border-color;
    }
  }
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: $bg-tertiary;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  .avatar-icon {
    width: 18px;
    height: 18px;
    color: $text-secondary;
  }
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message-bubble {
  padding: 12px 16px;
  
  .message-text {
    font-size: 14px;
    line-height: 1.6;
    color: $text-primary;
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
  }
}

.message-time {
  font-size: 11px;
  color: $text-muted;
  margin-top: 4px;
  padding: 0 4px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: $bg-tertiary;
  border-radius: $radius-md;
  width: fit-content;
  
  .typing-dots {
    display: flex;
    gap: 4px;
    
    .dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: $primary-color;
      animation: typing 1.4s infinite ease-in-out;
      
      &:nth-child(1) { animation-delay: 0s; }
      &:nth-child(2) { animation-delay: 0.2s; }
      &:nth-child(3) { animation-delay: 0.4s; }
    }
  }
  
  .typing-text {
    font-size: 13px;
    color: $text-secondary;
  }
}

.chat-input-area {
  padding: 16px 20px;
  border-top: 1px solid $border-color;
  background: $bg-tertiary;
}

.input-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  
  .quick-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    color: $text-secondary;
    
    .action-icon {
      width: 14px;
      height: 14px;
    }
  }
}

.input-wrapper {
  display: flex;
  gap: 12px;
  
  .message-input {
    flex: 1;
    background: $bg-card;
    border: 1px solid $border-color;
    border-radius: $radius-md;
    padding: 12px 16px;
    font-size: 14px;
    color: $text-primary;
    resize: none;
    transition: all $transition-fast;
    
    &:focus {
      outline: none;
      border-color: $primary-color;
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }
    
    &::placeholder {
      color: $text-muted;
    }
  }
  
  .send-btn {
    align-self: flex-end;
    padding: 10px 24px;
    border-radius: $radius-md;
    
    .send-icon {
      width: 16px;
      height: 16px;
      margin-right: 6px;
    }
  }
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  
  .hint-text {
    font-size: 12px;
    color: $text-muted;
  }
  
  .divider {
    color: $border-color;
  }
}

.model-quick-select {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background: $bg-card;
  border: 1px solid $border-color;
  border-bottom: none;
  border-radius: $radius-lg $radius-lg 0 0;
  padding: 16px 20px;
  margin-bottom: -1px;
}

.quick-select-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  .title {
    font-size: 14px;
    font-weight: 600;
    color: $text-primary;
  }
}

.model-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.model-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: $bg-tertiary;
  border-radius: $radius-md;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all $transition-fast;
  
  &:hover {
    border-color: $border-color;
  }
  
  &.selected {
    border-color: $primary-color;
    background: rgba(99, 102, 241, 0.1);
  }
  
  .radio-input {
    width: 16px;
    height: 16px;
  }
  
  .model-info {
    display: flex;
    flex-direction: column;
    
    .model-name {
      font-size: 13px;
      color: $text-primary;
    }
    
    .model-provider {
      font-size: 11px;
      color: $text-muted;
    }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}
</style>