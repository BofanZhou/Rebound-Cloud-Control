"""
设备状态路由
GET /api/device/status
POST /api/device/submit
"""
from fastapi import APIRouter, HTTPException, Header, Query, Request
from typing import Optional
from ..models.schemas import ApiResponse, TaskSubmitRequest, HistoryRecord, InputParams, RecommendParams
from ..services.machine_manager import machine_manager
from ..services.audit_log import log_operation
from ..utils import get_token_from_header, get_machine_id_from_token
from datetime import datetime, timezone

router = APIRouter(prefix="/device", tags=["设备状态"])


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
    http_request: Request = None,
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

        # 创建历史记录（任务已提交，状态为 running）
        history_record = HistoryRecord(
            id=result["task_id"],
            machine_id=machine_id,
            input_params=InputParams(
                diameter=request.diameter,
                thickness=request.thickness,
                material=request.material,
                target_angle=request.target_angle,
            ),
            recommend_params=RecommendParams(
                recommended_angle=request.recommended_angle,
                recommended_offset=request.recommended_offset,
                explanation="",
            ),
            execute_result=None,
            created_at=datetime.now(timezone.utc).isoformat(),
            completed_at=None,
        )
        machine_manager.add_history(machine_id, history_record)

        # 记录操作日志
        log_operation(
            username="operator",
            role="operator",
            action="submit_task",
            target_type="task",
            target_id=result["task_id"],
            detail=f"提交任务: 管径{request.diameter}mm 材质{request.material}",
            ip_address=http_request.client.host if http_request and http_request.client else None,
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
