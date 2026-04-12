<template>
  <div class="dashboard">
    <div class="page-header">
      <h2 class="page-title">
        <span class="title-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </span>
        参数推荐
      </h2>
      <span class="page-subtitle">PARAMETER RECOMMENDATION</span>
    </div>
    
    <div class="container">
      <!-- 左侧：参数输入 -->
      <div class="card input-card">
        <h3>参数输入</h3>
        <form @submit.prevent="handleRecommend">
          <div class="form-row">
            <div class="form-item">
              <label>
                <span class="label-icon">⌀</span>
                管径 (mm)
              </label>
              <div class="input-with-unit">
                <input 
                  v-model.number="formData.diameter" 
                  type="number" 
                  min="10" 
                  max="500" 
                  required 
                  class="digital-input"
                />
                <span class="unit">mm</span>
              </div>
            </div>
            
            <div class="form-item">
              <label>
                <span class="label-icon">━</span>
                壁厚 (mm)
              </label>
              <div class="input-with-unit">
                <input 
                  v-model.number="formData.thickness" 
                  type="number" 
                  min="1" 
                  max="50" 
                  required 
                  class="digital-input"
                />
                <span class="unit">mm</span>
              </div>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-item">
              <label>
                <span class="label-icon">◈</span>
                材质
              </label>
              <select v-model="formData.material" required>
                <option value="普通钢">普通钢</option>
                <option value="高强钢">高强钢</option>
                <option value="不锈钢">不锈钢</option>
                <option value="铝合金">铝合金</option>
              </select>
            </div>
            
            <div class="form-item">
              <label>
                <span class="label-icon">∠</span>
                目标角度 (°)
              </label>
              <div class="input-with-unit">
                <input 
                  v-model.number="formData.target_angle" 
                  type="number" 
                  min="0" 
                  max="180" 
                  required 
                  class="digital-input"
                />
                <span class="unit">°</span>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="handleReset" class="btn-secondary">
              <span class="btn-icon">↺</span>
              重置
            </button>
            <button type="submit" class="btn-primary" :disabled="recommendLoading">
              <span class="btn-icon">⚡</span>
              {{ recommendLoading ? '计算中...' : '获取推荐参数' }}
            </button>
          </div>
        </form>
      </div>

      <!-- 右侧：推荐结果 -->
      <div class="card result-card">
        <h3>推荐结果</h3>
        <div v-if="!recommendResult" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 16v-4M12 8h.01"/>
            </svg>
          </div>
          <p>请先输入参数并获取推荐</p>
          <span class="empty-hint">WAITING FOR INPUT...</span>
        </div>
        <div v-else class="result-content">
          <div class="result-highlight">
            <div class="highlight-label">推荐角度</div>
            <div class="highlight-value digital-display">
              {{ recommendResult.recommended_angle.toFixed(2) }}°
            </div>
            <div class="compensation-badge" :class="recommendResult.recommended_offset >= 0 ? 'positive' : 'negative'">
              {{ recommendResult.recommended_offset >= 0 ? '▲' : '▼' }}
              {{ Math.abs(recommendResult.recommended_offset).toFixed(2) }}°
            </div>
          </div>
          
          <div class="explanation-box">
            <div class="box-header">
              <span class="box-icon">ℹ</span>
              补偿说明
            </div>
            <p>{{ recommendResult.explanation }}</p>
          </div>
          
          <div class="params-panel">
            <div class="panel-header">
              <span class="panel-icon">📊</span>
              输入参数确认
            </div>
            <div class="panel-grid">
              <div class="panel-item">
                <span class="item-label">管径</span>
                <span class="item-value digital-display">{{ formData.diameter }} mm</span>
              </div>
              <div class="panel-item">
                <span class="item-label">壁厚</span>
                <span class="item-value digital-display">{{ formData.thickness }} mm</span>
              </div>
              <div class="panel-item">
                <span class="item-label">材质</span>
                <span class="item-value">{{ formData.material }}</span>
              </div>
              <div class="panel-item">
                <span class="item-label">目标</span>
                <span class="item-value digital-display">{{ formData.target_angle }}°</span>
              </div>
            </div>
          </div>
          
          <button 
            class="btn-primary btn-submit" 
            :disabled="submitLoading || !canSubmit"
            @click="handleSubmit"
          >
            <span class="btn-icon">▶</span>
            {{ submitLoading ? '提交中...' : '提交任务到设备' }}
          </button>
          
          <div v-if="!canSubmit && recommendResult" class="warning-hint">
            <span class="warning-icon">⚠</span>
            设备离线或忙碌中，无法提交任务
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import type { RecommendParams, RecommendResult, TaskSubmitParams } from '../types'
import { getRecommend, submitTask } from '../api'
import { useDeviceStore } from '../stores/device'
import { useAuthStore } from '../stores/auth'

const deviceStore = useDeviceStore()
const authStore = useAuthStore()

// 表单数据
const formData = reactive<RecommendParams>({
  diameter: 50,
  thickness: 5,
  material: '普通钢',
  target_angle: 90,
})

// 推荐结果
const recommendLoading = ref(false)
const recommendResult = ref<RecommendResult | null>(null)

// 提交状态
const submitLoading = ref(false)

const canSubmit = computed(() => {
  return recommendResult.value !== null && 
         deviceStore.isOnline && 
         (deviceStore.currentStatus === 'idle' || deviceStore.currentStatus === 'completed')
})

async function handleRecommend() {
  recommendLoading.value = true
  try {
    const res = await getRecommend({ ...formData })
    if (res.code === 0) {
      recommendResult.value = res.data
      alert('获取推荐参数成功！')
    } else {
      alert('获取推荐失败: ' + res.message)
    }
  } catch (err) {
    alert('获取推荐参数失败: ' + (err instanceof Error ? err.message : '未知错误'))
  } finally {
    recommendLoading.value = false
  }
}

function handleReset() {
  formData.diameter = 50
  formData.thickness = 5
  formData.material = '普通钢'
  formData.target_angle = 90
  recommendResult.value = null
}

async function handleSubmit() {
  if (!recommendResult.value) return
  
  submitLoading.value = true
  const params: TaskSubmitParams = {
    diameter: formData.diameter,
    thickness: formData.thickness,
    material: formData.material,
    target_angle: formData.target_angle,
    recommended_angle: recommendResult.value.recommended_angle,
    recommended_offset: recommendResult.value.recommended_offset,
  }
  
  try {
    // 获取当前机器ID
    const machineId = authStore.currentMachine?.id
    const res = await submitTask(params, machineId)
    if (res.code === 0) {
      alert(`任务提交成功: ${res.data.task_id}`)
      recommendResult.value = null
    } else {
      alert('提交任务失败: ' + res.message)
    }
  } catch (err) {
    alert('提交任务失败: ' + (err instanceof Error ? err.message : '未知错误'))
  } finally {
    submitLoading.value = false
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.title-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--industrial-yellow) 0%, #e09400 100%);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #000;
}

.title-icon svg {
  width: 20px;
  height: 20px;
}

.page-subtitle {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 2px;
}

.container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

/* 输入卡片 */
.input-card::after {
  content: 'INPUT';
  position: absolute;
  top: 20px;
  right: 20px;
  font-family: var(--font-display);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 2px;
  opacity: 0.5;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.label-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: var(--metal-dark);
  border-radius: 3px;
  margin-right: 6px;
  font-size: 10px;
  color: var(--industrial-yellow);
}

.input-with-unit {
  position: relative;
  display: flex;
  align-items: center;
}

.input-with-unit input {
  padding-right: 45px;
}

.unit {
  position: absolute;
  right: 12px;
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--text-muted);
  pointer-events: none;
}

.digital-input {
  font-family: var(--font-display);
  font-variant-numeric: tabular-nums;
  font-size: 16px;
  letter-spacing: 0.5px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--metal-dark);
}

.btn-icon {
  font-size: 14px;
}

/* 结果卡片 */
.result-card::after {
  content: 'OUTPUT';
  position: absolute;
  top: 20px;
  right: 20px;
  font-family: var(--font-display);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 2px;
  opacity: 0.5;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: var(--text-muted);
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-state p {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 8px;
}

.empty-hint {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 1px;
}

/* 结果内容 */
.result-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-highlight {
  background: linear-gradient(135deg, 
    rgba(0, 212, 255, 0.1) 0%, 
    rgba(0, 212, 255, 0.05) 100%
  );
  border: 1px solid var(--industrial-blue);
  border-radius: 4px;
  padding: 24px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.result-highlight::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--industrial-blue);
  box-shadow: 0 0 20px var(--industrial-blue-glow);
}

.highlight-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.highlight-value {
  font-size: 48px;
  font-weight: 600;
  color: var(--industrial-blue);
  text-shadow: 0 0 30px var(--industrial-blue-glow);
  line-height: 1.2;
}

.compensation-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 12px;
  padding: 6px 14px;
  border-radius: 4px;
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
}

.compensation-badge.positive {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid var(--industrial-green);
  color: var(--industrial-green);
}

.compensation-badge.negative {
  background: rgba(245, 166, 35, 0.1);
  border: 1px solid var(--industrial-yellow);
  color: var(--industrial-yellow);
}

/* 说明框 */
.explanation-box {
  background: var(--industrial-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 16px;
}

.box-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--industrial-yellow);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.box-icon {
  width: 16px;
  height: 16px;
  background: rgba(245, 166, 35, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
}

.explanation-box p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* 参数面板 */
.params-panel {
  background: var(--industrial-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 16px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.panel-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.panel-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: var(--industrial-bg-secondary);
  border-radius: 3px;
}

.item-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.item-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

/* 提交按钮 */
.btn-submit {
  width: 100%;
  padding: 14px;
  font-size: 14px;
}

.warning-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: rgba(245, 166, 35, 0.05);
  border: 1px dashed var(--industrial-yellow);
  border-radius: 4px;
  font-size: 12px;
  color: var(--industrial-yellow);
}

.warning-icon {
  font-size: 14px;
}

@media (max-width: 768px) {
  .container {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .highlight-value {
    font-size: 36px;
  }
  
  .panel-grid {
    grid-template-columns: 1fr;
  }
}

/* Deep polish */
.dashboard .card {
  border-radius: 18px;
}

.label-icon,
.box-icon,
.panel-icon,
.warning-icon,
.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.form-actions button,
.btn-submit {
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}

.form-actions button::before,
.btn-submit::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
  transform: translateX(-125%);
  transition: transform 0.45s ease;
}

.form-actions button:hover::before,
.btn-submit:hover::before {
  transform: translateX(125%);
}

.result-highlight {
  box-shadow: 0 16px 30px rgba(14, 165, 233, 0.16);
}
</style>
