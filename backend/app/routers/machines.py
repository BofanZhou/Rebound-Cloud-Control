"""
机器管理路由
GET /api/machines - 获取机器列表
POST /api/machines - 创建机器
GET /api/machines/{machine_id} - 获取机器详情
"""
from fastapi import APIRouter, HTTPException, Header, Request
from typing import Optional
from ..models.schemas import ApiResponse, MachineCreateRequest
from pydantic import BaseModel, Field
from ..services.machine_manager import machine_manager
from ..services.auth import auth_service
from ..services.audit_log import log_operation
from ..utils import get_token_from_header, verify_token

router = APIRouter(prefix="/machines", tags=["机器管理"])


@router.get("", response_model=ApiResponse)
async def get_machines(
    authorization: str = Header(None),
    status: Optional[str] = None
):
    """
    获取机器列表
    
    参数：
    - status: 按状态筛选 (online/offline/maintenance)
    
    响应示例：
    ```json
    {
        "code": 0,
        "message": "success",
        "data": [
            {
                "id": "MCH-XXX",
                "name": "机器1",
                "location": "车间A",
                "status": "online",
                "created_at": "2024-01-01T00:00:00",
                "last_active": "2024-01-01T12:00:00"
            }
        ]
    }
    ```
    """
    verify_token(authorization)
    
    machines = machine_manager.get_all_machines()
    
    # 按状态筛选
    if status:
        machines = [m for m in machines if m.status == status]
    
    return ApiResponse(
        code=0,
        message="success",
        data=[m.model_dump() for m in machines]
    )


@router.post("", response_model=ApiResponse)
async def create_machine(
    request: MachineCreateRequest,
    authorization: str = Header(None),
    http_request: Request = None,
):
    """
    创建新机器（仅管理员）
    
    请求示例：
    ```json
    {
        "name": "新机器",
        "location": "车间B"
    }
    ```
    """
    if not auth_service.has_permission(get_token_from_header(authorization), ["admin"]):
        raise HTTPException(status_code=403, detail="无权限创建机器")
    
    machine = machine_manager.create_machine(request)

    token_data = auth_service.verify_token(token)
    current_username = token_data.get("username", token_data.get("user_id", "unknown")) if token_data else "unknown"
    current_role = token_data.get("role", "unknown") if token_data else "unknown"

    log_operation(
        username=current_username,
        role=current_role,
        action="create_machine",
        target_type="machine",
        target_id=machine.id,
        detail=f"创建机器: {machine.name}",
        ip_address=http_request.client.host if http_request and http_request.client else None,
    )

    return ApiResponse(
        code=0,
        message="success",
        data=machine.model_dump()
    )


@router.get("/{machine_id}", response_model=ApiResponse)
async def get_machine_detail(
    machine_id: str,
    authorization: str = Header(None)
):
    """
    获取机器详情
    """
    verify_token(authorization)
    
    machine = machine_manager.get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="机器不存在")
    
    return ApiResponse(
        code=0,
        message="success",
        data=machine.model_dump()
    )


class UpdateMachineRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    location: str | None = Field(None, min_length=1, max_length=200)


@router.put("/{machine_id}", response_model=ApiResponse)
async def update_machine(
    machine_id: str,
    request: UpdateMachineRequest,
    authorization: str = Header(None),
    http_request: Request = None,
):
    """
    修改机器信息（仅管理员）
    """
    if not auth_service.has_permission(get_token_from_header(authorization), ["admin"]):
        raise HTTPException(status_code=403, detail="无权限修改机器")
    
    machine = machine_manager.update_machine(
        machine_id,
        name=request.name,
        location=request.location,
    )
    if not machine:
        raise HTTPException(status_code=404, detail="机器不存在")
    
    token_data = auth_service.verify_token(token)
    current_username = token_data.get("username", token_data.get("user_id", "unknown")) if token_data else "unknown"
    current_role = token_data.get("role", "unknown") if token_data else "unknown"

    log_operation(
        username=current_username,
        role=current_role,
        action="update_machine",
        target_type="machine",
        target_id=machine_id,
        detail=f"修改机器信息: {machine.name}",
        ip_address=http_request.client.host if http_request and http_request.client else None,
    )

    return ApiResponse(
        code=0,
        message="success",
        data=machine.model_dump()
    )


@router.delete("/{machine_id}", response_model=ApiResponse)
async def delete_machine(
    machine_id: str,
    authorization: str = Header(None),
    http_request: Request = None,
):
    """
    删除机器（仅管理员）
    """
    if not auth_service.has_permission(get_token_from_header(authorization), ["admin"]):
        raise HTTPException(status_code=403, detail="无权限删除机器")
    
    success = machine_manager.delete_machine(machine_id)
    if not success:
        raise HTTPException(status_code=404, detail="机器不存在")
    
    token_data = auth_service.verify_token(token)
    current_username = token_data.get("username", token_data.get("user_id", "unknown")) if token_data else "unknown"
    current_role = token_data.get("role", "unknown") if token_data else "unknown"

    log_operation(
        username=current_username,
        role=current_role,
        action="delete_machine",
        target_type="machine",
        target_id=machine_id,
        detail=f"删除机器: {machine_id}",
        ip_address=http_request.client.host if http_request and http_request.client else None,
    )
    return ApiResponse(code=0, message="success", data={})


@router.post("/{machine_id}/select", response_model=ApiResponse)
async def select_machine(
    machine_id: str,
    authorization: str = Header(None)
):
    """
    选择机器进入管理界面
    
    用户登录后需要选择一台机器进行操作
    """
    token_data = verify_token(authorization)
    
    machine = machine_manager.get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="机器不存在")
    
    # 更新机器状态
    machine_manager.update_machine_status(machine_id, "online")
    
    # 获取新的token，包含机器信息
    new_token = auth_service.generate_token(
        token_data["user_id"], 
        f"{token_data['role']}:machine:{machine_id}",
        token_data.get("username", token_data["user_id"]),
    )
    
    return ApiResponse(
        code=0,
        message="success",
        data={
            "token": new_token,
            "machine": machine.model_dump(),
        }
    )
