<template>
  <div class="app">
    <!-- 登录页面不显示导航 -->
    <template v-if="!isLoginPage">
      <!-- 顶部导航 -->
      <header class="header">
        <div class="header-content">
          <div class="logo">
            <div class="logo-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
            </div>
            <div class="logo-text">
              <span class="title">钢管回弹智能补偿系统</span>
              <span class="subtitle">{{ currentMachineName }}</span>
            </div>
          </div>
          
          <nav class="nav">
            <router-link 
              v-for="item in menuItems" 
              :key="item.key"
              :to="item.path"
              :class="['nav-link', { active: $route.name === item.key }]"
            >
              <span class="nav-icon" v-html="item.icon"></span>
              <span class="nav-label">{{ item.label }}</span>
            </router-link>
          </nav>

          <!-- 用户信息 -->
          <div class="user-section">
            <span v-if="userRole" class="role-badge" :class="userRole">
              {{ roleLabel }}
            </span>
            <span class="user-name">{{ displayName }}</span>
            
            <!-- 切换机器按钮（用户登录模式） -->
            <button 
              v-if="!isMachineLogin && isLoggedIn" 
              class="switch-btn"
              @click="switchMachine"
              title="切换机器"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
            </button>
            
            <button class="logout-btn" @click="handleLogout">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
            </button>
          </div>
        </div>
      </header>

      <!-- 主内容区 -->
      <main class="main">
        <router-view />
      </main>

      <!-- 底部 -->
      <footer class="footer">
        <div class="footer-content">
          <div class="footer-left">
            <span class="status-dot online"></span>
            <span>SYSTEM ONLINE</span>
          </div>
          <div class="footer-center">
            钢管回弹智能补偿系统 v2.0 | 多机管理版本
          </div>
          <div class="footer-right">
            <span>{{ authMode }}</span>
            <span class="warning-icon">⚠</span>
          </div>
        </div>
      </footer>
    </template>
    
    <!-- 登录页面 -->
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isLoginPage = computed(() => route.name === 'login')
const isLoggedIn = computed(() => authStore.isLoggedIn)
const isMachineLogin = computed(() => authStore.isMachineLogin)
const userRole = computed(() => authStore.userRole)
const displayName = computed(() => authStore.displayName)

const currentMachineName = computed(() => {
  if (authStore.currentMachine) {
    return authStore.currentMachine.name
  }
  return 'INDUSTRIAL CONTROL SYSTEM'
})

const roleLabel = computed(() => {
  const labels: Record<string, string> = {
    admin: '管理员',
    maintenance: '维修',
    operator: '操作员',
    machine: '机器',
  }
  return labels[userRole.value || ''] || userRole.value
})

const authMode = computed(() => {
  if (isMachineLogin.value) {
    return 'MACHINE MODE'
  }
  return 'USER MODE'
})

const menuItems = [
  { 
    key: 'dashboard', 
    label: '参数推荐', 
    path: '/', 
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>' 
  },
  { 
    key: 'device', 
    label: '设备状态', 
    path: '/device', 
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>' 
  },
  { 
    key: 'history', 
    label: '历史记录', 
    path: '/history', 
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' 
  },
]

function switchMachine() {
  router.push('/machines')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
/* ===== 工业风设计系统 ===== */
:root {
  /* 主色调 */
  --industrial-bg: #0d1117;
  --industrial-bg-secondary: #161b22;
  --industrial-bg-card: #1c2128;
  
  /* 金属色系 */
  --metal-dark: #2d333b;
  --metal-mid: #3d444d;
  --metal-light: #4a5568;
  --metal-bright: #6b7280;
  
  /* 工业警示色 */
  --industrial-yellow: #f5a623;
  --industrial-yellow-glow: rgba(245, 166, 35, 0.4);
  --industrial-orange: #ff6b35;
  --industrial-red: #ef4444;
  --industrial-green: #22c55e;
  --industrial-green-glow: rgba(34, 197, 94, 0.4);
  --industrial-blue: #00d4ff;
  --industrial-blue-glow: rgba(0, 212, 255, 0.4);
  
  /* 文字颜色 */
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;
  
  /* 边框 */
  --border-color: #30363d;
  --border-bright: #484f58;
  
  /* 字体 */
  --font-display: 'Roboto Mono', 'Consolas', 'Monaco', monospace;
  --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-body);
  background: var(--industrial-bg);
  color: var(--text-primary);
  min-height: 100vh;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: 
    linear-gradient(135deg, rgba(0,212,255,0.03) 0%, transparent 50%),
    linear-gradient(225deg, rgba(245,166,35,0.03) 0%, transparent 50%),
    var(--industrial-bg);
}

/* ===== 头部导航 ===== */
.header {
  background: var(--industrial-bg-secondary);
  border-bottom: 1px solid var(--border-color);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.5);
}

.header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    var(--industrial-yellow) 20%, 
    var(--industrial-blue) 50%, 
    var(--industrial-yellow) 80%, 
    transparent 100%
  );
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--metal-dark) 0%, var(--metal-mid) 100%);
  border: 1px solid var(--border-bright);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--industrial-yellow);
  box-shadow: 
    inset 0 1px 0 rgba(255,255,255,0.1),
    0 2px 8px rgba(0,0,0,0.3);
}

.logo-icon svg {
  width: 24px;
  height: 24px;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 10px;
  color: var(--text-muted);
  font-family: var(--font-display);
  letter-spacing: 1px;
}

/* ===== 导航链接 ===== */
.nav {
  display: flex;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 4px;
  text-decoration: none;
  color: var(--text-secondary);
  transition: all 0.3s ease;
  border: 1px solid transparent;
  background: transparent;
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--metal-dark);
  border-color: var(--border-color);
}

.nav-link.active {
  color: var(--industrial-yellow);
  background: linear-gradient(135deg, rgba(245,166,35,0.1) 0%, rgba(245,166,35,0.05) 100%);
  border-color: var(--industrial-yellow);
  box-shadow: 
    inset 0 1px 0 rgba(245,166,35,0.1),
    0 0 20px rgba(245,166,35,0.1);
}

.nav-icon {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon svg {
  width: 100%;
  height: 100%;
}

.nav-label {
  font-size: 14px;
  font-weight: 500;
}

/* ===== 用户信息区域 ===== */
.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.role-badge.admin {
  background: rgba(245, 166, 35, 0.1);
  border: 1px solid var(--industrial-yellow);
  color: var(--industrial-yellow);
}

.role-badge.maintenance {
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid var(--industrial-blue);
  color: var(--industrial-blue);
}

.role-badge.operator {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid var(--industrial-green);
  color: var(--industrial-green);
}

.role-badge.machine {
  background: rgba(139, 148, 158, 0.1);
  border: 1px solid var(--text-secondary);
  color: var(--text-secondary);
}

.user-name {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.switch-btn,
.logout-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--metal-dark);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
}

.switch-btn:hover {
  border-color: var(--industrial-blue);
  color: var(--industrial-blue);
}

.logout-btn:hover {
  border-color: var(--industrial-red);
  color: var(--industrial-red);
}

.switch-btn svg,
.logout-btn svg {
  width: 16px;
  height: 16px;
}

/* ===== 主内容 ===== */
.main {
  flex: 1;
  margin-top: 64px;
  padding: 24px;
}

/* ===== 底部 ===== */
.footer {
  background: var(--industrial-bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: 12px 24px;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: var(--font-display);
  font-size: 11px;
  letter-spacing: 0.5px;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--industrial-green);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--industrial-green);
  box-shadow: 0 0 10px var(--industrial-green-glow);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.footer-center {
  color: var(--text-muted);
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--industrial-yellow);
}

.warning-icon {
  color: var(--industrial-yellow);
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* ===== 通用组件样式 ===== */
.card {
  background: var(--industrial-bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 20px;
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255,255,255,0.03);
  position: relative;
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    var(--industrial-blue) 50%, 
    transparent 100%
  );
  opacity: 0.5;
}

.card h3 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card h3::before {
  content: '';
  width: 4px;
  height: 16px;
  background: var(--industrial-yellow);
  border-radius: 2px;
}

/* 表单样式 */
.form-item {
  margin-bottom: 16px;
}

.form-item label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-item input,
.form-item select {
  width: 100%;
  padding: 10px 12px;
  background: var(--industrial-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-primary);
  font-family: var(--font-display);
  transition: all 0.3s ease;
}

.form-item input:focus,
.form-item select:focus {
  outline: none;
  border-color: var(--industrial-blue);
  box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.1);
}

.form-item input::placeholder {
  color: var(--text-muted);
}

/* 按钮样式 */
button {
  padding: 10px 20px;
  background: var(--metal-dark);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

button:hover:not(:disabled) {
  background: var(--metal-mid);
  border-color: var(--border-bright);
}

button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, var(--industrial-yellow) 0%, #e09400 100%);
  border-color: var(--industrial-yellow);
  color: #000;
  font-weight: 600;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #ffb84d 0%, var(--industrial-yellow) 100%);
  box-shadow: 0 0 20px var(--industrial-yellow-glow);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.1);
  border-color: var(--industrial-red);
  color: var(--industrial-red);
}

.btn-danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
}

/* 标签 */
.tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border: 1px solid;
}

.tag.success {
  background: rgba(34, 197, 94, 0.1);
  border-color: var(--industrial-green);
  color: var(--industrial-green);
}

.tag.warning {
  background: rgba(245, 166, 35, 0.1);
  border-color: var(--industrial-yellow);
  color: var(--industrial-yellow);
}

.tag.error {
  background: rgba(239, 68, 68, 0.1);
  border-color: var(--industrial-red);
  color: var(--industrial-red);
}

.tag.default {
  background: var(--metal-dark);
  border-color: var(--border-color);
  color: var(--text-secondary);
}

/* 数字显示 */
.digital-display {
  font-family: var(--font-display);
  font-variant-numeric: tabular-nums;
}

/* 响应式 */
@media (max-width: 1024px) {
  .header-content {
    flex-wrap: wrap;
    height: auto;
    padding: 12px 16px;
    gap: 12px;
  }
  
  .nav {
    order: 3;
    width: 100%;
    justify-content: center;
  }
  
  .main {
    margin-top: 120px;
  }
}

@media (max-width: 768px) {
  .user-section .user-name {
    display: none;
  }
  
  .nav-link {
    padding: 8px 12px;
  }
  
  .nav-label {
    display: none;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
}
</style>
