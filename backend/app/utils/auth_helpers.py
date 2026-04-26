"""
共享认证辅助函数

所有路由器共用这些函数，避免代码重复。
"""
from typing import Optional
from fastapi import HTTPException
from ..services.auth import auth_service
from ..services.machine_manager import machine_manager


def get_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """从 Authorization 请求头中提取 Bearer token"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.replace("Bearer ", "")


def verify_token(authorization: Optional[str]) -> dict:
    """验证 token 并返回 payload，未验证抛出 401"""
    token = get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="未提供认证信息")
    token_data = auth_service.verify_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="未登录或token已过期")
    return token_data


def require_admin(authorization: Optional[str]) -> None:
    """验证当前用户为管理员，否则抛出 403"""
    token = get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="未提供认证信息")
    if not auth_service.has_permission(token, ["admin"]):
        raise HTTPException(status_code=403, detail="无权限访问")


def get_machine_id_from_token(token: str) -> str:
    """从 token payload 中提取机器 ID"""
    token_data = auth_service.verify_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="token无效或已过期")

    role = token_data.get("role", "")

    if role == "machine":
        return token_data.get("user_id", "")

    if ":machine:" in role:
        return role.split(":machine:")[1]

    machines = machine_manager.get_all_machines()
    if machines:
        return machines[0].id

    raise HTTPException(status_code=400, detail="未选择机器")
