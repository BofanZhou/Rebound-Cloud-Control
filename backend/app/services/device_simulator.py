"""
设备模拟器
模拟设备的状态流转和任务执行
"""
import asyncio
import uuid
import random
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..models.schemas import DeviceState, DeviceStatus, HistoryRecord, InputParams, RecommendParams, ExecuteResult


class DeviceSimulator:
    """
    设备状态模拟器
    
    状态流转：
    - offline -> idle: 设备上线
    - idle -> running: 开始任务
    - running -> completed: 任务完成
    - running -> error: 任务失败
    - any -> offline: 设备离线
    
    模拟逻辑：
    - 提交任务后进入 running 状态
    - 模拟 3-8 秒后自动完成
    - 实际角度 = 设定角度 ± 随机误差
    """
    
    def __init__(self, machine_id: str = "SIM-001"):
        self.machine_id = machine_id
        self.device_id = f"DEV-{machine_id}"
        self._status: DeviceStatus = "idle"
        self._online = True
        self._current_task: Optional[str] = None
        self._current_angle: float = 0.0
        self._actual_angle: float = 0.0
        self._deviation: float = 0.0
        self._last_heartbeat = datetime.now()
        
        # 任务执行中的标记
        self._running_task: Optional[asyncio.Task] = None
    
    @property
    def state(self) -> DeviceState:
        """获取当前设备状态"""
        self._update_heartbeat()
        return DeviceState(
            device_id=self.device_id,
            device_status=self._status,
            online=self._online,
            current_task=self._current_task,
            current_angle=self._current_angle,
            actual_angle=self._actual_angle,
            deviation=self._deviation,
            last_heartbeat=self._last_heartbeat.isoformat(),
        )
    
    def _update_heartbeat(self):
        """更新心跳时间"""
        self._last_heartbeat = datetime.now()
    
    async def submit_task(
        self,
        diameter: float,
        thickness: float,
        material: str,
        target_angle: float,
        recommended_angle: float,
        recommended_offset: float,
    ) -> Dict[str, str]:
        """
        提交任务
        
        Args:
            diameter: 管径
            thickness: 壁厚
            material: 材质
            target_angle: 目标角度
            recommended_angle: 推荐角度
            recommended_offset: 推荐补偿值
            
        Returns:
            任务信息
        """
        # 检查设备状态
        if not self._online:
            raise ValueError("设备离线，无法提交任务")
        
        if self._status == "running":
            raise ValueError("设备正在执行任务，请等待完成")
        
        # 生成任务ID
        task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
        
        # 启动任务执行
        self._current_task = task_id
        self._current_angle = recommended_angle
        self._status = "running"
        
        # 异步执行任务
        self._running_task = asyncio.create_task(
            self._execute_task(task_id, recommended_angle)
        )
        
        return {
            "task_id": task_id,
            "status": "running",
            "message": f"任务 {task_id} 已开始执行",
        }
    
    async def _execute_task(self, task_id: str, target_angle: float):
        """
        执行任务（异步）
        
        模拟执行过程：
        1. 模拟 3-8 秒执行时间
        2. 计算实际角度（加入随机误差）
        3. 计算偏差
        4. 更新历史记录
        """
        try:
            # 模拟执行时间（3-8秒）
            execution_time = random.uniform(3, 8)
            await asyncio.sleep(execution_time)
            
            # 模拟实际角度误差（±0.5度范围内）
            # 误差与壁厚、材质有关，这里简化处理
            error = random.uniform(-0.5, 0.5)
            self._actual_angle = target_angle + error
            self._deviation = error
            
            # 更新状态为完成
            self._status = "completed"
            
        except asyncio.CancelledError:
            # 任务被取消
            self._status = "error"
        except Exception:
            # 任务执行出错
            self._status = "error"
    
    def reset(self):
        """重置设备状态"""
        if self._running_task and not self._running_task.done():
            self._running_task.cancel()
        
        self._status = "idle"
        self._current_task = None
        self._current_angle = 0.0
        self._actual_angle = 0.0
        self._deviation = 0.0
        self._running_task = None
    
    def set_online(self, online: bool):
        """设置设备在线状态"""
        self._online = online
        if not online:
            self._status = "offline"
        elif self._status == "offline":
            self._status = "idle"
