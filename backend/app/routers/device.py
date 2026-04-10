"""
设备状态路由
GET /api/device/status
POST /api/device/submit
"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from ..models.schemas import ApiResponse, TaskSubmitRequest
from ..services.machine_manager import machine_manager
from ..services.auth import auth_service

router = APIRouter(prefix="/device", tags=["设备状态"])


def get_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """从请求头中提取token"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.replace("Bearer ", "")


def get_machine_id_from_token(token: str) -> str:
    """从token中提取机器ID"""
    token_data = auth_service.verify_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    
    role = token_data.get("role", "")
    
    # 如果是机器直接登录
    if role == "machine":
        return token_data.get("user_id", "")
    
    # 如果是用户选择了机器，角色格式为 role:machine:machine_id
    if ":machine:" in role:
        return role.split(":machine:")[1]
    
    # 否则返回第一个可用的机器（用于兼容单机模式）
    machines = machine_manager.get_all_machines()
    if machines:
        return machines[0].id
    
    raise HTTPException(status_code=400, detail="未选择机器")


@router.get("/status", response_model=ApiResponse)
async def get_device_status(
    authorization: str = Header(None),
    machine_id: Optional[str] = Query(None, description="机器ID（可选，优先使用token中的信息）")
):
    """
    获取设备当前状态
    
    返回设备的实时状态，包括：
    - device_status: 设备状态 (offline/idle/running/completed/error)
    - online: 是否在线
    - current_task: 当前任务ID
    - current_angle: 当前设定角度
    - actual_angle: 实际角度
    - deviation: 偏差
    - last_heartbeat: 最后心跳时间
    
    响应示例：
    ```json
    {
        "code": 0,
        "message": "success",
        "data": {
            "device_id": "DEV-MCH-XXX",
            "device_status": "idle",
            "online": true,
            "current_task": null,
            "current_angle": 0,
            "actual_angle": 0,
            "deviation": 0,
            "last_heartbeat": "2024-01-01T12:00:00"
        }
    }
    ```
    """
    try:
        # 验证token
        token = get_token_from_header(authorization)
        if not token:
            raise HTTPException(status_code=401, detail="未提供认证信息")
        
        # 获取机器ID
        if machine_id:
            # 使用query参数中的machine_id
            machine = machine_manager.get_machine(machine_id)
            if not machine:
                raise HTTPException(status_code=404, detail="机器不存在")
        else:
            machine_id = get_machine_id_from_token(token)
        
        # 获取模拟器状态
        simulator = machine_manager.get_simulator(machine_id)
        if not simulator:
            raise HTTPException(status_code=404, detail="设备未找到")
        
        state = simulator.state
        return ApiResponse(
            code=0,
            message="success",
            data=state.model_dump(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=ApiResponse)
async def submit_task(
    request: TaskSubmitRequest,
    authorization: str = Header(None),
    machine_id: Optional[str] = Query(None, description="机器ID（可选，优先使用token中的信息）")
):
    """
    提交任务到设备
    
    将弯折任务提交到设备执行。
    设备会从 idle 状态进入 running 状态，
    任务完成后自动进入 completed 状态。
    
    请求示例：
    ```json
    {
        "diameter": 50,
        "thickness": 5,
        "material": "普通钢",
        "target_angle": 90,
        "recommended_angle": 92,
        "recommended_offset": 2
    }
    ```
    
    响应示例：
    ```json
    {
        "code": 0,
        "message": "success",
        "data": {
            "task_id": "TASK-A1B2C3D4",
            "status": "running",
            "message": "任务 TASK-A1B2C3D4 已开始执行"
        }
    }
    ```
    
    错误响应：
    - 设备离线: HTTP 400
    - 设备忙: HTTP 400
    """
    try:
        # 验证token
        token = get_token_from_header(authorization)
        if not token:
            raise HTTPException(status_code=401, detail="未提供认证信息")
        
        # 获取机器ID
        if machine_id:
            machine = machine_manager.get_machine(machine_id)
            if not machine:
                raise HTTPException(status_code=404, detail="机器不存在")
        else:
            machine_id = get_machine_id_from_token(token)
        
        # 获取模拟器
        simulator = machine_manager.get_simulator(machine_id)
        if not simulator:
            raise HTTPException(status_code=404, detail="设备未找到")
        
        result = await simulator.submit_task(
            diameter=request.diameter,
            thickness=request.thickness,
            material=request.material,
            target_angle=request.target_angle,
            recommended_angle=request.recommended_angle,
            recommended_offset=request.recommended_offset,
        )
        
        return ApiResponse(
            code=0,
            message="success",
            data=result,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
