// ==================== API 通用响应类型 ====================

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// ==================== 用户认证相关类型 ====================

export type UserRole = 'admin' | 'maintenance' | 'operator' | 'machine'

export interface UserInfo {
  id: string
  username: string
  role: UserRole
  name: string
}

export interface LoginRequest {
  username: string
  password: string
  login_type: 'machine' | 'user'
}

export interface LoginResponse {
  token: string
  user?: UserInfo
  machine_id?: string
  machine_name?: string
  role: UserRole
}

// ==================== 机器管理相关类型 ====================

export type MachineStatus = 'online' | 'offline' | 'maintenance'

export interface Machine {
  id: string
  name: string
  location: string
  status: MachineStatus
  created_at: string
  last_active: string
}

export interface MachineCreateRequest {
  name: string
  location: string
}

// ==================== 参数推荐相关类型 ====================

export interface RecommendParams {
  diameter: number          // 管径 (mm)
  thickness: number         // 壁厚 (mm)
  material: string          // 材质
  target_angle: number      // 目标角度 (度)
}

export interface RecommendResult {
  recommended_angle: number   // 推荐角度
  recommended_offset: number  // 推荐补偿值
  explanation: string         // 说明
  timestamp: string           // 时间戳
}

// ==================== 设备状态相关类型 ====================

export type DeviceStatus = 'offline' | 'idle' | 'running' | 'completed' | 'error'

export interface DeviceState {
  device_id: string
  device_status: DeviceStatus
  online: boolean
  current_task: string | null
  current_angle: number
  actual_angle: number
  deviation: number
  last_heartbeat: string
}

export interface TaskSubmitParams {
  diameter: number
  thickness: number
  material: string
  target_angle: number
  recommended_angle: number
  recommended_offset: number
}

export interface TaskSubmitResult {
  task_id: string
  status: string
  message: string
}

// ==================== 历史记录类型 ====================

export interface HistoryRecord {
  id: string
  machine_id: string
  input_params: {
    diameter: number
    thickness: number
    material: string
    target_angle: number
  }
  recommend_params: {
    recommended_angle: number
    recommended_offset: number
    explanation: string
  }
  execute_result?: {
    actual_angle: number
    deviation: number
    final_status: DeviceStatus
  }
  created_at: string
  completed_at?: string
}
