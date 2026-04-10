"""
Pydantic 数据模型定义
定义所有 API 的请求/响应数据结构
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== 通用响应模型 ====================

class ApiResponse(BaseModel):
    """通用 API 响应格式"""
    code: int = Field(0, description="响应码，0 表示成功")
    message: str = Field("success", description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")


# ==================== 用户认证相关 ====================

UserRole = Literal['admin', 'maintenance', 'operator']


class User(BaseModel):
    """用户模型"""
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码（哈希存储）")
    role: UserRole = Field(..., description="用户角色")
    name: str = Field(..., description="显示名称")
    created_at: str = Field(..., description="创建时间")


class UserInfo(BaseModel):
    """用户信息（不含敏感信息）"""
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: UserRole = Field(..., description="用户角色")
    name: str = Field(..., description="显示名称")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    login_type: Literal['machine', 'user'] = Field(..., description="登录类型：machine-机器登录，user-用户登录")


class LoginResponse(BaseModel):
    """登录响应"""
    token: str = Field(..., description="访问令牌")
    user: Optional[UserInfo] = Field(None, description="用户信息（用户登录时返回）")
    machine_id: Optional[str] = Field(None, description="机器ID（机器登录时返回）")
    role: Optional[str] = Field(None, description="角色类型")


# ==================== 机器管理相关 ====================

class Machine(BaseModel):
    """机器模型"""
    id: str = Field(..., description="机器ID")
    name: str = Field(..., description="机器名称")
    location: str = Field(..., description="机器位置")
    status: Literal['online', 'offline', 'maintenance'] = Field(..., description="机器状态")
    created_at: str = Field(..., description="创建时间")
    last_active: str = Field(..., description="最后活跃时间")


class MachineCreateRequest(BaseModel):
    """创建机器请求"""
    name: str = Field(..., description="机器名称")
    location: str = Field(..., description="机器位置")


class MachineLoginRequest(BaseModel):
    """机器登录请求"""
    machine_id: str = Field(..., description="机器ID")
    password: str = Field(..., description="机器密码（可选，简单验证）")


# ==================== 参数推荐相关 ====================

class RecommendRequest(BaseModel):
    """推荐参数请求"""
    diameter: float = Field(..., ge=10, le=500, description="管径 (mm)")
    thickness: float = Field(..., ge=1, le=50, description="壁厚 (mm)")
    material: str = Field(..., min_length=1, description="材质")
    target_angle: float = Field(..., ge=0, le=180, description="目标角度 (度)")


class RecommendResult(BaseModel):
    """推荐参数结果"""
    recommended_angle: float = Field(..., description="推荐角度")
    recommended_offset: float = Field(..., description="推荐补偿值")
    explanation: str = Field(..., description="说明")
    timestamp: str = Field(..., description="时间戳 ISO 格式")


# ==================== 设备状态相关 ====================

DeviceStatus = Literal['offline', 'idle', 'running', 'completed', 'error']


class DeviceState(BaseModel):
    """设备状态"""
    device_id: str = Field(..., description="设备ID")
    device_status: DeviceStatus = Field(..., description="设备状态")
    online: bool = Field(..., description="是否在线")
    current_task: Optional[str] = Field(None, description="当前任务ID")
    current_angle: float = Field(0.0, description="当前设定角度")
    actual_angle: float = Field(0.0, description="实际角度")
    deviation: float = Field(0.0, description="偏差")
    last_heartbeat: str = Field(..., description="最后心跳时间 ISO 格式")


class TaskSubmitRequest(BaseModel):
    """任务提交请求"""
    diameter: float = Field(..., description="管径")
    thickness: float = Field(..., description="壁厚")
    material: str = Field(..., description="材质")
    target_angle: float = Field(..., description="目标角度")
    recommended_angle: float = Field(..., description="推荐角度")
    recommended_offset: float = Field(..., description="推荐补偿值")


class TaskSubmitResult(BaseModel):
    """任务提交结果"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="消息")


# ==================== 历史记录相关 ====================

class InputParams(BaseModel):
    """输入参数"""
    diameter: float
    thickness: float
    material: str
    target_angle: float


class RecommendParams(BaseModel):
    """推荐参数"""
    recommended_angle: float
    recommended_offset: float
    explanation: str


class ExecuteResult(BaseModel):
    """执行结果"""
    actual_angle: float
    deviation: float
    final_status: DeviceStatus


class HistoryRecord(BaseModel):
    """历史记录"""
    id: str = Field(..., description="记录ID")
    machine_id: str = Field(..., description="机器ID")
    input_params: InputParams = Field(..., description="输入参数")
    recommend_params: RecommendParams = Field(..., description="推荐参数")
    execute_result: Optional[ExecuteResult] = Field(None, description="执行结果")
    created_at: str = Field(..., description="创建时间")
    completed_at: Optional[str] = Field(None, description="完成时间")
