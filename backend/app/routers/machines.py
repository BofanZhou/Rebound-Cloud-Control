"""
机器管理路由
GET /api/machines - 获取机器列表
POST /api/machines - 创建机器
GET /api/machines/{machine_id} - 获取机器详情
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from ..models.schemas import ApiResponse, MachineCreateRequest
from ..services.machine_manager import machine_manager
from ..services.auth import auth_service

router = APIRouter(prefix="/machines", tags=["机器管理"])


def get_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """从请求头中提取token"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.replace("Bearer ", "")


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
    token = get_token_from_header(authorization)
    if not token or not auth_service.verify_token(token):
        raise HTTPException(status_code=401, detail="未登录或token已过期")
    
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
    authorization: str = Header(None)
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
    token = get_token_from_header(authorization)
    
    # 检查权限
    if not auth_service.has_permission(token, ["admin"]):
        raise HTTPException(status_code=403, detail="无权限创建机器")
    
    machine = machine_manager.create_machine(request)
    
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
    token = get_token_from_header(authorization)
    if not token or not auth_service.verify_token(token):
        raise HTTPException(status_code=401, detail="未登录或token已过期")
    
    machine = machine_manager.get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="机器不存在")
    
    return ApiResponse(
        code=0,
        message="success",
        data=machine.model_dump()
    )


@router.post("/{machine_id}/select", response_model=ApiResponse)
async def select_machine(
    machine_id: str,
    authorization: str = Header(None)
):
    """
    选择机器进入管理界面
    
    用户登录后需要选择一台机器进行操作
    """
    token = get_token_from_header(authorization)
    if not token or not auth_service.verify_token(token):
        raise HTTPException(status_code=401, detail="未登录或token已过期")
    
    machine = machine_manager.get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="机器不存在")
    
    # 更新机器状态
    machine_manager.update_machine_status(machine_id, "online")
    
    # 获取新的token，包含机器信息
    token_data = auth_service.verify_token(token)
    new_token = auth_service.generate_token(
        token_data["user_id"], 
        f"{token_data['role']}:machine:{machine_id}"
    )
    
    return ApiResponse(
        code=0,
        message="success",
        data={
            "token": new_token,
            "machine": machine.model_dump(),
        }
    )
