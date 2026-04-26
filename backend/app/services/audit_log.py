"""
操作日志审计服务
记录所有关键操作到数据库
"""
from datetime import datetime, timezone
from typing import Optional
from ..db.database import SessionLocal
from ..db.models import OperationLogDB


def log_operation(
    username: str,
    role: str,
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    detail: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> None:
    """
    记录一条操作日志

    Args:
        username: 操作用户名
        role: 用户角色
        action: 操作类型（如 login, logout, create_machine, delete_user 等）
        target_type: 操作对象类型（如 machine, user, task）
        target_id: 操作对象ID
        detail: 详细描述
        ip_address: IP地址
    """
    db = SessionLocal()
    try:
        log = OperationLogDB(
            timestamp=datetime.now(timezone.utc),
            username=username,
            role=role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            ip_address=ip_address,
        )
        db.add(log)
        db.commit()
    except Exception:
        # 日志记录失败不应影响主业务
        pass
    finally:
        db.close()


def get_logs(
    limit: int = 100,
    offset: int = 0,
    username: Optional[str] = None,
    action: Optional[str] = None,
) -> list:
    """
    获取操作日志列表

    Args:
        limit: 返回数量限制
        offset: 分页偏移
        username: 按用户名筛选
        action: 按操作类型筛选
    """
    db = SessionLocal()
    try:
        query = db.query(OperationLogDB).order_by(OperationLogDB.timestamp.desc())

        if username:
            query = query.filter(OperationLogDB.username == username)
        if action:
            query = query.filter(OperationLogDB.action == action)

        total = query.count()
        logs = query.offset(offset).limit(limit).all()

        return [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "username": log.username,
                "role": log.role,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "detail": log.detail,
                "ip_address": log.ip_address,
            }
            for log in logs
        ], total
    finally:
        db.close()
