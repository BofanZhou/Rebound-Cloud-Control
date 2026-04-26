"""
WebSocket 实时设备状态推送
ws://localhost:8000/ws/device/{machine_id}
"""
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

from ..services.machine_manager import machine_manager

router = APIRouter(tags=["WebSocket"])

# Global connection manager: machine_id -> set of active WebSockets
_connection_manager: Dict[str, Set[WebSocket]] = {}


def _get_connections(machine_id: str) -> Set[WebSocket]:
    """获取指定机器的所有 WebSocket 连接"""
    return _connection_manager.setdefault(machine_id, set())


def broadcast_state(machine_id: str, state_dict: dict):
    """
    向所有订阅了该机器的 WebSocket 客户端广播状态变化
    由 machine_manager 在设备状态变化时调用
    """
    connections = _get_connections(machine_id)
    if not connections:
        return

    # 使用 asyncio.create_task 异步发送，避免阻塞
    disconnected = set()
    for ws in connections:
        try:
            # WebSocket.send_json 是同步的但在 asyncio 环境中可用
            asyncio.create_task(ws.send_json({
                "type": "state_update",
                "machine_id": machine_id,
                "data": state_dict,
            }))
        except Exception:
            disconnected.add(ws)

    # 清理已断开的连接
    for ws in disconnected:
        connections.discard(ws)


@router.websocket("/ws/device/{machine_id}")
async def device_websocket(websocket: WebSocket, machine_id: str):
    """
    WebSocket 连接：实时接收指定设备的状态变化

    连接后自动发送当前状态，之后每当设备状态变化时主动推送。
    """
    await websocket.accept()

    # 验证机器存在
    machine = machine_manager.get_machine(machine_id)
    if not machine:
        await websocket.send_json({
            "type": "error",
            "message": f"机器 {machine_id} 不存在",
        })
        await websocket.close(code=4004)
        return

    # 注册连接
    connections = _get_connections(machine_id)
    connections.add(websocket)

    try:
        # 立即发送当前状态
        simulator = machine_manager.get_simulator(machine_id)
        if simulator:
            await websocket.send_json({
                "type": "state_update",
                "machine_id": machine_id,
                "data": simulator.state.model_dump(),
            })

        # 保持连接，处理客户端消息（如 ping）
        while True:
            message = await websocket.receive_text()
            # 简单处理客户端心跳
            if message == "ping":
                await websocket.send_json({"type": "pong"})
            elif message == "reset":
                # 支持远程重置设备
                if simulator:
                    simulator.reset()

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        connections.discard(websocket)
