"""
机器管理器
管理多台机器的状态和数据隔离
"""
import os
import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from ..models.schemas import Machine, MachineCreateRequest, HistoryRecord
from .device_simulator import DeviceSimulator


class MachineManager:
    """
    机器管理器
    
    功能：
    - 管理多台机器的注册、查询
    - 每台机器有独立的存储空间
    - 维护机器状态
    """
    
    def __init__(self, data_dir: str = "data/machines"):
        self.data_dir = data_dir
        self._machines: Dict[str, Machine] = {}
        self._simulators: Dict[str, DeviceSimulator] = {}
        self._history: Dict[str, List[HistoryRecord]] = {}
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 加载已有机器数据
        self._load_machines()
        
        # 如果没有机器，创建默认机器
        if not self._machines:
            self._create_default_machine()
    
    def _get_machine_dir(self, machine_id: str) -> str:
        """获取机器数据目录"""
        return os.path.join(self.data_dir, machine_id)
    
    def _get_machine_file(self, machine_id: str) -> str:
        """获取机器信息文件路径"""
        return os.path.join(self._get_machine_dir(machine_id), "machine.json")
    
    def _get_history_file(self, machine_id: str) -> str:
        """获取历史记录文件路径"""
        return os.path.join(self._get_machine_dir(machine_id), "history.json")
    
    def _load_machines(self):
        """加载所有机器信息"""
        if not os.path.exists(self.data_dir):
            return
        
        for machine_id in os.listdir(self.data_dir):
            machine_dir = self._get_machine_dir(machine_id)
            machine_file = os.path.join(machine_dir, "machine.json")
            
            if os.path.exists(machine_file):
                try:
                    with open(machine_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        machine = Machine(**data)
                        self._machines[machine_id] = machine
                        
                        # 为每台机器创建模拟器
                        self._simulators[machine_id] = DeviceSimulator(machine_id)
                        
                        # 加载历史记录
                        self._load_history(machine_id)
                        
                except Exception as e:
                    print(f"加载机器 {machine_id} 失败: {e}")
    
    def _load_history(self, machine_id: str):
        """加载机器历史记录"""
        history_file = self._get_history_file(machine_id)
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history[machine_id] = [HistoryRecord(**record) for record in data]
            except Exception as e:
                print(f"加载历史记录 {machine_id} 失败: {e}")
                self._history[machine_id] = []
        else:
            self._history[machine_id] = []
    
    def _save_machine(self, machine: Machine):
        """保存机器信息到文件"""
        machine_dir = self._get_machine_dir(machine.id)
        os.makedirs(machine_dir, exist_ok=True)
        
        machine_file = self._get_machine_file(machine.id)
        with open(machine_file, 'w', encoding='utf-8') as f:
            json.dump(machine.model_dump(), f, ensure_ascii=False, indent=2)
    
    def _save_history(self, machine_id: str):
        """保存历史记录到文件"""
        if machine_id not in self._history:
            return
        
        history_file = self._get_history_file(machine_id)
        with open(history_file, 'w', encoding='utf-8') as f:
            data = [record.model_dump() for record in self._history[machine_id]]
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _create_default_machine(self):
        """创建默认机器"""
        self.create_machine(MachineCreateRequest(
            name="默认机器",
            location="车间A-001"
        ))
    
    def create_machine(self, request: MachineCreateRequest, machine_id: str = None) -> Machine:
        """创建新机器"""
        if machine_id is None:
            machine_id = f"MCH-{uuid.uuid4().hex[:8].upper()}"
        
        now = datetime.now().isoformat()
        machine = Machine(
            id=machine_id,
            name=request.name,
            location=request.location,
            status="online",
            created_at=now,
            last_active=now,
        )
        
        self._machines[machine_id] = machine
        self._simulators[machine_id] = DeviceSimulator(machine_id)
        self._history[machine_id] = []
        
        self._save_machine(machine)
        
        return machine
    
    def get_machine(self, machine_id: str) -> Optional[Machine]:
        """获取机器信息"""
        return self._machines.get(machine_id)
    
    def get_all_machines(self) -> List[Machine]:
        """获取所有机器列表"""
        return list(self._machines.values())
    
    def update_machine_status(self, machine_id: str, status: str):
        """更新机器状态"""
        if machine_id in self._machines:
            self._machines[machine_id].status = status
            self._machines[machine_id].last_active = datetime.now().isoformat()
            self._save_machine(self._machines[machine_id])
    
    def get_simulator(self, machine_id: str) -> Optional[DeviceSimulator]:
        """获取机器的模拟器"""
        return self._simulators.get(machine_id)
    
    def add_history(self, machine_id: str, record: HistoryRecord):
        """添加历史记录"""
        if machine_id not in self._history:
            self._history[machine_id] = []
        
        self._history[machine_id].insert(0, record)
        self._save_history(machine_id)
    
    def get_history(self, machine_id: str, limit: int = 10) -> List[HistoryRecord]:
        """获取机器历史记录"""
        if machine_id not in self._history:
            return []
        return self._history[machine_id][:limit]
    
    def update_history_record(self, machine_id: str, record: HistoryRecord):
        """更新历史记录"""
        if machine_id not in self._history:
            return
        
        for i, r in enumerate(self._history[machine_id]):
            if r.id == record.id:
                self._history[machine_id][i] = record
                self._save_history(machine_id)
                break


# 全局机器管理器实例 - 真正延迟加载
_machine_manager_instance = None

def get_machine_manager():
    global _machine_manager_instance
    if _machine_manager_instance is None:
        _data_dir = os.environ.get('DATA_DIR', 'data/machines')
        _machine_manager_instance = MachineManager(data_dir=_data_dir)
    return _machine_manager_instance

# 使用 property 实现真正的延迟访问
class _MachineManagerProxy:
    def __getattr__(self, name):
        return getattr(get_machine_manager(), name)

machine_manager = _MachineManagerProxy()
