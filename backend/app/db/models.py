"""
SQLAlchemy ORM models.
Kept in sync with Pydantic schemas but separated to avoid coupling.
"""
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class UserDB(Base):
    """用户表"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)


class MachineDB(Base):
    """机器表"""
    __tablename__ = "machines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="online", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    # Relationship: one machine -> many history records
    history_records: Mapped[list["HistoryRecordDB"]] = relationship(
        back_populates="machine",
        cascade="all, delete-orphan",
        order_by="HistoryRecordDB.created_at.desc()",
    )


class OperationLogDB(Base):
    """操作日志表"""
    __tablename__ = "operation_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=now_utc, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    detail: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)


class HistoryRecordDB(Base):
    """历史记录表"""
    __tablename__ = "history_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    machine_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Input params
    diameter: Mapped[float] = mapped_column(Float, nullable=False)
    thickness: Mapped[float] = mapped_column(Float, nullable=False)
    material: Mapped[str] = mapped_column(String(50), nullable=False)
    target_angle: Mapped[float] = mapped_column(Float, nullable=False)

    # Recommendation params
    recommended_angle: Mapped[float] = mapped_column(Float, nullable=False)
    recommended_offset: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    # Execution result (nullable until task completes)
    actual_angle: Mapped[float | None] = mapped_column(Float, nullable=True)
    deviation: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_status: Mapped[str | None] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    machine: Mapped["MachineDB"] = relationship(back_populates="history_records")
