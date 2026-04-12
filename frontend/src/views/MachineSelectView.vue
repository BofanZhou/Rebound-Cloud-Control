<template>
  <div class="machine-select-page">
    <div class="page-header">
      <h1>选择机器</h1>
      <p class="subtitle">请选择要管理的机器设备</p>
      
      <!-- 用户信息 -->
      <div class="user-info">
        <span class="role-badge" :class="userRole">{{ roleLabel }}</span>
        <span class="user-name">{{ authStore.user?.name }}</span>
        <button class="logout-btn" @click="handleLogout">退出</button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <span>加载机器列表...</span>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-state">
      <span class="error-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 8v5"/>
          <path d="M12 16h.01"/>
        </svg>
      </span>
      <span>{{ error }}</span>
      <button @click="fetchMachines">重试</button>
    </div>

    <!-- 机器列表 -->
    <div v-else class="machines-grid">
      <div 
        v-for="machine in machines" 
        :key="machine.id"
        :class="['machine-card', machine.status]"
        @click="selectMachine(machine)"
      >
        <!-- 状态指示器 -->
        <div class="status-indicator">
          <span class="status-dot"></span>
          <span class="status-text">{{ statusLabel(machine.status) }}</span>
        </div>
        
        <!-- 机器信息 -->
        <div class="machine-info">
          <h3 class="machine-name">{{ machine.name }}</h3>
          <p class="machine-id">{{ machine.id }}</p>
          <p class="machine-location">
            <span class="location-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 21s7-5.2 7-11a7 7 0 1 0-14 0c0 5.8 7 11 7 11z"/>
                <circle cx="12" cy="10" r="2.5"/>
              </svg>
            </span>
            {{ machine.location }}
          </p>
        </div>
        
        <!-- 最后活跃时间 -->
        <div class="machine-meta">
          <span class="last-active">
            最后活跃: {{ formatTime(machine.last_active) }}
          </span>
        </div>
        
        <!-- 操作提示 -->
        <div class="machine-action">
          <span>点击进入管理</span>
          <span class="action-arrow" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14"/>
              <path d="M13 6l6 6-6 6"/>
            </svg>
          </span>
        </div>
      </div>

      <!-- 添加机器卡片（仅管理员） -->
      <div 
        v-if="authStore.isAdmin" 
        class="machine-card add-machine"
        @click="showAddDialog = true"
      >
        <div class="add-icon">+</div>
        <span class="add-text">添加新机器</span>
      </div>
    </div>

    <!-- 添加机器弹窗 -->
    <div v-if="showAddDialog" class="modal-overlay" @click.self="showAddDialog = false">
      <div class="modal-content">
        <h3>添加新机器</h3>
        <form @submit.prevent="handleAddMachine">
          <div class="form-group">
            <label>机器名称</label>
            <input 
              v-model="newMachine.name"
              type="text"
              placeholder="如：弯管机 001"
              required
            />
          </div>
          <div class="form-group">
            <label>机器位置</label>
            <input 
              v-model="newMachine.location"
              type="text"
              placeholder="如：车间A-001"
              required
            />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showAddDialog = false">
              取消
            </button>
            <button type="submit" class="btn-confirm" :disabled="adding">
              {{ adding ? '添加中...' : '添加' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getMachines, createMachine } from '../api'
import type { Machine, MachineStatus } from '../types'

const router = useRouter()
const authStore = useAuthStore()

const machines = ref<Machine[]>([])
const loading = ref(false)
const error = ref('')
const showAddDialog = ref(false)
const adding = ref(false)

const newMachine = ref({
  name: '',
  location: '',
})

const userRole = computed(() => authStore.userRole || '')

const roleLabel = computed(() => {
  const labels: Record<string, string> = {
    admin: '管理员',
    maintenance: '维修人员',
    operator: '操作员',
  }
  return labels[userRole.value] || userRole.value
})

function statusLabel(status: MachineStatus): string {
  const labels: Record<MachineStatus, string> = {
    online: '在线',
    offline: '离线',
    maintenance: '维护中',
  }
  return labels[status]
}

function formatTime(time: string): string {
  try {
    const date = new Date(time)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return time
  }
}

async function fetchMachines() {
  loading.value = true
  error.value = ''
  
  try {
    const res = await getMachines()
    if (res.code === 0) {
      machines.value = res.data
    } else {
      error.value = res.message
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '获取机器列表失败'
  } finally {
    loading.value = false
  }
}

async function selectMachine(machine: Machine) {
  if (machine.status === 'offline') {
    if (!confirm('该机器当前离线，是否仍要进入？')) {
      return
    }
  }
  
  const success = await authStore.selectCurrentMachine(machine)
  if (success) {
    router.push('/')
  } else {
    alert(authStore.error || '选择机器失败')
  }
}

async function handleAddMachine() {
  adding.value = true
  
  try {
    const res = await createMachine(newMachine.value)
    if (res.code === 0) {
      machines.value.push(res.data)
      showAddDialog.value = false
      newMachine.value = { name: '', location: '' }
    } else {
      alert(res.message)
    }
  } catch (err) {
    alert(err instanceof Error ? err.message : '添加机器失败')
  } finally {
    adding.value = false
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  fetchMachines()
})
</script>

<style scoped>
.machine-select-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.page-header .subtitle {
  color: var(--text-secondary);
  font-size: 14px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 8px;
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 11px;
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

.user-name {
  color: var(--text-primary);
  font-weight: 500;
}

.logout-btn {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: auto;
}

.logout-btn:hover {
  border-color: var(--industrial-red);
  color: var(--industrial-red);
  box-shadow: 0 10px 20px rgba(220, 38, 38, 0.14);
}

/* Loading & Error States */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 24px;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--industrial-yellow);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state .error-icon {
  width: 48px;
  height: 48px;
  color: var(--industrial-red);
}

.error-state .error-icon svg {
  width: 100%;
  height: 100%;
}

.error-state button {
  padding: 8px 24px;
  background: var(--metal-dark);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.error-state button:hover {
  border-color: var(--industrial-yellow);
  color: var(--industrial-yellow);
}

/* Machines Grid */
.machines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.machine-card {
  background: var(--industrial-bg-card);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.28s ease;
  position: relative;
  overflow: hidden;
}

.machine-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  transition: all 0.3s ease;
}

.machine-card.online::before {
  background: var(--industrial-green);
}

.machine-card.offline::before {
  background: var(--industrial-red);
}

.machine-card.maintenance::before {
  background: var(--industrial-yellow);
}

.machine-card:hover {
  border-color: var(--border-bright);
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.14);
  transform: translateY(-4px);
}

.machine-card.online:hover {
  box-shadow: 0 8px 24px rgba(34, 197, 94, 0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.machine-card.online .status-dot {
  background: var(--industrial-green);
  box-shadow: 0 0 10px var(--industrial-green-glow);
}

.machine-card.offline .status-dot {
  background: var(--industrial-red);
}

.machine-card.maintenance .status-dot {
  background: var(--industrial-yellow);
  box-shadow: 0 0 10px var(--industrial-yellow-glow);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
}

.machine-card.online .status-text {
  color: var(--industrial-green);
}

.machine-card.offline .status-text {
  color: var(--industrial-red);
}

.machine-card.maintenance .status-text {
  color: var(--industrial-yellow);
}

.machine-info {
  margin-bottom: 16px;
}

.machine-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.machine-id {
  font-size: 12px;
  color: var(--text-muted);
  font-family: var(--font-display);
  margin-bottom: 8px;
}

.machine-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.location-icon {
  width: 14px;
  height: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.location-icon svg {
  width: 14px;
  height: 14px;
}

.machine-meta {
  margin-bottom: 16px;
}

.last-active {
  font-size: 11px;
  color: var(--text-muted);
  font-family: var(--font-display);
}

.machine-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.machine-card:hover .machine-action {
  color: var(--industrial-yellow);
}

.action-arrow {
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.action-arrow svg {
  width: 16px;
  height: 16px;
}

.machine-card:hover .action-arrow {
  transform: translateX(4px);
}

/* Add Machine Card */
.machine-card.add-machine {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  border-style: dashed;
  background: transparent;
}

.machine-card.add-machine::before {
  display: none;
}

.machine-card.add-machine:hover {
  border-color: var(--industrial-yellow);
  background: rgba(245, 166, 35, 0.05);
}

.add-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--metal-dark);
  border: 2px solid var(--border-color);
  font-size: 24px;
  color: var(--industrial-yellow);
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.machine-card.add-machine:hover .add-icon {
  border-color: var(--industrial-yellow);
  background: rgba(245, 166, 35, 0.1);
}

.add-text {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.modal-content {
  background: var(--industrial-bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 24px;
  text-align: center;
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
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--industrial-yellow);
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.modal-actions button {
  flex: 1;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: var(--metal-dark);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-cancel:hover {
  border-color: var(--border-bright);
  color: var(--text-primary);
  box-shadow: 0 10px 18px rgba(15, 23, 42, 0.08);
}

.btn-confirm {
  background: linear-gradient(135deg, var(--industrial-blue) 0%, #0284c7 100%);
  border: 1px solid var(--industrial-blue);
  color: #fff;
  font-weight: 600;
  position: relative;
  overflow: hidden;
}

.btn-confirm:hover:not(:disabled) {
  box-shadow: 0 14px 28px rgba(14, 165, 233, 0.3);
  transform: translateY(-1px);
}

.btn-confirm::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.34) 50%, transparent 100%);
  transform: translateX(-125%);
  transition: transform 0.45s ease;
}

.btn-confirm:hover::before {
  transform: translateX(125%);
}

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .machines-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
