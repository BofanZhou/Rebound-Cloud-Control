// API 接口封装
import type {
  ApiResponse,
  RecommendParams,
  RecommendResult,
  DeviceState,
  TaskSubmitParams,
  TaskSubmitResult,
  HistoryRecord,
  LoginRequest,
  LoginResponse,
  Machine,
  MachineCreateRequest,
  UserInfo,
} from '../types'

// API 基础地址，生产环境使用环境变量
const API_BASE = import.meta.env.VITE_API_BASE || '/api'

// 获取token
function getToken(): string | null {
  return localStorage.getItem('token')
}

// 通用请求封装
async function request<T>(url: string, options?: RequestInit): Promise<ApiResponse<T>> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  
  // 添加认证头
  const token = getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  const response = await fetch(`${API_BASE}${url}`, {
    headers,
    ...options,
  })
  
  if (!response.ok) {
    if (response.status === 401) {
      // 未授权，清除token并跳转登录
      localStorage.removeItem('token')
      window.location.href = '/login'
      throw new Error('未登录或登录已过期')
    }
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  return response.json()
}

// ==================== 认证相关 API ====================

/**
 * 登录
 * @param request 登录请求
 */
export async function login(data: LoginRequest): Promise<ApiResponse<LoginResponse>> {
  return request<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/**
 * 获取当前用户信息
 */
export async function getMe(): Promise<ApiResponse<any>> {
  return request('/auth/me', {
    method: 'GET',
  })
}

/**
 * 获取用户列表（仅管理员）
 */
export async function getUsers(): Promise<ApiResponse<UserInfo[]>> {
  return request('/auth/users', {
    method: 'GET',
  })
}

// ==================== 机器管理 API ====================

/**
 * 获取机器列表
 * @param status 状态筛选（可选）
 */
export async function getMachines(status?: string): Promise<ApiResponse<Machine[]>> {
  let url = '/machines'
  if (status) {
    url += `?status=${status}`
  }
  return request<Machine[]>(url, {
    method: 'GET',
  })
}

/**
 * 创建机器（仅管理员）
 * @param request 创建请求
 */
export async function createMachine(data: MachineCreateRequest): Promise<ApiResponse<Machine>> {
  return request<Machine>('/machines', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/**
 * 选择机器
 * @param machineId 机器ID
 */
export async function selectMachine(machineId: string): Promise<ApiResponse<{ token: string; machine: Machine }>> {
  return request(`/machines/${machineId}/select`, {
    method: 'POST',
  })
}

// ==================== 推荐参数 API ====================

/**
 * 获取推荐参数
 * @param params 输入参数
 */
export async function getRecommend(params: RecommendParams): Promise<ApiResponse<RecommendResult>> {
  return request<RecommendResult>('/recommend', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

// ==================== 设备状态 API ====================

/**
 * 获取设备当前状态
 * @param machineId 机器ID（可选）
 */
export async function getDeviceStatus(machineId?: string): Promise<ApiResponse<DeviceState>> {
  let url = '/device/status'
  if (machineId) {
    url += `?machine_id=${machineId}`
  }
  return request<DeviceState>(url, {
    method: 'GET',
  })
}

/**
 * 提交任务到设备
 * @param params 任务参数
 * @param machineId 机器ID（可选）
 */
export async function submitTask(params: TaskSubmitParams, machineId?: string): Promise<ApiResponse<TaskSubmitResult>> {
  let url = '/device/submit'
  if (machineId) {
    url += `?machine_id=${machineId}`
  }
  return request<TaskSubmitResult>(url, {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

// ==================== 历史记录 API ====================

/**
 * 获取历史记录列表
 * @param limit 限制数量
 * @param machineId 机器ID（可选）
 */
export async function getHistory(limit: number = 10, machineId?: string): Promise<ApiResponse<HistoryRecord[]>> {
  let url = `/history?limit=${limit}`
  if (machineId) {
    url += `&machine_id=${machineId}`
  }
  return request<HistoryRecord[]>(url, {
    method: 'GET',
  })
}
