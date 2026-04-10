"""
用户认证服务
处理用户登录、权限验证
"""
import os
import json
import uuid
import hashlib
from typing import Dict, Optional
from datetime import datetime, timedelta
from ..models.schemas import User, UserInfo, UserRole


class AuthService:
    """
    用户认证服务
    
    功能：
    - 用户登录验证
    - 简单 token 生成
    - 用户权限管理
    
    注意：此为演示版本，使用简单的内存存储和token机制
    生产环境应使用 JWT 和数据库
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self._users: Dict[str, User] = {}
        self._tokens: Dict[str, dict] = {}  # token -> {user_id, expires}
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 加载用户数据
        self._load_users()
        
        # 如果没有用户，创建默认用户
        if not self._users:
            self._create_default_users()
    
    def _hash_password(self, password: str) -> str:
        """简单密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self):
        """加载用户数据"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_data in data:
                        user = User(**user_data)
                        self._users[user.username] = user
            except Exception as e:
                print(f"加载用户数据失败: {e}")
    
    def _save_users(self):
        """保存用户数据"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            data = [user.model_dump() for user in self._users.values()]
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _create_default_users(self):
        """创建默认用户"""
        default_users = [
            {
                "username": "admin",
                "password": "admin123",
                "role": "admin",
                "name": "系统管理员",
            },
            {
                "username": "maintenance",
                "password": "maint123",
                "role": "maintenance",
                "name": "维修人员",
            },
            {
                "username": "operator",
                "password": "oper123",
                "role": "operator",
                "name": "操作员",
            },
        ]
        
        for user_data in default_users:
            self._create_user(
                username=user_data["username"],
                password=user_data["password"],
                role=user_data["role"],
                name=user_data["name"],
            )
    
    def _create_user(self, username: str, password: str, role: UserRole, name: str) -> User:
        """创建用户"""
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            password=self._hash_password(password),
            role=role,
            name=name,
            created_at=datetime.now().isoformat(),
        )
        self._users[username] = user
        self._save_users()
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        验证用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            验证成功返回 User，失败返回 None
        """
        user = self._users.get(username)
        if not user:
            return None
        
        hashed = self._hash_password(password)
        if user.password == hashed:
            return user
        
        return None
    
    def generate_token(self, user_id: str, role: str) -> str:
        """
        生成访问令牌
        
        Args:
            user_id: 用户ID
            role: 角色
            
        Returns:
            token 字符串
        """
        token = f"tk_{uuid.uuid4().hex}"
        expires = datetime.now() + timedelta(days=7)
        
        self._tokens[token] = {
            "user_id": user_id,
            "role": role,
            "expires": expires.isoformat(),
        }
        
        return token
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        验证 token
        
        Args:
            token: 令牌字符串
            
        Returns:
            验证成功返回用户信息，失败返回 None
        """
        if token not in self._tokens:
            return None
        
        token_data = self._tokens[token]
        expires = datetime.fromisoformat(token_data["expires"])
        
        if datetime.now() > expires:
            del self._tokens[token]
            return None
        
        return token_data
    
    def get_user_info(self, username: str) -> Optional[UserInfo]:
        """获取用户信息（不含密码）"""
        user = self._users.get(username)
        if not user:
            return None
        
        return UserInfo(
            id=user.id,
            username=user.username,
            role=user.role,
            name=user.name,
        )
    
    def get_all_users(self) -> list:
        """获取所有用户信息"""
        return [
            UserInfo(
                id=user.id,
                username=user.username,
                role=user.role,
                name=user.name,
            )
            for user in self._users.values()
        ]
    
    def has_permission(self, token: str, required_roles: list) -> bool:
        """
        检查用户是否有权限
        
        Args:
            token: 访问令牌
            required_roles: 需要的角色列表
            
        Returns:
            是否有权限
        """
        token_data = self.verify_token(token)
        if not token_data:
            return False
        
        return token_data["role"] in required_roles


# 全局认证服务实例
auth_service = AuthService()
