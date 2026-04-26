<template>
  <div class="operation-log">
    <PageHeader 
      title="操作日志"
      subtitle="OPERATION LOGS"
      :icon="pageIcon"
    />

    <div class="toolbar">
      <div class="filter-group">
        <input v-model="filterUsername" placeholder="筛选用户" class="filter-input" />
        <select v-model="filterAction" class="filter-select">
          <option value="">全部操作</option>
          <option value="login">登录</option>
          <option value="machine_login">机器登录</option>
          <option value="logout">登出</option>
          <option value="create_user">创建用户</option>
          <option value="delete_user">删除用户</option>
          <option value="update_password">修改密码</option>
          <option value="create_machine">创建机器</option>
          <option value="update_machine">修改机器</option>
          <option value="delete_machine">删除机器</option>
          <option value="submit_task">提交任务</option>
        </select>
        <button class="btn-secondary" @click="applyFilter">筛选</button>
        <button class="btn-text" @click="resetFilter">重置</button>
      </div>
      <button class="btn-secondary" @click="fetchLogs">
        <span class="btn-icon">↻</span>
        刷新
      </button>
    </div>

    <div class="card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="logs.length === 0" class="empty">暂无日志记录</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>用户</th>
            <th>角色</th>
            <th>操作</th>
            <th>对象</th>
            <th>详情</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td class="time-cell">{{ formatTime(log.timestamp) }}</td>
            <td>{{ log.username }}</td>
            <td>
              <span class="role-badge" :class="log.role">{{ roleLabels[log.role] || log.role }}</span>
            </td>
            <td>
              <span class="action-badge" :class="log.action">{{ actionLabels[log.action] || log.action }}</span>
            </td>
            <td>
              <span v-if="log.target_type" class="target-tag">{{ log.target_type }}:{{ log.target_id }}</span>
              <span v-else>-</span>
            </td>
            <td class="detail-cell">{{ log.detail || '-' }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="total > limit" class="pagination">
        <button :disabled="offset === 0" @click="prevPage">上一页</button>
        <span>第 {{ offset / limit + 1 }} 页，共 {{ Math.ceil(total / limit) }} 页</span>
        <button :disabled="offset + limit >= total" @click="nextPage">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getOperationLogs } from '../api'
import { useToastStore } from '../stores/toast'
import { formatTime } from '../utils'
import PageHeader from '../components/PageHeader.vue'

const pageIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`

const logs = ref<any[]>([])
const loading = ref(false)
const toast = useToastStore()
const total = ref(0)
const limit = ref(50)
const offset = ref(0)
const filterUsername = ref('')
const filterAction = ref('')

const roleLabels: Record<string, string> = {
  admin: '管理员',
  maintenance: '维修人员',
  operator: '操作员',
  machine: '机器',
}

const actionLabels: Record<string, string> = {
  login: '登录',
  machine_login: '机器登录',
  logout: '登出',
  create_user: '创建用户',
  delete_user: '删除用户',
  update_password: '修改密码',
  create_machine: '创建机器',
  update_machine: '修改机器',
  delete_machine: '删除机器',
  submit_task: '提交任务',
}

async function fetchLogs() {
  loading.value = true
  try {
    const res = await getOperationLogs(
      limit.value,
      offset.value,
      filterUsername.value || undefined,
      filterAction.value || undefined,
    )
    if (res.code === 0) {
      logs.value = res.data.logs
      total.value = res.data.total
    } else {
      toast.show('获取日志失败: ' + res.message, 'error')
    }
  } catch (err) {
    toast.show('获取日志失败', 'error')
  } finally {
    loading.value = false
  }
}

function applyFilter() {
  offset.value = 0
  fetchLogs()
}

function resetFilter() {
  filterUsername.value = ''
  filterAction.value = ''
  offset.value = 0
  fetchLogs()
}

function prevPage() {
  offset.value = Math.max(0, offset.value - limit.value)
  fetchLogs()
}

function nextPage() {
  offset.value += limit.value
  fetchLogs()
}

onMounted(fetchLogs)
</script>

<style scoped>
.operation-log {
  max-width: 1400px;
  margin: 0 auto;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filter-input,
.filter-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--industrial-bg);
  color: var(--text-primary);
  font-size: 13px;
}

.filter-input {
  width: 140px;
}

.filter-select {
  width: 130px;
}

/* Uses global .card from App.vue */

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th,
.data-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.time-cell {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}

.detail-cell {
  color: var(--text-secondary);
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.role-badge.admin {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.role-badge.maintenance {
  background: rgba(245, 166, 35, 0.1);
  color: #f5a623;
}

.role-badge.operator {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.role-badge.machine {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.action-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  background: var(--metal-dark);
  color: var(--text-secondary);
}

.target-tag {
  font-size: 11px;
  color: var(--text-muted);
  font-family: var(--font-display);
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.pagination button {
  padding: 6px 14px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--industrial-bg-card);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 13px;
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-secondary,
.btn-text {
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  border: none;
}

.btn-secondary {
  background: var(--metal-dark);
  color: var(--text-primary);
}

.btn-text {
  background: none;
  color: var(--text-muted);
}

.btn-text:hover {
  color: var(--text-primary);
}
</style>
