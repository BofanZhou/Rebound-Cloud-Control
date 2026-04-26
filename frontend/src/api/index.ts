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
  TrainingStatus,
  PredictResult,
  IterativeResult,
} from '../types'

const API_BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '')
const REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 12000)

function getFallbackBaseList(): string[] {
  // Primary base first, then fallback without /api prefix for platforms
  // that forward to backend root paths.
  const bases = [API_BASE]
  if (API_BASE === '/api') {
    bases.push('')
  }
  return bases
}

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
    const bases = getFallbackBaseList()
    let lastError: Error | null = null

    for (let i = 0; i < bases.length; i++) {
      const base = bases[i]
      const response = await fetch(`${base}${url}`, {
        headers,
        ...options,
        signal: controller.signal,
      })

      if (response.ok) {
        return response.json()
      }

      if (response.status === 401) {
        logoutAndRedirectToLogin()
        throw new Error('Unauthorized or session expired')
      }

      // Fallback only when primary /api route is not found.
      if (response.status === 404 && i < bases.length - 1) {
        continue
      }

      lastError = new Error(await parseErrorMessage(response))
      break
    }

    throw lastError || new Error('Request failed')
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
  return request<UserInfo[]>('/auth/users', {
    method: 'GET',
  })
}

export async function createUser(data: { username: string; password: string; role: string; name: string }): Promise<ApiResponse<UserInfo>> {
  return request<UserInfo>('/auth/users', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function deleteUser(username: string): Promise<ApiResponse<null>> {
  return request<null>(`/auth/users/${username}`, {
    method: 'DELETE',
  })
}

export async function updateUserPassword(username: string, newPassword: string): Promise<ApiResponse<null>> {
  return request<null>(`/auth/users/${username}/password`, {
    method: 'POST',
    body: JSON.stringify({ new_password: newPassword }),
  })
}

export async function getOperationLogs(limit: number = 100, offset: number = 0, username?: string, action?: string): Promise<ApiResponse<{ logs: any[]; total: number; limit: number; offset: number }>> {
  let url = `/auth/logs?limit=${limit}&offset=${offset}`
  if (username) url += `&username=${username}`
  if (action) url += `&action=${action}`
  return request(url, {
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

export async function updateMachine(machineId: string, data: { name?: string; location?: string }): Promise<ApiResponse<Machine>> {
  return request<Machine>(`/machines/${machineId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteMachine(machineId: string): Promise<ApiResponse<null>> {
  return request<null>(`/machines/${machineId}`, {
    method: 'DELETE',
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

// ==================== 模型训练 ====================

export async function uploadDataset(file: File): Promise<ApiResponse<{ count: number; sample: any[] }>> {
  const formData = new FormData()
  formData.append('file', file)
  const token = getToken()
  const headers: Record<string, string> = {}
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${API_BASE}/training/upload`, { method: 'POST', body: formData, headers })
  if (res.status === 401) { logoutAndRedirectToLogin(); throw new Error('Unauthorized') }
  return res.json()
}

export async function getTrainingStatus(): Promise<ApiResponse<TrainingStatus>> {
  return request<TrainingStatus>('/training/status', { method: 'GET' })
}

export async function startTraining(epochs = 80, batchSize = 32, lr = 0.001): Promise<ApiResponse<{ message: string }>> {
  const formData = new FormData()
  formData.append('epochs', String(epochs))
  formData.append('batch_size', String(batchSize))
  formData.append('learning_rate', String(lr))
  const token = getToken()
  const headers: Record<string, string> = {}
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${API_BASE}/training/start`, { method: 'POST', body: formData, headers })
  return res.json()
}

export async function predict(material: string, diameter: number, thickness: number, targetAngle: number): Promise<ApiResponse<PredictResult>> {
  const formData = new FormData()
  formData.append('material', material)
  formData.append('diameter', String(diameter))
  formData.append('thickness', String(thickness))
  formData.append('target_angle', String(targetAngle))
  const token = getToken()
  const headers: Record<string, string> = {}
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${API_BASE}/training/predict`, { method: 'POST', body: formData, headers })
  return res.json()
}

export async function predictIterative(
  material: string, diameter: number, thickness: number, targetAngle: number,
  maxIter = 20, step = 0.5,
): Promise<ApiResponse<IterativeResult>> {
  const formData = new FormData()
  formData.append('material', material)
  formData.append('diameter', String(diameter))
  formData.append('thickness', String(thickness))
  formData.append('target_angle', String(targetAngle))
  formData.append('max_iterations', String(maxIter))
  formData.append('step', String(step))
  const token = getToken()
  const headers: Record<string, string> = {}
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${API_BASE}/training/predict-iterative`, { method: 'POST', body: formData, headers })
  return res.json()
}
