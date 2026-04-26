<template>
  <div class="history">
    <PageHeader
      title="历史记录"
      subtitle="OPERATION HISTORY"
      :icon="pageIcon"
    />
    
    <div class="toolbar">
      <button class="btn-refresh" @click="handleRefresh" :disabled="historyStore.loading">
        <span class="btn-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
        </span>
        <span class="btn-text">{{ historyStore.loading ? '刷新中...' : '刷新数据' }}</span>
      </button>
      <button class="btn-clear" @click="handleClear">
        <span class="btn-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </span>
        <span class="btn-text">清空记录</span>
      </button>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>任务ID</th>
            <th>管径</th>
            <th>壁厚</th>
            <th>材质</th>
            <th>目标角度</th>
            <th>推荐角度</th>
            <th>实际角度</th>
            <th>偏差</th>
            <th>状态</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="historyStore.records.length === 0">
            <td colspan="11" class="empty-cell">
              <div class="empty-content">
                <div class="empty-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <path d="M3 9h18"/>
                    <path d="M9 21V9"/>
                  </svg>
                </div>
                <p>暂无历史记录</p>
                <span class="empty-hint">NO DATA AVAILABLE</span>
              </div>
            </td>
          </tr>
          <tr v-for="(record, index) in historyStore.records" :key="record.id" :class="{ 'row-alt': index % 2 === 1 }">
            <td class="cell-id">
              <span class="id-badge">{{ record.id }}</span>
            </td>
            <td class="digital-display">{{ record.input_params.diameter }} mm</td>
            <td class="digital-display">{{ record.input_params.thickness }} mm</td>
            <td>
              <span class="material-tag">{{ record.input_params.material }}</span>
            </td>
            <td class="digital-display">{{ record.input_params.target_angle }}°</td>
            <td class="digital-display highlight">{{ record.recommend_params.recommended_angle.toFixed(2) }}°</td>
            <td class="digital-display">
              {{ record.execute_result ? record.execute_result.actual_angle.toFixed(2) + '°' : '-' }}
            </td>
            <td>
              <span v-if="record.execute_result" :class="['deviation-badge', getDeviationClass(record.execute_result.deviation)]">
                {{ formatDeviation(record.execute_result.deviation) }}°
              </span>
              <span v-else class="deviation-badge default">-</span>
            </td>
            <td>
              <span v-if="record.execute_result" :class="['status-badge', getStatusClass(record.execute_result.final_status)]">
                <span class="status-dot"></span>
                {{ getStatusLabel(record.execute_result.final_status) }}
              </span>
              <span v-else class="status-badge pending">
                <span class="status-dot"></span>
                待执行
              </span>
            </td>
            <td class="cell-time">{{ formatTime(record.created_at) }}</td>
            <td>
              <button class="btn-detail" @click="showDetail(record)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="1"/>
                  <circle cx="19" cy="12" r="1"/>
                  <circle cx="5" cy="12" r="1"/>
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
              </svg>
            </span>
            <div class="title-text">
              <span class="main">任务详情</span>
              <span class="sub">TASK DETAILS</span>
            </div>
          </div>
          <button class="close-btn" @click="closeModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body" v-if="selectedRecord">
          <!-- 基本信息 -->
          <div class="detail-section">
            <div class="section-header">
              <span class="section-icon">ID</span>
              <span class="section-title">基本信息</span>
            </div>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="item-label">任务ID</span>
                <span class="item-value digital-display">{{ selectedRecord.id }}</span>
              </div>
              <div class="detail-item">
                <span class="item-label">创建时间</span>
                <span class="item-value">{{ formatTime(selectedRecord.created_at) }}</span>
              </div>
              <div class="detail-item">
                <span class="item-label">完成时间</span>
                <span class="item-value">{{ formatTime(selectedRecord.completed_at) || '未完成' }}</span>
              </div>
            </div>
          </div>
          
          <!-- 输入参数 -->
          <div class="detail-section">
            <div class="section-header">
              <span class="section-icon">IN</span>
              <span class="section-title">输入参数</span>
            </div>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="item-label">管径</span>
                <span class="item-value digital-display">{{ selectedRecord.input_params.diameter }} mm</span>
              </div>
              <div class="detail-item">
                <span class="item-label">壁厚</span>
                <span class="item-value digital-display">{{ selectedRecord.input_params.thickness }} mm</span>
              </div>
              <div class="detail-item">
                <span class="item-label">材质</span>
                <span class="item-value">{{ selectedRecord.input_params.material }}</span>
              </div>
              <div class="detail-item">
                <span class="item-label">目标角度</span>
                <span class="item-value digital-display">{{ selectedRecord.input_params.target_angle }}°</span>
              </div>
            </div>
          </div>
          
          <!-- 推荐参数 -->
          <div class="detail-section">
            <div class="section-header">
              <span class="section-icon">AI</span>
              <span class="section-title">推荐参数</span>
            </div>
            <div class="detail-grid">
              <div class="detail-item highlight">
                <span class="item-label">推荐角度</span>
                <span class="item-value digital-display accent">{{ selectedRecord.recommend_params.recommended_angle.toFixed(2) }}°</span>
              </div>
              <div class="detail-item">
                <span class="item-label">补偿值</span>
                <span class="item-value digital-display">{{ formatDeviation(selectedRecord.recommend_params.recommended_offset) }}°</span>
              </div>
              <div class="detail-item full-width">
                <span class="item-label">说明</span>
                <span class="item-value explanation">{{ selectedRecord.recommend_params.explanation }}</span>
              </div>
            </div>
          </div>
          
          <!-- 执行结果 -->
          <div class="detail-section" v-if="selectedRecord.execute_result">
            <div class="section-header">
              <span class="section-icon">✓</span>
              <span class="section-title">执行结果</span>
            </div>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="item-label">实际角度</span>
                <span class="item-value digital-display">{{ selectedRecord.execute_result.actual_angle.toFixed(2) }}°</span>
              </div>
              <div class="detail-item">
                <span class="item-label">最终偏差</span>
                <span :class="['item-value', 'digital-display', getDeviationClass(selectedRecord.execute_result.deviation)]">
                  {{ formatDeviation(selectedRecord.execute_result.deviation) }}°
                </span>
              </div>
              <div class="detail-item">
                <span class="item-label">最终状态</span>
                <span :class="['status-badge', getStatusClass(selectedRecord.execute_result.final_status)]">
                  <span class="status-dot"></span>
                  {{ getStatusLabel(selectedRecord.execute_result.final_status) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useHistoryStore } from '../stores/history'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import type { HistoryRecord, DeviceStatus } from '../types'
import { formatTime, formatDeviation } from '../utils'
import PageHeader from '../components/PageHeader.vue'

const pageIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`

const historyStore = useHistoryStore()
const authStore = useAuthStore()
const toast = useToastStore()

// 获取当前机器ID
const currentMachineId = computed(() => authStore.currentMachine?.id)

// 弹窗状态
const showModal = ref(false)
const selectedRecord = ref<HistoryRecord | null>(null)

function showDetail(record: HistoryRecord) {
  selectedRecord.value = record
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedRecord.value = null
}

function handleRefresh() {
  historyStore.fetchHistory(20, currentMachineId.value)
  toast.show('刷新成功', 'success')
}

function handleClear() {
  if (confirm('确定要清空所有历史记录吗？')) {
    historyStore.clearRecords()
    toast.show('已清空历史记录', 'success')
  }
}

// 工具函数
function getDeviationClass(deviation: number): string {
  const abs = Math.abs(deviation)
  if (abs <= 0.5) return 'success'
  if (abs <= 1.0) return 'warning'
  return 'error'
}

function getStatusClass(status: DeviceStatus): string {
  const map: Record<DeviceStatus, string> = {
    offline: 'offline',
    idle: 'success',
    running: 'running',
    completed: 'success',
    error: 'error',
  }
  return map[status] || 'default'
}

function getStatusLabel(status: DeviceStatus): string {
  const map: Record<DeviceStatus, string> = {
    offline: '离线',
    idle: '空闲',
    running: '运行中',
    completed: '已完成',
    error: '错误',
  }
  return map[status] || '未知'
}

// 生命周期
onMounted(() => {
  historyStore.fetchHistory(20, currentMachineId.value)
})
</script>

<style scoped>
.history {
  max-width: 1400px;
  margin: 0 auto;
}

/* 工具栏 */
.toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
}

.toolbar button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: var(--industrial-bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 13px;
  transition: all 0.3s ease;
}

.toolbar button:hover:not(:disabled) {
  background: var(--metal-dark);
  border-color: var(--border-bright);
}

.toolbar button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon svg {
  width: 100%;
  height: 100%;
}

.btn-refresh:hover:not(:disabled) {
  border-color: var(--industrial-blue);
  color: var(--industrial-blue);
}

.btn-clear:hover:not(:disabled) {
  border-color: var(--industrial-red);
  color: var(--industrial-red);
}

/* 表格容器 */
.table-container {
  background: var(--industrial-bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(11, 29, 51, 0.08);
}

.table-container::before {
  content: '';
  display: block;
  height: 2px;
  background: linear-gradient(90deg, var(--industrial-yellow) 0%, var(--industrial-blue) 100%);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th,
.data-table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  background: var(--industrial-bg-secondary);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.data-table tbody tr {
  transition: background 0.2s ease;
}

.data-table tbody tr:hover {
  background: rgba(26, 109, 255, 0.03);
}

.row-alt {
  background: rgba(255, 255, 255, 0.02);
}

/* 单元格样式 */
.cell-id {
  font-family: var(--font-display);
}

.id-badge {
  display: inline-block;
  padding: 4px 10px;
  background: var(--metal-dark);
  border-radius: 3px;
  font-size: 12px;
  color: var(--text-primary);
}

.material-tag {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(26, 109, 255, 0.1);
  border: 1px solid var(--industrial-blue);
  border-radius: 3px;
  font-size: 11px;
  color: var(--industrial-blue);
}

.highlight {
  color: var(--color-primary);
  font-weight: 500;
}

.deviation-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 3px;
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 500;
}

.deviation-badge.success {
  background: rgba(22, 163, 74, 0.10);
  color: var(--color-success);
}

.deviation-badge.warning {
  background: rgba(245, 158, 11, 0.10);
  color: var(--color-warning);
}

.deviation-badge.error {
  background: rgba(220, 38, 38, 0.10);
  color: var(--color-danger);
}

.deviation-badge.default {
  background: var(--metal-dark);
  color: var(--text-muted);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-badge.success {
  background: rgba(22, 163, 74, 0.10);
  color: var(--color-success);
}

.status-badge.success .status-dot {
  background: var(--industrial-green);
  box-shadow: 0 0 6px var(--industrial-green-glow);
}

.status-badge.running {
  background: rgba(26, 109, 255, 0.1);
  color: var(--industrial-blue);
}

.status-badge.running .status-dot {
  background: var(--industrial-blue);
  box-shadow: 0 0 6px var(--industrial-blue-glow);
  animation: blink 1s infinite;
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--industrial-red);
}

.status-badge.error .status-dot {
  background: var(--industrial-red);
}

.status-badge.offline {
  background: var(--metal-dark);
  color: var(--text-muted);
}

.status-badge.pending {
  background: rgba(245, 166, 35, 0.1);
  color: var(--industrial-yellow);
}

.status-badge.pending .status-dot {
  background: var(--industrial-yellow);
  animation: blink 1.5s infinite;
}

.cell-time {
  color: var(--text-secondary);
  font-size: 12px;
}

.btn-detail {
  padding: 6px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 3px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-detail:hover {
  background: var(--metal-dark);
  border-color: var(--industrial-blue);
  color: var(--industrial-blue);
}

.btn-detail svg {
  width: 16px;
  height: 16px;
  display: block;
}

/* 空状态 */
.empty-cell {
  padding: 60px 20px;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--text-muted);
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  opacity: 0.4;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-content p {
  font-size: 14px;
  margin-bottom: 8px;
}

.empty-hint {
  font-family: var(--font-display);
  font-size: 11px;
  letter-spacing: 1px;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--industrial-bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: auto;
  box-shadow: 0 20px 60px rgba(11, 29, 51, 0.12);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--industrial-bg-secondary);
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-title .title-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, rgba(26, 109, 255, 0.08), rgba(26, 109, 255, 0.04));
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
}

.modal-title .title-icon svg {
  width: 20px;
  height: 20px;
}

.title-text {
  display: flex;
  flex-direction: column;
}

.title-text .main {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.title-text .sub {
  font-size: 10px;
  color: var(--text-muted);
  font-family: var(--font-display);
  letter-spacing: 1px;
}

.close-btn {
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  padding: 0;
}

.close-btn:hover {
  background: var(--metal-dark);
  border-color: var(--industrial-red);
  color: var(--industrial-red);
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

.modal-body {
  padding: 24px;
}

.detail-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.detail-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.section-icon {
  font-size: 16px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--industrial-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.detail-item.highlight {
  border-color: var(--industrial-yellow);
  background: rgba(245, 166, 35, 0.05);
}

.item-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.item-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.item-value.accent {
  color: var(--industrial-yellow);
  font-size: 16px;
}

.item-value.explanation {
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.item-value.success {
  color: var(--industrial-green);
}

.item-value.warning {
  color: var(--industrial-yellow);
}

.item-value.error {
  color: var(--industrial-red);
}

@media (max-width: 1024px) {
  .data-table {
    font-size: 12px;
  }
  
  .data-table th,
  .data-table td {
    padding: 10px 12px;
  }
}

@media (max-width: 768px) {
  .table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .data-table {
    min-width: 800px;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .history {
    max-width: 100%;
  }

  .toolbar {
    flex-direction: column;
    gap: 10px;
  }

  .toolbar button {
    width: 100%;
    justify-content: center;
  }

  .modal-overlay {
    align-items: flex-end;
    padding: 12px;
  }

  .modal {
    width: 100%;
    max-height: calc(100svh - 24px);
    border-radius: 22px;
  }

  .modal-header {
    padding: 16px 18px;
  }

  .modal-body {
    padding: 18px;
  }

  .detail-item {
    align-items: flex-start;
    flex-direction: column;
    gap: 6px;
  }
}

/* Deep polish */
.table-container,
.modal {
  border-radius: 16px;
}

.toolbar button,
.btn-detail,
.close-btn {
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.toolbar button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(112deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
  transform: translateX(-125%);
  transition: transform 0.45s ease;
}

.toolbar button:hover::before {
  transform: translateX(125%);
}

.status-badge .status-dot {
  box-shadow: 0 0 0 4px rgba(255,255,255,0.45);
}

.table-container::before {
  content: none;
}

.table-container,
.modal {
  border-radius: 22px;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.05);
}

.toolbar button,
.btn-detail,
.close-btn,
.detail-item,
.id-badge,
.material-tag,
.deviation-badge,
.status-badge {
  border-radius: 999px;
}

.detail-item {
  border-radius: 16px;
  background: rgba(118, 118, 128, 0.08);
}

.modal-overlay {
  background: rgba(0, 0, 0, 0.28);
  backdrop-filter: saturate(180%) blur(18px);
}

.section-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0, 113, 227, 0.10);
  color: var(--color-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 800;
}
</style>
