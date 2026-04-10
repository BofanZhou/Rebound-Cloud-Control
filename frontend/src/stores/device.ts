import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DeviceState, DeviceStatus } from '../types'
import { getDeviceStatus } from '../api'

/**
 * 设备状态 Store
 * 管理设备状态，支持轮询更新
 */
export const useDeviceStore = defineStore('device', () => {
  // ==================== State ====================
  const deviceState = ref<DeviceState | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pollInterval = ref<number | null>(null)

  // ==================== Getters ====================
  const isOnline = computed(() => deviceState.value?.online ?? false)
  const currentStatus = computed(() => deviceState.value?.device_status ?? 'offline')
  const hasTask = computed(() => !!deviceState.value?.current_task)
  
  // 状态标签和颜色映射
  const statusConfig: Record<DeviceStatus, { label: string; type: 'success' | 'warning' | 'error' | 'info' | 'default' }> = {
    offline: { label: '离线', type: 'default' },
    idle: { label: '空闲', type: 'success' },
    running: { label: '运行中', type: 'warning' },
    completed: { label: '已完成', type: 'success' },
    error: { label: '错误', type: 'error' },
  }
  
  const statusDisplay = computed(() => {
    const status = currentStatus.value
    return statusConfig[status] || { label: '未知', type: 'default' }
  })

  // ==================== Actions ====================
  
  /**
   * 获取设备状态
   * @param machineId 机器ID（可选，不传则使用当前选中的机器）
   */
  async function fetchStatus(machineId?: string) {
    loading.value = true
    error.value = null
    
    try {
      const res = await getDeviceStatus(machineId)
      if (res.code === 0) {
        deviceState.value = res.data
      } else {
        error.value = res.message
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取设备状态失败'
    } finally {
      loading.value = false
    }
  }

  /**
   * 开始轮询
   * @param interval 轮询间隔（毫秒）
   * @param machineId 机器ID（可选）
   */
  function startPolling(interval: number = 2000, machineId?: string) {
    // 先停止现有轮询
    stopPolling()
    
    // 立即获取一次
    fetchStatus(machineId)
    
    // 设置定时器
    pollInterval.value = window.setInterval(() => {
      fetchStatus(machineId)
    }, interval)
  }

  /**
   * 停止轮询
   */
  function stopPolling() {
    if (pollInterval.value) {
      clearInterval(pollInterval.value)
      pollInterval.value = null
    }
  }

  /**
   * 更新设备状态（用于 WebSocket 或模拟）
   */
  function updateState(newState: DeviceState) {
    deviceState.value = newState
  }

  return {
    // State
    deviceState,
    loading,
    error,
    pollInterval,
    // Getters
    isOnline,
    currentStatus,
    hasTask,
    statusDisplay,
    // Actions
    fetchStatus,
    startPolling,
    stopPolling,
    updateState,
  }
})
