import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastItem {
  id: number
  type: ToastType
  message: string
  duration: number
}

let toastId = 0

export const useToastStore = defineStore('toast', () => {
  const toasts = ref<ToastItem[]>([])

  function show(message: string, type: ToastType = 'info', duration = 3000) {
    const id = ++toastId
    const item: ToastItem = { id, type, message, duration }
    toasts.value.push(item)

    if (duration > 0) {
      setTimeout(() => remove(id), duration)
    }
  }

  function remove(id: number) {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx >= 0) {
      toasts.value.splice(idx, 1)
    }
  }

  return { toasts, show, remove }
})
