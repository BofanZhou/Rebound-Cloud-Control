"""
用户认证服务
处理用户登录、权限验证
"""
import os
import uuid
import hashlib
from typing import Dict, Optional
from datetime import datetime, timedelta, timezone

from ..models.schemas import User, UserInfo, UserRole
from ..db.database import SessionLocal
from ..db.models import UserDB


class AuthService:
    """
    用户认证服务

    功能：
    - 用户登录验证
    - 简单 token 生成
    - 用户权限管理

    注意：此为演示版本，使用简单的 token 机制
    生产环境应使用 JWT
    """

    def __init__(self):
        self._tokens: Dict[str, dict] = {}  # token -> {user_id, role, expires}
        self._ensure_default_users()

    def _hash_password(self, password: str) -> str:
        """简单密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _ensure_default_users(self):
        """如果没有用户，创建默认用户"""
        db = SessionLocal()
        try:
            count = db.query(UserDB).count()
            if count == 0:
                default_users = [
                    ("admin", "admin123", "admin", "系统管理员"),
                    ("maintenance", "maint123", "maintenance", "维修人员"),
                    ("operator", "oper123", "operator", "操作员"),
                ]
                for username, password, role, name in default_users:
                    user = UserDB(
                        id=str(uuid.uuid4()),
                        username=username,
                        password=self._hash_password(password),
                        role=role,
                        name=name,
                    )
                    db.add(user)
                db.commit()
        finally:
            db.close()

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        验证用户登录
        """
        db = SessionLocal()
        try:
            user_db = db.query(UserDB).filter(UserDB.username == username).first()
            if not user_db:
                return None

            hashed = self._hash_password(password)
            if user_db.password != hashed:
                return None

            return User(
                id=user_db.id,
                username=user_db.username,
                password=user_db.password,
                role=user_db.role,  # type: ignore[arg-type]
                name=user_db.name,
                created_at=user_db.created_at.isoformat(),
            )
        finally:
            db.close()

    def generate_token(self, user_id: str, role: str, username: str = None) -> str:
        """
        生成访问令牌
        """
        token = f"tk_{uuid.uuid4().hex}"
        expires = datetime.now(timezone.utc) + timedelta(days=7)

        self._tokens[token] = {
            "user_id": user_id,
            "username": username or user_id,
            "role": role,
            "expires": expires.isoformat(),
        }

        return token

    def verify_token(self, token: str) -> Optional[dict]:
        """
        验证 token
        """
        if token not in self._tokens:
            return None

        token_data = self._tokens[token]
        expires = datetime.fromisoformat(token_data["expires"])

        if datetime.now(timezone.utc) > expires:
            del self._tokens[token]
            return None

        return token_data

    def get_user_info(self, username: str) -> Optional[UserInfo]:
        """获取用户信息（不含密码）"""
        db = SessionLocal()
        try:
            user_db = db.query(UserDB).filter(UserDB.username == username).first()
            if not user_db:
                return None

            return UserInfo(
                id=user_db.id,
                username=user_db.username,
                role=user_db.role,  # type: ignore[arg-type]
                name=user_db.name,
            )
        finally:
            db.close()

    def get_all_users(self) -> list:
        """获取所有用户信息"""
        db = SessionLocal()
        try:
            users_db = db.query(UserDB).all()
            return [
                UserInfo(
                    id=u.id,
                    username=u.username,
                    role=u.role,  # type: ignore[arg-type]
                    name=u.name,
                )
                for u in users_db
            ]
        finally:
            db.close()

    def has_permission(self, token: str, required_roles: list) -> bool:
        """
        检查用户是否有权限
        """
        token_data = self.verify_token(token)
        if not token_data:
            return False

        return token_data["role"] in required_roles

    def create_user(self, username: str, password: str, role: UserRole, name: str) -> UserInfo:
        """创建新用户（供后续用户管理UI使用）"""
        db = SessionLocal()
        try:
            # 检查用户名是否已存在
            existing = db.query(UserDB).filter(UserDB.username == username).first()
            if existing:
                raise ValueError(f"用户名 '{username}' 已存在")
            user = UserDB(
                id=str(uuid.uuid4()),
                username=username,
                password=self._hash_password(password),
                role=role,
                name=name,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return UserInfo(
                id=user.id,
                username=user.username,
                role=user.role,  # type: ignore[arg-type]
                name=user.name,
            )
        finally:
            db.close()

    def delete_user(self, username: str) -> bool:
        """删除用户（不能删除自己）"""
        db = SessionLocal()
        try:
            user = db.query(UserDB).filter(UserDB.username == username).first()
            if not user:
                return False
            db.delete(user)
            db.commit()
            return True
        finally:
            db.close()

    def update_user_password(self, username: str, new_password: str) -> bool:
        """修改用户密码"""
        db = SessionLocal()
        try:
            user = db.query(UserDB).filter(UserDB.username == username).first()
            if not user:
                return False
            user.password = self._hash_password(new_password)
            db.commit()
            return True
        finally:
            db.close()


# 全局认证服务实例 - 真正延迟加载
_auth_service_instance = None


def get_auth_service():
    global _auth_service_instance
    if _auth_service_instance is None:
        _auth_service_instance = AuthService()
    return _auth_service_instance


# 使用 property 实现真正的延迟访问
class _AuthServiceProxy:
    def __getattr__(self, name):
        return getattr(get_auth_service(), name)


auth_service = _AuthServiceProxy()
