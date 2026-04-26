<template>
  <div class="machine-select-page">
    <PageHeader
      title="选择机器"
      subtitle="MACHINE SELECTION"
      :icon="pageIcon"
    />

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
        
        <!-- 管理操作（仅管理员） -->
        <div v-if="authStore.isAdmin" class="machine-admin-actions" @click.stop>
          <button class="admin-btn edit" @click.stop="openEdit(machine)" title="编辑">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
          <button class="admin-btn delete" @click.stop="handleDelete(machine)" title="删除">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          </button>
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

    <!-- 编辑机器弹窗 -->
    <div v-if="showEditDialog" class="modal-overlay" @click.self="showEditDialog = false">
      <div class="modal-content">
        <h3>编辑机器</h3>
        <form @submit.prevent="handleEdit">
          <div class="form-group">
            <label>机器名称</label>
            <input v-model="editForm.name" type="text" required />
          </div>
          <div class="form-group">
            <label>机器位置</label>
            <input v-model="editForm.location" type="text" required />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showEditDialog = false">取消</button>
            <button type="submit" class="btn-confirm" :disabled="editing">
              {{ editing ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import { getMachines, createMachine, updateMachine, deleteMachine } from '../api'
import type { Machine, MachineStatus } from '../types'
import { formatTime } from '../utils'
import PageHeader from '../components/PageHeader.vue'

const pageIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/></svg>`

const router = useRouter()
const authStore = useAuthStore()
const toast = useToastStore()

const machines = ref<Machine[]>([])
const loading = ref(false)
const error = ref('')
const showAddDialog = ref(false)
const adding = ref(false)
const showEditDialog = ref(false)
const editing = ref(false)
const editTarget = ref<Machine | null>(null)
const editForm = ref({ name: '', location: '' })

const newMachine = ref({
  name: '',
  location: '',
})

function statusLabel(status: MachineStatus): string {
  const labels: Record<MachineStatus, string> = {
    online: '在线',
    offline: '离线',
    maintenance: '维护中',
  }
  return labels[status]
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
    toast.show(authStore.error || '选择机器失败', 'error')
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
      toast.show(res.message, 'error')
    }
  } catch (err) {
    toast.show(err instanceof Error ? err.message : '添加机器失败', 'error')
  } finally {
    adding.value = false
  }
}

function openEdit(machine: Machine) {
  editTarget.value = machine
  editForm.value = { name: machine.name, location: machine.location }
  showEditDialog.value = true
}

async function handleEdit() {
  if (!editTarget.value) return
  editing.value = true
  try {
    const res = await updateMachine(editTarget.value.id, editForm.value)
    if (res.code === 0) {
      showEditDialog.value = false
      const idx = machines.value.findIndex(m => m.id === editTarget.value!.id)
      if (idx >= 0) machines.value[idx] = res.data
    } else {
      toast.show('修改失败: ' + res.message, 'error')
    }
  } catch (err) {
    toast.show('修改失败', 'error')
  } finally {
    editing.value = false
  }
}

async function handleDelete(machine: Machine) {
  if (!confirm(`确定要删除机器 "${machine.name}" (${machine.id}) 吗？`)) return
  try {
    const res = await deleteMachine(machine.id)
    if (res.code === 0) {
      machines.value = machines.value.filter(m => m.id !== machine.id)
    } else {
      toast.show('删除失败: ' + res.message, 'error')
    }
  } catch (err) {
    toast.show('删除失败', 'error')
  }
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

.machine-admin-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s ease;
  z-index: 10;
}

.machine-card:hover .machine-admin-actions {
  opacity: 1;
}

.admin-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: rgba(255,255,255,0.9);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.admin-btn svg {
  width: 14px;
  height: 14px;
}

.admin-btn.edit {
  color: var(--industrial-blue);
}

.admin-btn.edit:hover {
  background: var(--industrial-blue);
  color: white;
}

.admin-btn.delete {
  color: #ef4444;
}

.admin-btn.delete:hover {
  background: #ef4444;
  color: white;
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
  box-shadow: 0 20px 60px rgba(11, 29, 51, 0.12);
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
  background: linear-gradient(135deg, var(--industrial-blue) 0%, #1A6DFF 100%);
  border: 1px solid var(--industrial-blue);
  color: #fff;
  font-weight: 600;
  position: relative;
  overflow: hidden;
}

.btn-confirm:hover:not(:disabled) {
  box-shadow: 0 14px 28px rgba(26, 109, 255, 0.3);
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
}
</style>
