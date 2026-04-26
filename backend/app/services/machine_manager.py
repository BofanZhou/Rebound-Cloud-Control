"""
机器管理器
管理多台机器的状态和数据隔离（基于数据库）
"""
import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone

from ..models.schemas import Machine, MachineCreateRequest, HistoryRecord, InputParams, RecommendParams, ExecuteResult
from ..db.database import SessionLocal
from ..db.models import MachineDB, HistoryRecordDB
from .device_simulator import DeviceSimulator


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MachineManager:
    """
    机器管理器

    功能：
    - 管理多台机器的注册、查询（数据库持久化）
    - 每台机器有独立的模拟器实例（内存）
    - 历史记录通过数据库存储和查询
    """

    def __init__(self):
        self._simulators: Dict[str, DeviceSimulator] = {}

        # 加载已有机器并创建模拟器
        self._load_machines()

        # 如果没有机器，创建默认机器
        if not self._simulators:
            self._create_default_machine()

    def _load_machines(self):
        """从数据库加载所有机器并创建模拟器"""
        db = SessionLocal()
        try:
            machines_db = db.query(MachineDB).all()
            for m in machines_db:
                self._simulators[m.id] = DeviceSimulator(
                    machine_id=m.id,
                    on_complete_callback=self._on_task_complete,
                    on_state_change_callback=self._on_state_change,
                )
        finally:
            db.close()

    def _create_default_machine(self):
        """创建默认机器"""
        self.create_machine(MachineCreateRequest(
            name="默认机器",
            location="车间A-001"
        ))

    def _on_state_change(self, machine_id: str, state):
        """
        状态变化回调：广播到所有 WebSocket 客户端
        """
        try:
            # 延迟导入避免循环依赖
            from ..routers.websocket import broadcast_state
            broadcast_state(machine_id, state.model_dump())
        except Exception:
            pass

    def _on_task_complete(self, machine_id: str, task_id: str, actual_angle: float,
                          deviation: float, final_status: str):
        """
        任务完成回调：更新历史记录中的执行结果
        """
        db = SessionLocal()
        try:
            record = db.query(HistoryRecordDB).filter(
                HistoryRecordDB.machine_id == machine_id,
                HistoryRecordDB.task_id == task_id,
            ).first()
            if record:
                record.actual_angle = actual_angle
                record.deviation = deviation
                record.final_status = final_status
                record.completed_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()

    def create_machine(self, request: MachineCreateRequest, machine_id: str = None) -> Machine:
        """创建新机器"""
        if machine_id is None:
            machine_id = f"MCH-{uuid.uuid4().hex[:8].upper()}"

        now = datetime.now(timezone.utc)
        db = SessionLocal()
        try:
            machine_db = MachineDB(
                id=machine_id,
                name=request.name,
                location=request.location,
                status="online",
                created_at=now,
                last_active=now,
            )
            db.add(machine_db)
            db.commit()
            db.refresh(machine_db)

            # 创建模拟器
            self._simulators[machine_id] = DeviceSimulator(
                machine_id=machine_id,
                on_complete_callback=self._on_task_complete,
                on_state_change_callback=self._on_state_change,
            )

            return Machine(
                id=machine_db.id,
                name=machine_db.name,
                location=machine_db.location,
                status=machine_db.status,  # type: ignore[arg-type]
                created_at=machine_db.created_at.isoformat(),
                last_active=machine_db.last_active.isoformat(),
            )
        finally:
            db.close()

    def get_machine(self, machine_id: str) -> Optional[Machine]:
        """获取机器信息"""
        db = SessionLocal()
        try:
            m = db.query(MachineDB).filter(MachineDB.id == machine_id).first()
            if not m:
                return None
            return Machine(
                id=m.id,
                name=m.name,
                location=m.location,
                status=m.status,  # type: ignore[arg-type]
                created_at=m.created_at.isoformat(),
                last_active=m.last_active.isoformat(),
            )
        finally:
            db.close()

    def get_all_machines(self) -> List[Machine]:
        """获取所有机器列表"""
        db = SessionLocal()
        try:
            machines_db = db.query(MachineDB).all()
            return [
                Machine(
                    id=m.id,
                    name=m.name,
                    location=m.location,
                    status=m.status,  # type: ignore[arg-type]
                    created_at=m.created_at.isoformat(),
                    last_active=m.last_active.isoformat(),
                )
                for m in machines_db
            ]
        finally:
            db.close()

    def update_machine_status(self, machine_id: str, status: str):
        """更新机器状态"""
        db = SessionLocal()
        try:
            m = db.query(MachineDB).filter(MachineDB.id == machine_id).first()
            if m:
                m.status = status
                m.last_active = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()

    def update_machine(self, machine_id: str, name: str | None = None, location: str | None = None) -> Machine | None:
        """更新机器信息"""
        db = SessionLocal()
        try:
            m = db.query(MachineDB).filter(MachineDB.id == machine_id).first()
            if not m:
                return None
            if name is not None:
                m.name = name
            if location is not None:
                m.location = location
            m.last_active = datetime.now(timezone.utc)
            db.commit()
            db.refresh(m)
            return Machine(
                id=m.id,
                name=m.name,
                location=m.location,
                status=m.status,  # type: ignore[arg-type]
                created_at=m.created_at.isoformat(),
                last_active=m.last_active.isoformat(),
            )
        finally:
            db.close()

    def delete_machine(self, machine_id: str) -> bool:
        """删除机器及其历史记录"""
        db = SessionLocal()
        try:
            m = db.query(MachineDB).filter(MachineDB.id == machine_id).first()
            if not m:
                return False
            db.delete(m)
            db.commit()
            # 移除内存中的模拟器
            if machine_id in self._simulators:
                sim = self._simulators[machine_id]
                sim.reset()
                del self._simulators[machine_id]
            return True
        finally:
            db.close()

    def get_simulator(self, machine_id: str) -> Optional[DeviceSimulator]:
        """获取机器的模拟器"""
        return self._simulators.get(machine_id)

    def add_history(self, machine_id: str, record: HistoryRecord):
        """添加历史记录到数据库"""
        db = SessionLocal()
        try:
            record_db = HistoryRecordDB(
                id=record.id,
                machine_id=record.machine_id,
                task_id=record.id,  # 复用 record id 作为 task_id
                diameter=record.input_params.diameter,
                thickness=record.input_params.thickness,
                material=record.input_params.material,
                target_angle=record.input_params.target_angle,
                recommended_angle=record.recommend_params.recommended_angle,
                recommended_offset=record.recommend_params.recommended_offset,
                explanation=record.recommend_params.explanation,
                actual_angle=record.execute_result.actual_angle if record.execute_result else None,
                deviation=record.execute_result.deviation if record.execute_result else None,
                final_status=record.execute_result.final_status if record.execute_result else None,
                created_at=datetime.fromisoformat(record.created_at),
                completed_at=datetime.fromisoformat(record.completed_at) if record.completed_at else None,
            )
            db.add(record_db)
            db.commit()
        finally:
            db.close()

    def get_history(self, machine_id: str, limit: int = 10) -> List[HistoryRecord]:
        """获取机器历史记录（从数据库）"""
        db = SessionLocal()
        try:
            records_db = db.query(HistoryRecordDB).filter(
                HistoryRecordDB.machine_id == machine_id
            ).order_by(HistoryRecordDB.created_at.desc()).limit(limit).all()

            return [
                HistoryRecord(
                    id=r.id,
                    machine_id=r.machine_id,
                    input_params=InputParams(
                        diameter=r.diameter,
                        thickness=r.thickness,
                        material=r.material,
                        target_angle=r.target_angle,
                    ),
                    recommend_params=RecommendParams(
                        recommended_angle=r.recommended_angle,
                        recommended_offset=r.recommended_offset,
                        explanation=r.explanation,
                    ),
                    execute_result=ExecuteResult(
                        actual_angle=r.actual_angle,
                        deviation=r.deviation,
                        final_status=r.final_status,  # type: ignore[arg-type]
                    ) if r.final_status else None,
                    created_at=r.created_at.isoformat(),
                    completed_at=r.completed_at.isoformat() if r.completed_at else None,
                )
                for r in records_db
            ]
        finally:
            db.close()


# 全局机器管理器实例 - 真正延迟加载
_machine_manager_instance = None


def get_machine_manager():
    global _machine_manager_instance
    if _machine_manager_instance is None:
        _machine_manager_instance = MachineManager()
    return _machine_manager_instance


# 使用 property 实现真正的延迟访问
class _MachineManagerProxy:
    def __getattr__(self, name):
        return getattr(get_machine_manager(), name)


machine_manager = _MachineManagerProxy()
