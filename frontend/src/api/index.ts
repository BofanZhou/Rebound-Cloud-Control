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

const API_BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '')
const REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 12000)

function getToken(): string | null {
  return localStorage.getItem('token')
}

function logoutAndRedirectToLogin() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('role')
  localStorage.removeItem('machine_id')
  localStorage.removeItem('machine_name')
  localStorage.removeItem('current_machine')

  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const payload = await response.json()

    if (payload?.message && typeof payload.message === 'string') {
      return payload.message
    }

    if (payload?.detail) {
      return typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail)
    }
  } catch {
    // ignore and fallback to status text
  }

  return `Request failed (${response.status})`
}

async function request<T>(url: string, options?: RequestInit): Promise<ApiResponse<T>> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  const token = getToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  try {
    const response = await fetch(`${API_BASE}${url}`, {
      headers,
      ...options,
      signal: controller.signal,
    })

    if (!response.ok) {
      if (response.status === 401) {
        logoutAndRedirectToLogin()
        throw new Error('Unauthorized or session expired')
      }

      throw new Error(await parseErrorMessage(response))
    }

    return response.json()
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error(`Request timeout (>${REQUEST_TIMEOUT_MS}ms)`)
    }

    throw error
  } finally {
    clearTimeout(timeout)
  }
}

export async function login(data: LoginRequest): Promise<ApiResponse<LoginResponse>> {
  return request<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getMe(): Promise<ApiResponse<any>> {
  return request('/auth/me', {
    method: 'GET',
  })
}

export async function getUsers(): Promise<ApiResponse<UserInfo[]>> {
  return request('/auth/users', {
    method: 'GET',
  })
}

export async function getMachines(status?: string): Promise<ApiResponse<Machine[]>> {
  let url = '/machines'
  if (status) {
    url += `?status=${status}`
  }
  return request<Machine[]>(url, {
    method: 'GET',
  })
}

export async function createMachine(data: MachineCreateRequest): Promise<ApiResponse<Machine>> {
  return request<Machine>('/machines', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function selectMachine(machineId: string): Promise<ApiResponse<{ token: string; machine: Machine }>> {
  return request(`/machines/${machineId}/select`, {
    method: 'POST',
  })
}

export async function getRecommend(params: RecommendParams): Promise<ApiResponse<RecommendResult>> {
  return request<RecommendResult>('/recommend', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

export async function getDeviceStatus(machineId?: string): Promise<ApiResponse<DeviceState>> {
  let url = '/device/status'
  if (machineId) {
    url += `?machine_id=${machineId}`
  }
  return request<DeviceState>(url, {
    method: 'GET',
  })
}

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

export async function getHistory(limit: number = 10, machineId?: string): Promise<ApiResponse<HistoryRecord[]>> {
  let url = `/history?limit=${limit}`
  if (machineId) {
    url += `&machine_id=${machineId}`
  }
  return request<HistoryRecord[]>(url, {
    method: 'GET',
  })
}
