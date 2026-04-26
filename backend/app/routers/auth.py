"""
用户认证路由
POST /api/auth/login
POST /api/auth/logout
GET /api/auth/me
GET /api/auth/users        - 获取用户列表（管理员）
POST /api/auth/users       - 创建用户（管理员）
DELETE /api/auth/users/{username} - 删除用户（管理员）
POST /api/auth/users/{username}/password - 修改密码（管理员）
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, Field
from ..models.schemas import ApiResponse, LoginRequest, UserInfo, MachineCreateRequest, UserRole
from ..services.auth import auth_service
from ..services.machine_manager import machine_manager
from ..services.audit_log import log_operation, get_logs
from ..utils import get_token_from_header, require_admin, verify_token

router = APIRouter(prefix="/auth", tags=["认证"])


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4, max_length=50)
    role: UserRole = Field(...)
    name: str = Field(..., min_length=1, max_length=50)


class UpdatePasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=4, max_length=50)


@router.post("/login", response_model=ApiResponse)
async def login(request: LoginRequest, http_request: Request):
    """
    用户登录
    
    支持两种登录方式：
    - machine: 机器登录，直接输入机器ID
    - user: 用户登录，输入用户名密码
    """
    try:
        if request.login_type == "machine":
            # 机器登录
            machine = machine_manager.get_machine(request.username)
            if not machine:
                # 机器不存在，自动创建新机器（使用用户输入的ID）
                machine = machine_manager.create_machine(
                    MachineCreateRequest(
                        name=f"机器 {request.username}",
                        location="未分配"
                    ),
                    machine_id=request.username
                )
            
            # 生成机器访问token
            token = auth_service.generate_token(machine.id, "machine", machine.name)
            
            # 更新机器状态
            machine_manager.update_machine_status(machine.id, "online")
            
            log_operation(
                username=request.username,
                role="machine",
                action="machine_login",
                target_type="machine",
                target_id=machine.id,
                detail=f"机器登录: {machine.name}",
                ip_address=http_request.client.host if http_request.client else None,
            )
            return ApiResponse(
                code=0,
                message="success",
                data={
                    "token": token,
                    "machine_id": machine.id,
                    "role": "machine",
                    "machine_name": machine.name,
                }
            )
        
        else:
            # 用户登录
            user = auth_service.authenticate(request.username, request.password)
            if not user:
                raise HTTPException(status_code=401, detail="用户名或密码错误")
            
            # 生成token
            token = auth_service.generate_token(user.id, user.role, user.username)
            
            log_operation(
                username=request.username,
                role=user.role,
                action="login",
                detail=f"用户登录: {user.name}",
                ip_address=http_request.client.host if http_request.client else None,
            )
            return ApiResponse(
                code=0,
                message="success",
                data={
                    "token": token,
                    "user": auth_service.get_user_info(request.username).model_dump(),
                    "role": user.role,
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout", response_model=ApiResponse)
async def logout(authorization: str = Header(None)):
    """
    用户登出
    """
    # 简化处理：实际应该将token加入黑名单
    return ApiResponse(code=0, message="success", data={})


@router.get("/logs", response_model=ApiResponse)
async def get_operation_logs(
    authorization: str = Header(None),
    limit: int = 100,
    offset: int = 0,
    username: Optional[str] = None,
    action: Optional[str] = None,
):
    """
    获取操作日志列表（仅管理员）
    """
    require_admin(authorization)
    logs, total = get_logs(limit=limit, offset=offset, username=username, action=action)
    return ApiResponse(
        code=0,
        message="success",
        data={
            "logs": logs,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )


@router.get("/me", response_model=ApiResponse)
async def get_me(authorization: str = Header(None)):
    """
    获取当前登录用户信息
    """
    token_data = verify_token(authorization)
    return ApiResponse(
        code=0,
        message="success",
        data=token_data
    )


# ==================== 用户管理（仅管理员）====================

@router.get("/users", response_model=ApiResponse)
async def get_users(authorization: str = Header(None)):
    """
    获取所有用户列表（仅管理员）
    """
    require_admin(authorization)
    users = auth_service.get_all_users()
    return ApiResponse(
        code=0,
        message="success",
        data=[user.model_dump() for user in users]
    )


@router.post("/users", response_model=ApiResponse)
async def create_user(
    request: CreateUserRequest,
    authorization: str = Header(None),
    http_request: Request = None,
):
    """
    创建新用户（仅管理员）
    """
    require_admin(authorization)
    try:
        user = auth_service.create_user(
            username=request.username,
            password=request.password,
            role=request.role,
            name=request.name,
        )
        log_operation(
            username="admin",
            role="admin",
            action="create_user",
            target_type="user",
            target_id=user.id,
            detail=f"创建用户: {user.username} ({user.name})",
            ip_address=http_request.client.host if http_request and http_request.client else None,
        )
        return ApiResponse(code=0, message="success", data=user.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{username}", response_model=ApiResponse)
async def delete_user(
    username: str,
    authorization: str = Header(None),
    http_request: Request = None,
):
    """
    删除用户（仅管理员）
    """
    require_admin(authorization)
    
    success = auth_service.delete_user(username)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")

    log_operation(
        username="admin",
        role="admin",
        action="delete_user",
        target_type="user",
        target_id=username,
        detail=f"删除用户: {username}",
        ip_address=http_request.client.host if http_request and http_request.client else None,
    )

    return ApiResponse(code=0, message="success", data={})


@router.post("/users/{username}/password", response_model=ApiResponse)
async def update_password(
    username: str,
    request: UpdatePasswordRequest,
    authorization: str = Header(None),
    http_request: Request = None,
):
    """
    修改用户密码（仅管理员）
    """
    require_admin(authorization)
    
    success = auth_service.update_user_password(username, request.new_password)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")

    log_operation(
        username="admin",
        role="admin",
        action="update_password",
        target_type="user",
        target_id=username,
        detail=f"修改密码: {username}",
        ip_address=http_request.client.host if http_request and http_request.client else None,
    )

    return ApiResponse(code=0, message="success", data={})
