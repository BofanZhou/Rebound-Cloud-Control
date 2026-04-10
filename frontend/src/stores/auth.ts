import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo, UserRole, Machine, LoginRequest } from '../types'
import { login, selectMachine } from '../api'

/**
 * 认证状态 Store
 * 管理用户登录、权限、当前选中的机器
 */
export const useAuthStore = defineStore('auth', () => {
  // ==================== State ====================
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<UserInfo | null>(null)
  const currentMachine = ref<Machine | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ==================== Getters ====================
  const isLoggedIn = computed(() => !!token.value)
  
  const userRole = computed<UserRole | null>(() => {
    if (!user.value) {
      // 检查token中是否包含机器角色
      const storedRole = localStorage.getItem('role')
      if (storedRole === 'machine') return 'machine'
      return null
    }
    return user.value.role
  })
  
  const isMachineLogin = computed(() => userRole.value === 'machine')
  const isAdmin = computed(() => userRole.value === 'admin')
  const isMaintenance = computed(() => userRole.value === 'maintenance')
  const canManageMachines = computed(() => isAdmin.value || isMaintenance.value)
  
  const displayName = computed(() => {
    if (currentMachine.value) {
      return currentMachine.value.name
    }
    return user.value?.name || '未登录'
  })

  // ==================== Actions ====================
  
  /**
   * 用户登录
   */
  async function doLogin(request: LoginRequest) {
    loading.value = true
    error.value = null
    
    try {
      const res = await login(request)
      if (res.code === 0) {
        const data = res.data
        token.value = data.token
        localStorage.setItem('token', data.token)
        localStorage.setItem('role', data.role)
        
        if (data.user) {
          user.value = data.user
          localStorage.setItem('user', JSON.stringify(data.user))
        } else if (data.machine_id) {
          // 机器登录
          localStorage.setItem('machine_id', data.machine_id)
          if (data.machine_name) {
            localStorage.setItem('machine_name', data.machine_name)
          }
        }
        
        return true
      } else {
        error.value = res.message
        return false
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '登录失败'
      return false
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 选择机器（用户登录后）
   */
  async function selectCurrentMachine(machine: Machine) {
    loading.value = true
    error.value = null
    
    try {
      const res = await selectMachine(machine.id)
      if (res.code === 0) {
        const data = res.data
        // 更新token
        token.value = data.token
        localStorage.setItem('token', data.token)
        
        currentMachine.value = machine
        localStorage.setItem('current_machine', JSON.stringify(machine))
        
        return true
      } else {
        error.value = res.message
        return false
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '选择机器失败'
      return false
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 恢复登录状态
   */
  function restoreSession() {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    const storedMachine = localStorage.getItem('current_machine')
    const storedRole = localStorage.getItem('role')
    
    if (storedToken) {
      token.value = storedToken
    }
    
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch {
        user.value = null
      }
    }
    
    if (storedMachine) {
      try {
        currentMachine.value = JSON.parse(storedMachine)
      } catch {
        currentMachine.value = null
      }
    }
    
    if (storedRole && !user.value) {
      // 机器登录模式
      if (storedRole === 'machine') {
        const machineId = localStorage.getItem('machine_id')
        const machineName = localStorage.getItem('machine_name')
        if (machineId) {
          currentMachine.value = {
            id: machineId,
            name: machineName || machineId,
            location: '',
            status: 'online',
            created_at: '',
            last_active: '',
          }
        }
      }
    }
  }
  
  /**
   * 登出
   */
  function logout() {
    token.value = null
    user.value = null
    currentMachine.value = null
    
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('role')
    localStorage.removeItem('machine_id')
    localStorage.removeItem('machine_name')
    localStorage.removeItem('current_machine')
  }

  return {
    // State
    token,
    user,
    currentMachine,
    loading,
    error,
    // Getters
    isLoggedIn,
    userRole,
    isMachineLogin,
    isAdmin,
    isMaintenance,
    canManageMachines,
    displayName,
    // Actions
    doLogin,
    selectCurrentMachine,
    restoreSession,
    logout,
  }
})
