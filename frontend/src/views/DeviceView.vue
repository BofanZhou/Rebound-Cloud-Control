<template>
  <div class="device">
    <PageHeader
      title="设备状态"
      subtitle="DEVICE MONITORING"
      :icon="pageIcon"
    />
    
    <div class="container">
      <!-- 设备状态卡片 -->
      <div class="card status-card">
        <h3>设备状态</h3>
        <div class="status-display">
          <div class="status-indicator" :class="statusClass">
            <div class="indicator-ring">
              <div class="indicator-core">
                <span v-if="deviceStore.isOnline" class="status-icon online">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                </span>
                <span v-else class="status-icon offline">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                  </svg>
                </span>
              </div>
            </div>
            <div class="status-label" :class="statusClass">
              {{ deviceStore.statusDisplay.label }}
            </div>
            <div class="connection-status" :class="deviceStore.isOnline ? 'online' : 'offline'">
              <span class="connection-dot"></span>
              {{ deviceStore.isOnline ? '设备在线' : '设备离线' }}
            </div>
          </div>
        </div>
        
        <div class="info-panel">
          <div class="info-row">
            <span class="info-label">设备ID</span>
            <span class="info-value digital-display">{{ deviceStore.deviceState?.device_id || '---' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">最后心跳</span>
            <span class="info-value">{{ formatTime(deviceStore.deviceState?.last_heartbeat) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">当前任务</span>
            <span class="info-value digital-display">{{ deviceStore.deviceState?.current_task || '无' }}</span>
          </div>
        </div>
      </div>

      <!-- 角度信息 -->
      <div class="card angle-card">
        <h3>角度监测</h3>
        <div class="angle-grid">
          <div class="angle-box">
            <div class="angle-header">
              <span class="angle-icon">🎯</span>
              <span class="angle-title">设定角度</span>
            </div>
            <div class="angle-value digital-display">
              {{ deviceStore.deviceState?.current_angle?.toFixed(2) || '0.00' }}°
            </div>
            <div class="angle-bar">
              <div class="bar-fill" :style="{ width: getAnglePercent(deviceStore.deviceState?.current_angle) + '%' }"></div>
            </div>
          </div>
          
          <div class="angle-box">
            <div class="angle-header">
              <span class="angle-icon">📐</span>
              <span class="angle-title">实际角度</span>
            </div>
            <div class="angle-value digital-display" :class="actualAngleClass">
              {{ deviceStore.deviceState?.actual_angle?.toFixed(2) || '0.00' }}°
            </div>
            <div class="angle-bar">
              <div class="bar-fill actual" :style="{ width: getAnglePercent(deviceStore.deviceState?.actual_angle) + '%' }"></div>
            </div>
          </div>
          
          <div class="angle-box deviation-box">
            <div class="angle-header">
              <span class="angle-icon">⚡</span>
              <span class="angle-title">偏差值</span>
            </div>
            <div class="angle-value digital-display" :class="deviationClass">
              {{ formatDeviation(deviceStore.deviceState?.deviation) }}°
            </div>
            <div class="deviation-indicator">
              <div class="indicator-scale">
                <div class="scale-marker" :style="{ left: getDeviationPercent(deviceStore.deviceState?.deviation) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 控制面板 -->
      <div class="card control-card">
        <h3>控制面板</h3>
        <div class="control-grid">
          <button 
            class="control-btn start"
            :disabled="!canStart"
            @click="handleSimulateStart"
          >
            <span class="btn-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </span>
            <span class="btn-text">
              <span class="text-main">开始任务</span>
              <span class="text-sub">START TASK</span>
            </span>
          </button>
          
          <button 
            class="control-btn complete"
            :disabled="!canComplete"
            @click="handleSimulateComplete"
          >
            <span class="btn-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
              </svg>
            </span>
            <span class="btn-text">
              <span class="text-main">完成任务</span>
              <span class="text-sub">COMPLETE</span>
            </span>
          </button>
          
          <button 
            class="control-btn reset"
            :disabled="!canReset"
            @click="handleReset"
          >
            <span class="btn-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
              </svg>
            </span>
            <span class="btn-text">
              <span class="text-main">重置设备</span>
              <span class="text-sub">RESET</span>
            </span>
          </button>
        </div>
        
        <div class="auto-refresh">
          <label class="toggle-label">
            <input type="checkbox" v-model="autoRefresh" @change="handleAutoRefreshChange" />
            <span class="toggle-slider"></span>
            <span class="toggle-text">
              <span class="toggle-main">自动刷新</span>
              <span class="toggle-sub">AUTO REFRESH</span>
            </span>
          </label>
        </div>
      </div>
    </div>

    <!-- 状态流程图 -->
    <div class="card flow-card">
      <h3>状态流程</h3>
      <div class="status-flow">
        <div 
          v-for="(step, index) in statusSteps" 
          :key="step.key"
          class="flow-step"
          :class="{
            active: currentStepIndex === index,
            completed: currentStepIndex > index,
          }"
        >
          <div class="step-connector" v-if="index > 0">
            <div class="connector-line"></div>
          </div>
          <div class="step-node">
            <div class="node-ring">
              <div class="node-core">
                <span v-html="step.icon"></span>
              </div>
            </div>
            <div class="step-info">
              <span class="step-number">STEP {{ index + 1 }}</span>
              <span class="step-label">{{ step.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDeviceStore } from '../stores/device'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import { formatTime, formatDeviation } from '../utils'
import PageHeader from '../components/PageHeader.vue'

const pageIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>`

// DeviceStatus type is used in the template via store

const deviceStore = useDeviceStore()
const authStore = useAuthStore()
const toast = useToastStore()

// 获取当前机器ID
const currentMachineId = computed(() => authStore.currentMachine?.id)

// 状态类名
const statusClass = computed(() => ({
  online: deviceStore.isOnline,
  offline: !deviceStore.isOnline,
  running: deviceStore.currentStatus === 'running',
  error: deviceStore.currentStatus === 'error',
  completed: deviceStore.currentStatus === 'completed',
}))

const actualAngleClass = computed(() => ({
  'has-value': deviceStore.deviceState?.actual_angle && deviceStore.deviceState.actual_angle > 0,
}))

const deviationClass = computed(() => {
  const deviation = deviceStore.deviceState?.deviation || 0
  if (Math.abs(deviation) <= 0.5) return 'good'
  if (Math.abs(deviation) <= 1.0) return 'warning'
  return 'error'
})

// 控制按钮状态
const canStart = computed(() => 
  deviceStore.isOnline && 
  (deviceStore.currentStatus === 'idle' || deviceStore.currentStatus === 'completed')
)

const canComplete = computed(() => 
  deviceStore.currentStatus === 'running'
)

const canReset = computed(() => 
  deviceStore.currentStatus !== 'offline'
)

function handleSimulateStart() {
  toast.show('模拟：任务开始执行', 'info')
}

function handleSimulateComplete() {
  toast.show('模拟：任务完成', 'success')
}

function handleReset() {
  toast.show('模拟：设备重置', 'info')
}

// 自动刷新
const autoRefresh = ref(true)

function handleAutoRefreshChange() {
  if (autoRefresh.value) {
    deviceStore.startMonitoring(currentMachineId.value)
  } else {
    deviceStore.stopMonitoring()
  }
}

// 状态流程
const statusSteps = [
  { 
    key: 'idle', 
    label: '空闲待机', 
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="12" height="16" rx="2"/><line x1="12" y1="8" x2="12" y2="8.01"/><line x1="12" y1="16" x2="12" y2="16.01"/></svg>` 
  },
  { 
    key: 'running', 
    label: '运行加工', 
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>` 
  },
  { 
    key: 'completed', 
    label: '加工完成', 
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>` 
  },
]

const currentStepIndex = computed(() => {
  const status = deviceStore.currentStatus
  const index = statusSteps.findIndex(s => s.key === status)
  return index >= 0 ? index : 0
})

// 工具函数
function getAnglePercent(angle: number | undefined): number {
  if (angle === undefined) return 0
  return Math.min(Math.max(angle / 180 * 100, 0), 100)
}

function getDeviationPercent(deviation: number | undefined): number {
  if (deviation === undefined) return 50
  // Map -5 to +5 degrees to 0-100%
  return Math.min(Math.max((deviation + 5) / 10 * 100, 0), 100)
}

// 生命周期
onMounted(() => {
  if (autoRefresh.value) {
    deviceStore.startMonitoring(currentMachineId.value)
  }
})

onUnmounted(() => {
  deviceStore.stopMonitoring()
})
</script>

<style scoped>
.device {
  max-width: 1400px;
  margin: 0 auto;
}

.container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

/* 状态卡片 */
.status-card::after {
  content: 'STATUS';
  position: absolute;
  top: 20px;
  right: 20px;
  font-family: var(--font-display);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 2px;
  opacity: 0.5;
}

.status-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.status-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.indicator-ring {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, var(--metal-dark), var(--metal-mid), var(--metal-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.indicator-core {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  background: var(--industrial-bg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-icon svg {
  width: 100%;
  height: 100%;
}

.status-icon.online {
  color: var(--industrial-green);
  filter: drop-shadow(0 0 10px var(--industrial-green-glow));
}

.status-icon.offline {
  color: var(--industrial-red);
  opacity: 0.6;
}

.status-label {
  font-size: 14px;
  font-weight: 600;
  padding: 8px 20px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status-label.online, .status-label.idle {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid var(--industrial-green);
  color: var(--industrial-green);
}

.status-label.running {
  background: rgba(26, 109, 255, 0.1);
  border: 1px solid var(--industrial-blue);
  color: var(--industrial-blue);
  animation: pulse-glow 1.5s infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 10px rgba(26, 109, 255, 0.2); }
  50% { box-shadow: 0 0 20px rgba(26, 109, 255, 0.4); }
}

.status-label.completed {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid var(--industrial-green);
  color: var(--industrial-green);
}

.status-label.error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--industrial-red);
  color: var(--industrial-red);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-family: var(--font-display);
}

.connection-status.online {
  color: var(--industrial-green);
}

.connection-status.offline {
  color: var(--text-muted);
}

.connection-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.connection-status.online .connection-dot {
  box-shadow: 0 0 10px currentColor;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* 信息面板 */
.info-panel {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

/* 角度卡片 */
.angle-card::after {
  content: 'MONITOR';
  position: absolute;
  top: 20px;
  right: 20px;
  font-family: var(--font-display);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 2px;
  opacity: 0.5;
}

.angle-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.angle-box {
  background: var(--industrial-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 16px;
  position: relative;
  overflow: hidden;
}

.angle-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: var(--industrial-blue);
}

.angle-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.angle-title {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.angle-value {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.angle-value.has-value {
  color: var(--industrial-blue);
  text-shadow: 0 0 20px var(--industrial-blue-glow);
}

.angle-value.good {
  color: var(--industrial-green);
  text-shadow: 0 0 20px var(--industrial-green-glow);
}

.angle-value.warning {
  color: var(--industrial-yellow);
}

.angle-value.error {
  color: var(--industrial-red);
}

.angle-bar {
  height: 4px;
  background: var(--metal-dark);
  border-radius: 2px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
  border-radius: 2px;
  transition: width 0.5s ease;
}

.bar-fill.actual {
  background: linear-gradient(90deg, var(--color-success), var(--color-success-light));
}

.deviation-box::before {
  background: var(--industrial-yellow);
}

.deviation-indicator {
  padding: 8px 0;
}

.indicator-scale {
  height: 6px;
  background: linear-gradient(90deg, 
    var(--color-danger) 0%,
    var(--color-warning) 25%,
    var(--color-success) 50%,
    var(--color-warning) 75%,
    var(--color-danger) 100%
  );
  border-radius: 3px;
  position: relative;
}

.scale-marker {
  position: absolute;
  top: -3px;
  width: 12px;
  height: 12px;
  background: #fff;
  border-radius: 50%;
  transform: translateX(-50%);
  box-shadow: 0 0 10px rgba(255,255,255,0.5);
}

/* 控制卡片 */
.control-card::after {
  content: 'CONTROL';
  position: absolute;
  top: 20px;
  right: 20px;
  font-family: var(--font-display);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 2px;
  opacity: 0.5;
}

.control-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.control-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--industrial-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  text-align: left;
  transition: all 0.3s ease;
}

.control-btn:hover:not(:disabled) {
  background: var(--metal-dark);
  border-color: var(--border-bright);
}

.control-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.control-btn.start:hover:not(:disabled) {
  border-color: var(--industrial-green);
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.1);
}

.control-btn.complete:hover:not(:disabled) {
  border-color: var(--industrial-blue);
  box-shadow: 0 0 20px rgba(26, 109, 255, 0.1);
}

.control-btn.reset:hover:not(:disabled) {
  border-color: var(--industrial-red);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.1);
}

.btn-icon {
  width: 36px;
  height: 36px;
  background: var(--metal-dark);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-icon svg {
  width: 20px;
  height: 20px;
}

.btn-text {
  display: flex;
  flex-direction: column;
}

.text-main {
  font-size: 14px;
  font-weight: 500;
}

.text-sub {
  font-size: 10px;
  color: var(--text-muted);
  font-family: var(--font-display);
  letter-spacing: 0.5px;
}

/* 自动刷新开关 */
.auto-refresh {
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.toggle-label input {
  display: none;
}

.toggle-slider {
  width: 48px;
  height: 24px;
  background: var(--metal-dark);
  border-radius: 12px;
  position: relative;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.toggle-slider::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  background: var(--text-muted);
  border-radius: 50%;
  transition: all 0.3s ease;
}

.toggle-label input:checked + .toggle-slider {
  background: rgba(34, 197, 94, 0.2);
  border-color: var(--industrial-green);
}

.toggle-label input:checked + .toggle-slider::after {
  left: 26px;
  background: var(--industrial-green);
  box-shadow: 0 0 10px var(--industrial-green-glow);
}

.toggle-text {
  display: flex;
  flex-direction: column;
}

.toggle-main {
  font-size: 13px;
  font-weight: 500;
}

.toggle-sub {
  font-size: 10px;
  color: var(--text-muted);
  font-family: var(--font-display);
  letter-spacing: 0.5px;
}

/* 流程卡片 */
.flow-card::after {
  content: 'WORKFLOW';
  position: absolute;
  top: 20px;
  right: 20px;
  font-family: var(--font-display);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 2px;
  opacity: 0.5;
}

.status-flow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 60px;
  padding: 30px;
}

.flow-step {
  display: flex;
  align-items: center;
  position: relative;
}

.step-connector {
  position: absolute;
  left: -50px;
  width: 40px;
  height: 2px;
}

.connector-line {
  width: 100%;
  height: 100%;
  background: var(--metal-dark);
}

.flow-step.completed .connector-line {
  background: var(--industrial-green);
}

.step-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.node-ring {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--metal-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.flow-step.active .node-ring {
  background: var(--industrial-blue);
  box-shadow: 0 0 30px var(--industrial-blue-glow);
  animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
  0%, 100% { box-shadow: 0 0 20px var(--industrial-blue-glow); }
  50% { box-shadow: 0 0 40px var(--industrial-blue-glow); }
}

.flow-step.completed .node-ring {
  background: var(--industrial-green);
}

.node-core {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--industrial-bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.node-core svg {
  width: 24px;
  height: 24px;
}

.flow-step.active .node-core {
  color: var(--industrial-blue);
}

.flow-step.completed .node-core {
  color: var(--industrial-green);
}

.step-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.step-number {
  font-size: 10px;
  color: var(--text-muted);
  font-family: var(--font-display);
  letter-spacing: 1px;
}

.step-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.flow-step.active .step-label {
  color: var(--industrial-blue);
}

.flow-step.completed .step-label {
  color: var(--industrial-green);
}

@media (max-width: 1024px) {
  .container {
    grid-template-columns: 1fr 1fr;
  }
  
  .status-flow {
    flex-direction: column;
    gap: 30px;
  }
  
  .step-connector {
    display: none;
  }
}

@media (max-width: 768px) {
  .container {
    grid-template-columns: 1fr;
  }
}

/* Deep polish */
.device .card {
  border-radius: 18px;
}

.control-btn {
  border-radius: 14px;
  position: relative;
  overflow: hidden;
}

.control-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(112deg, transparent 0%, rgba(255,255,255,0.24) 50%, transparent 100%);
  transform: translateX(-125%);
  transition: transform 0.45s ease;
}

.control-btn:hover:not(:disabled)::before {
  transform: translateX(125%);
}

.btn-icon svg,
.title-icon svg,
.node-core svg,
.status-icon svg {
  stroke-linecap: round;
  stroke-linejoin: round;
}

.indicator-ring {
  box-shadow: inset 0 0 0 2px rgba(255,255,255,0.42), 0 10px 28px rgba(11, 29, 51, 0.12);
}
</style>
