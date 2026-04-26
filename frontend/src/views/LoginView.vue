<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Logo 区域 -->
      <div class="login-header">
        <div class="logo">
          <svg viewBox="-2 -4 77 71" width="90" height="82">
            <rect x="0" y="0" width="32" height="32" rx="1.5" ry="1.5" fill="#0B1D33"/>
            <g transform="rotate(6 54.585 14.415)"><rect x="38.585" y="-1.585" width="32" height="32" rx="1.5" ry="1.5" fill="#1A6DFF"/></g>
            <rect x="0" y="35" width="32" height="32" rx="1.5" ry="1.5" fill="#0B1D33"/>
            <rect x="37" y="35" width="32" height="32" rx="1.5" ry="1.5" fill="#6B7280"/>
          </svg>
        </div>
        <h1>ZIKOI 钢管回弹云控</h1>
        <p class="subtitle">STEEL PIPE SPRINGBACK CLOUD CONTROL</p>
      </div>

      <!-- 登录类型切换 -->
      <div class="login-tabs">
        <button 
          :class="['tab-btn', { active: loginType === 'machine' }]"
          @click="loginType = 'machine'"
        >
          <span class="tab-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="4" y="4" width="16" height="16" rx="2"/>
              <path d="M9 9h6v6H9z"/>
            </svg>
          </span>
          <span>机器登录</span>
        </button>
        <button 
          :class="['tab-btn', { active: loginType === 'user' }]"
          @click="loginType = 'user'"
        >
          <span class="tab-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="8" r="4"/>
              <path d="M4 20c1.5-4 4.5-6 8-6s6.5 2 8 6"/>
            </svg>
          </span>
          <span>用户登录</span>
        </button>
      </div>

      <!-- 登录表单 -->
      <form class="login-form" @submit.prevent="handleLogin">
        <!-- 机器登录表单 -->
        <template v-if="loginType === 'machine'">
          <div class="form-group">
            <label>机器ID</label>
            <input 
              v-model="form.machineId"
              type="text"
              placeholder="请输入机器ID，如：MCH-XXX"
              required
            />
          </div>
          <div class="form-group">
            <label>访问密码</label>
            <input 
              v-model="form.password"
              type="password"
              placeholder="请输入机器密码（可选）"
            />
          </div>
          <div class="form-hint">
            <span class="hint-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 8v4"/>
                <path d="M12 16h.01"/>
              </svg>
            </span>
            <span>机器登录后直接进入该机器的操作界面</span>
          </div>
        </template>

        <!-- 用户登录表单 -->
        <template v-else>
          <div class="form-group">
            <label>用户名</label>
            <input 
              v-model="form.username"
              type="text"
              placeholder="请输入用户名"
              required
            />
          </div>
          <div class="form-group">
            <label>密码</label>
            <input 
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              required
            />
          </div>
          <div class="role-hints">
            <div class="role-hint">
              <span class="role-tag admin">管理员</span>
              <span>管理所有机器和用户</span>
            </div>
            <div class="role-hint">
              <span class="role-tag maintenance">维修</span>
              <span>查看机器状态和历史记录</span>
            </div>
            <div class="role-hint">
              <span class="role-tag operator">操作员</span>
              <span>操作指定机器</span>
            </div>
          </div>
        </template>

        <!-- 错误提示 -->
        <div v-if="error" class="error-message">
          <span class="error-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 8v5"/>
              <path d="M12 16h.01"/>
            </svg>
          </span>
          {{ error }}
        </div>

        <!-- 登录按钮 -->
        <button 
          type="submit" 
          class="login-btn"
          :disabled="loading"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else>{{ loginType === 'machine' ? '进入机器' : '登录' }}</span>
        </button>
      </form>

      <!-- 演示账号 -->
      <div class="demo-accounts">
        <p class="demo-title">演示账号</p>
        <div class="demo-list">
          <div class="demo-item" @click="fillDemo('machine')">
            <span class="demo-type">机器</span>
            <span class="demo-cred">输入任意机器ID</span>
          </div>
          <div class="demo-item" @click="fillDemo('admin')">
            <span class="demo-type">管理</span>
            <span class="demo-cred">admin / admin123</span>
          </div>
          <div class="demo-item" @click="fillDemo('maintenance')">
            <span class="demo-type">维修</span>
            <span class="demo-cred">maintenance / maint123</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginType = ref<'machine' | 'user'>('machine')
const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  password: '',
  machineId: '',
})

async function handleLogin() {
  loading.value = true
  error.value = ''
  
  try {
    const request = loginType.value === 'machine' 
      ? {
          username: form.machineId,
          password: form.password,
          login_type: 'machine' as const,
        }
      : {
          username: form.username,
          password: form.password,
          login_type: 'user' as const,
        }
    
    const success = await authStore.doLogin(request)
    
    if (success) {
      if (loginType.value === 'machine') {
        // 机器登录直接进入主界面
        router.push('/')
      } else {
        // 用户登录进入机器选择界面
        router.push('/machines')
      }
    } else {
      error.value = authStore.error || '登录失败'
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登录失败'
  } finally {
    loading.value = false
  }
}

function fillDemo(type: string) {
  if (type === 'machine') {
    loginType.value = 'machine'
    form.machineId = 'MCH-'
    form.password = ''
  } else if (type === 'admin') {
    loginType.value = 'user'
    form.username = 'admin'
    form.password = 'admin123'
  } else if (type === 'maintenance') {
    loginType.value = 'user'
    form.username = 'maintenance'
    form.password = 'maint123'
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: 
    linear-gradient(135deg, rgba(0,212,255,0.05) 0%, transparent 50%),
    linear-gradient(225deg, rgba(245,166,35,0.05) 0%, transparent 50%),
    var(--industrial-bg);
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 420px;
  background: var(--industrial-bg-card);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 40px;
  box-shadow:
    0 24px 56px rgba(15, 23, 42, 0.18),
    inset 0 1px 0 rgba(255,255,255,0.7);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, 
    var(--industrial-yellow) 0%, 
    var(--industrial-blue) 50%, 
    var(--industrial-yellow) 100%
  );
}

/* Header */
.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, var(--metal-dark) 0%, var(--metal-mid) 100%);
  border: 1px solid var(--border-bright);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--industrial-yellow);
  box-shadow: 
    inset 0 1px 0 rgba(255,255,255,0.1),
    0 4px 12px rgba(0,0,0,0.3);
}

.logo svg {
  width: 32px;
  height: 32px;
}

.login-header h1 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 11px;
  color: var(--text-muted);
  font-family: var(--font-display);
  letter-spacing: 1px;
}

/* Tabs */
.login-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  padding: 4px;
  background: var(--industrial-bg);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.16), rgba(14, 165, 233, 0.08));
  border-color: var(--industrial-blue);
  color: #0B1D33;
  box-shadow: 0 8px 22px rgba(14, 165, 233, 0.2);
}

.tab-icon {
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tab-icon svg {
  width: 16px;
  height: 16px;
}

/* Form */
.login-form {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  background: var(--industrial-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-primary);
  font-family: var(--font-display);
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--industrial-yellow);
  box-shadow: 0 0 0 3px rgba(245, 166, 35, 0.1);
}

.form-group input::placeholder {
  color: var(--text-muted);
}

.form-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid rgba(26, 109, 255, 0.2);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.hint-icon {
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.hint-icon svg {
  width: 16px;
  height: 16px;
}

.role-hints {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.role-hint {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.role-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.role-tag.admin {
  background: rgba(245, 166, 35, 0.1);
  border: 1px solid var(--industrial-yellow);
  color: var(--industrial-yellow);
}

.role-tag.maintenance {
  background: rgba(26, 109, 255, 0.1);
  border: 1px solid var(--industrial-blue);
  color: var(--industrial-blue);
}

.role-tag.operator {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid var(--industrial-green);
  color: var(--industrial-green);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--industrial-red);
  border-radius: 6px;
  color: var(--industrial-red);
  font-size: 13px;
  margin-bottom: 16px;
}

.error-icon {
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.error-icon svg {
  width: 16px;
  height: 16px;
}

.login-btn {
  width: 100%;
  padding: 14px 24px;
  background: linear-gradient(135deg, var(--industrial-yellow) 0%, var(--industrial-blue) 100%);
  border: 1px solid var(--industrial-yellow);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.28s ease;
  position: relative;
  overflow: hidden;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-btn:hover:not(:disabled) {
  box-shadow: 0 16px 28px rgba(14, 165, 233, 0.35);
  transform: translateY(-2px);
}

.login-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.32) 48%, transparent 100%);
  transform: translateX(-130%);
  transition: transform 0.45s ease;
}

.login-btn:hover::before {
  transform: translateX(130%);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--border-color);
  border-top-color: var(--text-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Demo Accounts */
.demo-accounts {
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.demo-title {
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 12px;
}

.demo-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.demo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: var(--industrial-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.demo-item:hover {
  border-color: var(--border-bright);
  background: var(--metal-dark);
}

.demo-type {
  font-size: 11px;
  font-weight: 600;
  color: var(--industrial-yellow);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.demo-cred {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-display);
}

/* Responsive */
@media (max-width: 480px) {
  .login-container {
    padding: 24px;
  }
  
  .login-header h1 {
    font-size: 18px;
  }
  
  .tab-btn {
    padding: 10px;
    font-size: 13px;
  }
}
</style>
