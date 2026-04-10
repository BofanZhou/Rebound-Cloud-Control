import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { HistoryRecord } from '../types'
import { getHistory } from '../api'

/**
 * 历史记录 Store
 * 管理任务历史记录
 */
export const useHistoryStore = defineStore('history', () => {
  // ==================== State ====================
  const records = ref<HistoryRecord[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ==================== Actions ====================
  
  /**
   * 获取历史记录
   * @param limit 限制数量
   * @param machineId 机器ID（可选）
   */
  async function fetchHistory(limit: number = 10, machineId?: string) {
    loading.value = true
    error.value = null
    
    try {
      const res = await getHistory(limit, machineId)
      if (res.code === 0) {
        records.value = res.data
      } else {
        error.value = res.message
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取历史记录失败'
    } finally {
      loading.value = false
    }
  }

  /**
   * 添加新记录（本地）
   */
  function addRecord(record: HistoryRecord) {
    records.value.unshift(record)
    // 保持最多 50 条
    if (records.value.length > 50) {
      records.value = records.value.slice(0, 50)
    }
  }

  /**
   * 清空记录（本地）
   */
  function clearRecords() {
    records.value = []
  }

  return {
    // State
    records,
    loading,
    error,
    // Actions
    fetchHistory,
    addRecord,
    clearRecords,
  }
})
