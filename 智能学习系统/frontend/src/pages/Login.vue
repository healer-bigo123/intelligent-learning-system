<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1 class="logo">SmartLearning</h1>
        <p class="subtitle">个性化学习平台</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            required
          />
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>

        <div v-if="error" class="error-message">{{ error }}</div>
      </form>

      <div class="test-accounts">
        <p class="test-title">测试账号：</p>
        <div class="account-item">
          <span>学生：</span>
          <code>student1 / 123456</code>
        </div>
        <div class="account-item">
          <span>老师：</span>
          <code>teacher1 / 123456</code>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/client'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await api.post('/auth/login', {
      username: username.value,
      password: password.value
    })

    const { access_token, user } = response.data

    // 保存token和用户信息
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(user))

    // 跳转到首页
    router.push('/')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;

  .logo {
    font-size: 32px;
    font-weight: 700;
    color: #667eea;
    margin: 0 0 8px 0;
  }

  .subtitle {
    font-size: 14px;
    color: #64748b;
    margin: 0;
  }
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    font-size: 14px;
    font-weight: 500;
    color: #334155;
  }

  input {
    padding: 12px 16px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    transition: all 0.2s;

    &:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
  }
}

.login-btn {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.error-message {
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
  text-align: center;
}

.test-accounts {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;

  .test-title {
    font-size: 13px;
    font-weight: 500;
    color: #64748b;
    margin: 0 0 12px 0;
  }

  .account-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #475569;

    span {
      font-weight: 500;
    }

    code {
      padding: 4px 8px;
      background: #f1f5f9;
      border-radius: 4px;
      font-family: 'Courier New', monospace;
      font-size: 12px;
      color: #667eea;
    }
  }
}
</style>
