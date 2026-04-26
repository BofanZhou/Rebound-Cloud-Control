<template>
  <div class="training-page">
    <PageHeader title="模型训练" subtitle="MODEL TRAINING" :icon="pageIcon" />

    <div class="container">
      <!-- 左侧：训练设置 -->
      <div class="card setup-card">
        <h3>训练设置</h3>

        <div class="upload-section">
          <label class="upload-area" :class="{ 'has-file': uploadedFile }">
            <input type="file" accept=".csv" @change="handleFileSelect" class="file-input" />
            <div class="upload-content">
              <span class="upload-icon">📂</span>
              <span class="upload-text">{{ uploadedFile ? uploadedFile.name : '点击上传 CSV 数据集' }}</span>
              <span class="upload-hint">CSV 列: material, diameter, thickness, target_angle, result</span>
              <span v-if="uploadResult" class="upload-status success">已加载 {{ uploadResult.count }} 条记录</span>
              <span v-if="uploadError" class="upload-status error">{{ uploadError }}</span>
            </div>
          </label>
        </div>

        <div class="params-section">
          <div class="form-row">
            <div class="form-item">
              <label>训练轮数</label>
              <input v-model.number="trainParams.epochs" type="number" min="10" max="500" />
            </div>
            <div class="form-item">
              <label>批次大小</label>
              <input v-model.number="trainParams.batchSize" type="number" min="8" max="256" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-item">
              <label>学习率</label>
              <input v-model.number="trainParams.learningRate" type="number" step="0.0001" min="0.0001" max="0.1" />
            </div>
            <div class="form-item">
              <label>模型状态</label>
              <span class="model-badge" :class="modelStatusClass">{{ modelStatusText }}</span>
            </div>
          </div>
        </div>

        <div class="action-row">
          <button class="btn-primary" @click="handleStartTraining" :disabled="trainingState.is_training || !uploadedFile">
            {{ trainingState.is_training ? '训练中...' : '开始训练' }}
          </button>
          <button v-if="trainingState.model_exists" class="btn-secondary" @click="handleResetModel">重置模型</button>
        </div>
      </div>

      <!-- 右侧：预测测试 -->
      <div class="card predict-card">
        <h3>模型测试</h3>
        <div v-if="!trainingState.model_exists && !trainingState.is_training" class="empty-hint">
          请先完成模型训练
        </div>
        <template v-else>
          <div class="form-row">
            <div class="form-item">
              <label>材质</label>
              <select v-model="predictForm.material">
                <option value="普通钢">普通钢</option>
                <option value="高强钢">高强钢</option>
                <option value="不锈钢">不锈钢</option>
                <option value="铝合金">铝合金</option>
              </select>
            </div>
            <div class="form-item">
              <label>管径 (mm)</label>
              <input v-model.number="predictForm.diameter" type="number" min="10" max="500" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-item">
              <label>壁厚 (mm)</label>
              <input v-model.number="predictForm.thickness" type="number" min="1" max="50" />
            </div>
            <div class="form-item">
              <label>目标角度 (°)</label>
              <input v-model.number="predictForm.targetAngle" type="number" min="0" max="180" />
            </div>
          </div>

          <div class="predict-actions">
            <button class="btn-primary" @click="handlePredict" :disabled="predicting">单次预测</button>
            <button class="btn-secondary" @click="handlePredictIterative" :disabled="predicting">迭代预测</button>
          </div>

          <!-- 预测结果 -->
          <div v-if="predictResult" class="predict-result">
            <div class="result-header">预测结果: 
              <span :class="['result-class', predictResultClass]">{{ predictResult.label }}</span>
            </div>
            <div class="prob-bars">
              <div v-for="(prob, i) in predictResult.probabilities" :key="i" class="prob-row">
                <span class="prob-label">{{ ['偏小', '合适', '偏大'][i] }}</span>
                <div class="prob-bar-track">
                  <div class="prob-bar-fill" :style="{ width: (prob * 100) + '%' }" :class="['bar-' + i]"></div>
                </div>
                <span class="prob-value">{{ (prob * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>

          <!-- 迭代结果 -->
          <div v-if="iterativeResult" class="iterative-result">
            <div class="result-header" :class="{ success: iterativeResult.success, fail: !iterativeResult.success }">
              {{ iterativeResult.message }}
            </div>
            <div v-if="iterativeResult.final_angle" class="final-angle">
              最终推荐角度: <span class="highlight-value">{{ iterativeResult.final_angle }}°</span>
              <span class="offset-badge">原始: {{ iterativeResult.original_angle }}°</span>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 训练进度 -->
    <div v-if="trainingState.is_training || trainingState.final_accuracy > 0" class="card progress-card">
      <h3>训练进度</h3>

      <div class="progress-header">
        <div class="progress-stats">
          <div class="stat-item">
            <span class="stat-label">Epoch</span>
            <span class="stat-value">{{ trainingState.current_epoch }} / {{ trainingState.total_epochs }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">最终准确率</span>
            <span class="stat-value" :class="{ highlight: trainingState.final_accuracy > 0 }">
              {{ trainingState.final_accuracy > 0 ? (trainingState.final_accuracy * 100).toFixed(1) + '%' : '—' }}
            </span>
          </div>
          <div class="stat-item">
            <span class="stat-label">消息</span>
            <span class="stat-value msg">{{ trainingState.message || '—' }}</span>
          </div>
        </div>
        <div v-if="trainingState.is_training" class="progress-bar-track">
          <div class="progress-bar-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>

      <!-- 损失 & 准确率曲线 -->
      <div v-if="trainingState.train_losses.length > 0" class="charts-row">
        <div class="chart-box">
          <div class="chart-title">Training Loss</div>
          <div ref="lossChartRef" class="chart-canvas"></div>
        </div>
        <div class="chart-box">
          <div class="chart-title">Validation Accuracy</div>
          <div ref="accChartRef" class="chart-canvas"></div>
        </div>
      </div>

      <!-- 混淆矩阵 -->
      <div v-if="trainingState.confusion && trainingState.confusion[0][0] + trainingState.confusion[0][1] + trainingState.confusion[0][2] > 0" class="confusion-section">
        <div class="chart-title">Confusion Matrix</div>
        <table class="confusion-table">
          <thead>
            <tr><th></th><th>预测: 偏小</th><th>预测: 合适</th><th>预测: 偏大</th></tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in trainingState.confusion" :key="i">
              <td class="cm-label">{{ ['实际: 偏小', '实际: 合适', '实际: 偏大'][i] }}</td>
              <td v-for="(val, j) in row" :key="j" :class="['cm-cell', { 'cm-diag': i === j }]">{{ val }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { uploadDataset, getTrainingStatus, startTraining, predict, predictIterative } from '../api'
import { useToastStore } from '../stores/toast'
import PageHeader from '../components/PageHeader.vue'
import type { TrainingStatus, PredictResult, IterativeResult } from '../types'

const pageIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`

const toast = useToastStore()

const uploadedFile = ref<File | null>(null)
const uploadResult = ref<{ count: number } | null>(null)
const uploadError = ref('')
const predicting = ref(false)

const trainParams = reactive({ epochs: 80, batchSize: 32, learningRate: 0.001 })

const predictForm = reactive({ material: '普通钢', diameter: 50, thickness: 5, targetAngle: 90 })
const predictResult = ref<PredictResult | null>(null)
const iterativeResult = ref<IterativeResult | null>(null)

const trainingState = reactive<TrainingStatus>({
  is_training: false, current_epoch: 0, total_epochs: 0,
  train_losses: [], val_accuracies: [], final_accuracy: 0,
  confusion: [[0,0,0],[0,0,0],[0,0,0]], message: '', error: '',
  dataset_size: 0, model_exists: false,
})

let pollTimer: ReturnType<typeof setInterval> | null = null

const modelStatusText = computed(() => {
  if (trainingState.is_training) return '训练中'
  if (trainingState.model_exists) return `已就绪 (acc ${(trainingState.final_accuracy * 100).toFixed(0)}%)`
  return '未训练'
})
const modelStatusClass = computed(() => ({
  ready: trainingState.model_exists && !trainingState.is_training,
  training: trainingState.is_training,
  none: !trainingState.model_exists,
}))

const progressPercent = computed(() => {
  if (trainingState.total_epochs === 0) return 0
  return (trainingState.current_epoch / trainingState.total_epochs) * 100
})

const predictResultClass = computed(() => {
  if (!predictResult.value) return ''
  return { 0: 'small', 1: 'good', 2: 'large' }[predictResult.value.class] || ''
})

async function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  uploadedFile.value = file
  uploadError.value = ''
  uploadResult.value = null

  try {
    const res = await uploadDataset(file)
    if (res.code === 0) {
      uploadResult.value = res.data
      await fetchStatus()
      toast.show(`数据集加载成功 (${res.data.count} 条)`, 'success')
    } else {
      uploadError.value = res.message
    }
  } catch (err) {
    uploadError.value = err instanceof Error ? err.message : '上传失败'
  }
}

async function handleStartTraining() {
  if (!uploadedFile.value) return
  try {
    const res = await startTraining(trainParams.epochs, trainParams.batchSize, trainParams.learningRate)
    if (res.code === 0) {
      toast.show('训练已启动', 'success')
      startPolling()
    } else {
      toast.show(res.message, 'error')
    }
  } catch (err) {
    toast.show('启动训练失败', 'error')
  }
}

async function handleResetModel() {
  // 重新上传数据集即可覆盖
  uploadedFile.value = null
  uploadResult.value = null
  trainingState.model_exists = false
  trainingState.final_accuracy = 0
}

async function handlePredict() {
  predicting.value = true
  iterativeResult.value = null
  try {
    const res = await predict(predictForm.material, predictForm.diameter, predictForm.thickness, predictForm.targetAngle)
    if (res.code === 0) predictResult.value = res.data
  } catch (err) {
    toast.show('预测失败', 'error')
  } finally {
    predicting.value = false
  }
}

async function handlePredictIterative() {
  predicting.value = true
  predictResult.value = null
  try {
    const res = await predictIterative(
      predictForm.material, predictForm.diameter, predictForm.thickness, predictForm.targetAngle,
    )
    if (res.code === 0) iterativeResult.value = res.data
  } catch (err) {
    toast.show('迭代预测失败', 'error')
  } finally {
    predicting.value = false
  }
}

async function fetchStatus() {
  try {
    const res = await getTrainingStatus()
    if (res.code === 0) Object.assign(trainingState, res.data)
  } catch {}
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    await fetchStatus()
    if (!trainingState.is_training) stopPolling()
  }, 1000)
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

onMounted(fetchStatus)
onUnmounted(stopPolling)
</script>

<style scoped>
.training-page { max-width: 1400px; margin: 0 auto; }

.container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

/* 上传区域 */
.upload-section { margin-bottom: 20px; }

.upload-area {
  display: block;
  border: 2px dashed var(--border-bright);
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}
.upload-area:hover { border-color: var(--color-primary); background: rgba(26, 109, 255, 0.02); }
.upload-area.has-file { border-color: var(--color-success); border-style: solid; }

.file-input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }

.upload-content { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.upload-icon { font-size: 32px; }
.upload-text { font-size: 13px; font-weight: 600; color: var(--text-secondary); }
.upload-hint { font-size: 11px; color: var(--text-muted); font-family: var(--font-display); }
.upload-status { font-size: 12px; font-weight: 600; }
.upload-status.success { color: var(--color-success); }
.upload-status.error { color: var(--color-danger); }

/* 参数区 */
.params-section { margin-bottom: 16px; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }

.form-item label { display: block; font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }

.form-item input, .form-item select {
  width: 100%; padding: 9px 12px; border: 1px solid var(--input-border);
  border-radius: 8px; background: #fff; color: var(--text-primary); font-size: 13px;
}
.form-item input:focus, .form-item select:focus { outline: none; border-color: var(--color-primary); }

.model-badge {
  display: inline-block; padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600;
}
.model-badge.ready { background: rgba(22, 163, 74, 0.08); color: var(--color-success); }
.model-badge.training { background: rgba(26, 109, 255, 0.08); color: var(--color-primary); }
.model-badge.none { background: var(--metal-dark); color: var(--text-muted); }

.action-row { display: flex; gap: 12px; }
.action-row .btn-primary, .action-row .btn-secondary { flex: 1; }

.empty-hint { text-align: center; padding: 24px; color: var(--text-muted); font-size: 13px; }

/* 预测操作 */
.predict-actions { display: flex; gap: 12px; margin: 16px 0; }
.predict-actions button { flex: 1; }

/* 预测结果 */
.predict-result, .iterative-result { margin-top: 16px; padding: 16px; background: var(--industrial-bg); border-radius: 10px; }

.result-header { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--text-primary); }

.result-class { padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.result-class.small { background: rgba(245, 158, 11, 0.12); color: var(--color-warning); }
.result-class.good { background: rgba(22, 163, 74, 0.12); color: var(--color-success); }
.result-class.large { background: rgba(220, 38, 38, 0.12); color: var(--color-danger); }

.prob-bars { display: flex; flex-direction: column; gap: 6px; }

.prob-row { display: flex; align-items: center; gap: 10px; }
.prob-label { width: 36px; font-size: 11px; font-weight: 600; color: var(--text-muted); }
.prob-value { width: 44px; text-align: right; font-family: var(--font-display); font-size: 11px; color: var(--text-secondary); }

.prob-bar-track { flex: 1; height: 8px; background: var(--metal-dark); border-radius: 4px; overflow: hidden; }
.prob-bar-fill { height: 100%; border-radius: 4px; transition: width 0.4s ease; }
.prob-bar-fill.bar-0 { background: var(--color-warning); }
.prob-bar-fill.bar-1 { background: var(--color-success); }
.prob-bar-fill.bar-2 { background: var(--color-danger); }

.final-angle { margin-top: 12px; display: flex; align-items: center; gap: 8px; font-size: 14px; color: var(--text-secondary); }
.highlight-value { font-size: 24px; font-weight: 700; color: var(--color-primary); font-family: var(--font-display); }
.offset-badge { font-size: 11px; color: var(--text-muted); background: var(--metal-dark); padding: 2px 8px; border-radius: 4px; }

.result-header.success { color: var(--color-success); }
.result-header.fail { color: var(--color-danger); }

/* 进度卡片 */
.progress-card { margin-top: 0; }

.progress-header { margin-bottom: 20px; }

.progress-stats { display: flex; gap: 24px; margin-bottom: 12px; flex-wrap: wrap; }

.stat-item { display: flex; flex-direction: column; gap: 4px; }
.stat-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.stat-value { font-size: 14px; font-weight: 600; color: var(--text-primary); font-family: var(--font-display); }
.stat-value.highlight { color: var(--color-success); }
.stat-value.msg { font-size: 12px; font-family: var(--font-body); font-weight: 400; max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.progress-bar-track { height: 6px; background: var(--metal-dark); border-radius: 3px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light)); border-radius: 3px; transition: width 0.4s ease; }

/* 图表 */
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 20px; }

.chart-box { background: var(--industrial-bg); border-radius: 10px; padding: 16px; }
.chart-title { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }
.chart-canvas { width: 100%; height: 180px; }
.chart-canvas svg { width: 100%; height: 100%; }

/* 混淆矩阵 */
.confusion-section { margin-top: 24px; }

.confusion-table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
.confusion-table th, .confusion-table td { padding: 10px 14px; text-align: center; border: 1px solid var(--border-color); }
.confusion-table th { background: var(--industrial-bg); font-weight: 600; color: var(--text-muted); font-size: 11px; }
.cm-label { text-align: left; font-weight: 600; color: var(--text-secondary); }
.cm-cell { font-family: var(--font-display); font-size: 14px; color: var(--text-muted); }
.cm-diag { background: rgba(22, 163, 74, 0.08); color: var(--color-success); font-weight: 700; }

@media (max-width: 768px) {
  .container { grid-template-columns: 1fr; }
  .charts-row { grid-template-columns: 1fr; }
  .form-row { grid-template-columns: 1fr; }
}
</style>
