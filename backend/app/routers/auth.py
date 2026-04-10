"""
用户认证路由
POST /api/auth/login
POST /api/auth/logout
GET /api/auth/me
"""
from fastapi import APIRouter, HTTPException, Header
from ..models.schemas import ApiResponse, LoginRequest, LoginResponse, UserInfo, MachineCreateRequest
from ..services.auth import auth_service
from ..services.machine_manager import machine_manager

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=ApiResponse)
async def login(request: LoginRequest):
    """
    用户登录
    
    支持两种登录方式：
    - machine: 机器登录，直接输入机器ID
    - user: 用户登录，输入用户名密码
    
    请求示例：
    ```json
    {
        "username": "admin",
        "password": "admin123",
        "login_type": "user"
    }
    ```
    
    响应示例：
    ```json
    {
        "code": 0,
        "message": "success",
        "data": {
            "token": "tk_xxx",
            "user": {
                "id": "xxx",
                "username": "admin",
                "role": "admin",
                "name": "系统管理员"
            },
            "role": "admin"
        }
    }
    ```
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
            token = auth_service.generate_token(machine.id, "machine")
            
            # 更新机器状态
            machine_manager.update_machine_status(machine.id, "online")
            
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
            token = auth_service.generate_token(user.id, user.role)
            
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
    
    请求头：
    - Authorization: Bearer token
    """
    # 简化处理：实际应该将token加入黑名单
    return ApiResponse(code=0, message="success", data={})


@router.get("/me", response_model=ApiResponse)
async def get_me(authorization: str = Header(None)):
    """
    获取当前登录用户信息
    
    请求头：
    - Authorization: Bearer token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证信息")
    
    token = authorization.replace("Bearer ", "")
    token_data = auth_service.verify_token(token)
    
    if not token_data:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    
    return ApiResponse(
        code=0,
        message="success",
        data=token_data
    )


@router.get("/users", response_model=ApiResponse)
async def get_users(authorization: str = Header(None)):
    """
    获取所有用户列表（仅管理员）
    
    请求头：
    - Authorization: Bearer token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证信息")
    
    token = authorization.replace("Bearer ", "")
    
    # 检查权限
    if not auth_service.has_permission(token, ["admin"]):
        raise HTTPException(status_code=403, detail="无权限访问")
    
    users = auth_service.get_all_users()
    
    return ApiResponse(
        code=0,
        message="success",
        data=[user.model_dump() for user in users]
    )
