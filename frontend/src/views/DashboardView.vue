<template>
  <div class="dashboard">
    <PageHeader
      title="参数推荐"
      subtitle="PARAMETER RECOMMENDATION"
      :icon="pageIcon"
    />
    
    <div class="container">
      <!-- 左侧：参数输入 -->
      <div class="card input-card">
        <h3>参数输入</h3>
        <form @submit.prevent="handleRecommend">
          <div class="form-row">
            <div class="form-item">
              <label>
                <span class="label-icon">D</span>
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
                <span class="label-icon">T</span>
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
                <span class="label-icon">M</span>
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
                <span class="label-icon">A</span>
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
              <span class="btn-icon">R</span>
              重置
            </button>
            <button type="submit" class="btn-primary" :disabled="recommendLoading">
              <span class="btn-icon">OK</span>
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
              <span class="box-icon">i</span>
              补偿说明
            </div>
            <p>{{ recommendResult.explanation }}</p>
          </div>
          
          <div class="params-panel">
            <div class="panel-header">
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
            {{ submitLoading ? '提交中...' : '提交任务到设备' }}
          </button>
          
          <div v-if="!canSubmit && recommendResult" class="warning-hint">
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
import { useToastStore } from '../stores/toast'
import PageHeader from '../components/PageHeader.vue'

const pageIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>`

const deviceStore = useDeviceStore()
const authStore = useAuthStore()
const toast = useToastStore()

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
      toast.show('获取推荐参数成功！', 'success')
    } else {
      toast.show('获取推荐失败: ' + res.message, 'error')
    }
  } catch (err) {
    toast.show('获取推荐参数失败: ' + (err instanceof Error ? err.message : '未知错误'), 'error')
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
      toast.show(`任务提交成功: ${res.data.task_id}`, 'success')
      recommendResult.value = null
    } else {
      toast.show('提交任务失败: ' + res.message, 'error')
    }
  } catch (err) {
    toast.show('提交任务失败: ' + (err instanceof Error ? err.message : '未知错误'), 'error')
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

.container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
}

.input-card::after {
  content: none;
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
  width: 21px;
  height: 21px;
  background: rgba(0, 113, 227, 0.10);
  border-radius: 50%;
  margin-right: 7px;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-primary);
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
  font-variant-numeric: tabular-nums;
  font-size: 15px;
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
  background: rgba(118, 118, 128, 0.10);
}

.btn-icon {
  font-size: 10px;
  font-weight: 800;
}

.result-card::after {
  content: none;
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
  font-size: 12px;
  color: var(--text-muted);
}

/* 结果内容 */
.result-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-highlight {
  background: linear-gradient(180deg, rgba(0, 113, 227, 0.10), rgba(0, 113, 227, 0.05));
  border: 1px solid rgba(0, 113, 227, 0.12);
  border-radius: 20px;
  padding: 28px 24px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.result-highlight::before {
  content: none;
}

.highlight-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 600;
}

.highlight-value {
  font-size: 54px;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1.05;
}

.compensation-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 12px;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.compensation-badge.positive {
  background: rgba(22, 163, 74, 0.10);
  color: var(--color-success);
}

.compensation-badge.negative {
  background: rgba(245, 158, 11, 0.10);
  color: var(--color-warning);
}

/* 说明框 */
.explanation-box {
  background: rgba(118, 118, 128, 0.08);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 16px;
}

.box-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.box-icon {
  width: 16px;
  height: 16px;
  background: rgba(0, 113, 227, 0.10);
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
  background: rgba(118, 118, 128, 0.08);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 16px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
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
  background: rgba(255, 255, 255, 0.72);
  border-radius: 12px;
}

.item-label {
  font-size: 11px;
  color: var(--text-muted);
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
  background: rgba(245, 158, 11, 0.06);
  border: 1px solid rgba(183, 110, 0, 0.16);
  border-radius: 14px;
  font-size: 12px;
  color: var(--color-warning);
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

@media (max-width: 640px) {
  .dashboard {
    max-width: 100%;
  }

  .container {
    gap: 14px;
  }

  .form-row {
    gap: 12px;
  }

  .form-actions {
    flex-direction: column-reverse;
    gap: 10px;
    margin-top: 18px;
    padding-top: 16px;
  }

  .form-actions button,
  .btn-submit {
    width: 100%;
  }

  .result-highlight {
    padding: 22px 16px;
  }

  .highlight-value {
    font-size: 42px;
  }

  .panel-item {
    padding: 12px;
  }
}

/* Deep polish */
.dashboard .card {
  border-radius: 22px;
}

.label-icon,
.box-icon,
.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.form-actions button,
.btn-submit {
  border-radius: 999px;
  position: relative;
  overflow: hidden;
}

.form-actions button::before,
.btn-submit::before {
  content: none;
}

.form-actions button:hover::before,
.btn-submit:hover::before {
  transform: none;
}

.result-highlight {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.72);
}
</style>
