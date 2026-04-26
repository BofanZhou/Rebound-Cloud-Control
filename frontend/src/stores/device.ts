import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DeviceState, DeviceStatus } from '../types'
import { getDeviceStatus } from '../api'

/**
 * 设备状态 Store
 * 管理设备状态，优先使用 WebSocket 实时推送，降级回轮询
 */
export const useDeviceStore = defineStore('device', () => {
  // ==================== State ====================
  const deviceState = ref<DeviceState | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pollInterval = ref<number | null>(null)
  const wsConnected = ref(false)
  const wsConnecting = ref(false)

  // WebSocket instance
  let ws: WebSocket | null = null
  let wsReconnectTimer: number | null = null

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
   * 获取设备状态（轮询备用）
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
   * 连接 WebSocket
   * @param machineId 机器ID
   * @param baseUrl WebSocket 基础地址（默认使用当前页面 host）
   */
  function connectWebSocket(machineId: string, baseUrl?: string) {
    // 如果已有连接，先断开
    disconnectWebSocket()

    if (!machineId) {
      return
    }

    wsConnecting.value = true

    // 构建 WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = baseUrl || window.location.host
    const wsUrl = `${protocol}//${host}/ws/device/${machineId}`

    try {
      ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        wsConnected.value = true
        wsConnecting.value = false
        // 连接成功后停止轮询
        stopPolling()
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          if (message.type === 'state_update' && message.data) {
            deviceState.value = message.data as DeviceState
          }
        } catch {
          // 忽略解析错误
        }
      }

      ws.onclose = () => {
        wsConnected.value = false
        wsConnecting.value = false
        ws = null
        // 断开后自动降级到轮询
        if (!pollInterval.value) {
          startPolling(2000, machineId)
        }
      }

      ws.onerror = () => {
        wsConnected.value = false
        wsConnecting.value = false
        // 连接失败，降级到轮询
        if (!pollInterval.value) {
          startPolling(2000, machineId)
        }
      }
    } catch {
      wsConnecting.value = false
      // 创建失败，降级到轮询
      startPolling(2000, machineId)
    }
  }

  /**
   * 断开 WebSocket
   */
  function disconnectWebSocket() {
    if (wsReconnectTimer) {
      clearTimeout(wsReconnectTimer)
      wsReconnectTimer = null
    }
    if (ws) {
      ws.close()
      ws = null
    }
    wsConnected.value = false
    wsConnecting.value = false
  }

  /**
   * 启动设备监控（优先 WebSocket，降级轮询）
   * @param machineId 机器ID
   */
  function startMonitoring(machineId?: string) {
    if (!machineId) {
      return
    }
    // 尝试 WebSocket，失败会自动降级到轮询
    connectWebSocket(machineId)
  }

  /**
   * 停止设备监控
   */
  function stopMonitoring() {
    disconnectWebSocket()
    stopPolling()
  }

  /**
   * 更新设备状态（用于外部直接更新）
   */
  function updateState(newState: DeviceState) {
    deviceState.value = newState
  }

  /**
   * 发送 WebSocket 消息（如远程重置）
   */
  function sendCommand(command: string) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(command)
    }
  }

  return {
    // State
    deviceState,
    loading,
    error,
    pollInterval,
    wsConnected,
    wsConnecting,
    // Getters
    isOnline,
    currentStatus,
    hasTask,
    statusDisplay,
    // Actions
    fetchStatus,
    startPolling,
    stopPolling,
    connectWebSocket,
    disconnectWebSocket,
    startMonitoring,
    stopMonitoring,
    updateState,
    sendCommand,
  }
})
