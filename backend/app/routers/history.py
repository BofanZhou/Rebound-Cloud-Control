"""
历史记录路由
GET /api/history
"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from ..models.schemas import ApiResponse
from ..services.machine_manager import machine_manager
from ..utils import get_token_from_header, get_machine_id_from_token

router = APIRouter(prefix="/history", tags=["历史记录"])


@router.get("", response_model=ApiResponse)
async def get_history(
    authorization: str = Header(None),
    machine_id: Optional[str] = Query(None, description="机器ID（可选，优先使用token中的信息）"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数量限制")
):
    """
    获取任务历史记录
    
    返回最近执行的任务记录，包括：
    - 输入参数（管径、壁厚、材质、目标角度）
    - 推荐参数（推荐角度、补偿值、说明）
    - 执行结果（实际角度、偏差、最终状态）
    - 时间戳
    
    参数：
    - limit: 返回记录数量，默认 10，最大 100
    - machine_id: 机器ID，不传则从token中获取
    
    响应示例：
    ```json
    {
        "code": 0,
        "message": "success",
        "data": [
            {
                "id": "TASK-A1B2C3D4",
                "machine_id": "MCH-XXX",
                "input_params": {
                    "diameter": 50,
                    "thickness": 5,
                    "material": "普通钢",
                    "target_angle": 90
                },
                "recommend_params": {
                    "recommended_angle": 92,
                    "recommended_offset": 2,
                    "explanation": "基于普通钢材质的推荐"
                },
                "execute_result": {
                    "actual_angle": 91.85,
                    "deviation": -0.15,
                    "final_status": "completed"
                },
                "created_at": "2024-01-01T12:00:00",
                "completed_at": "2024-01-01T12:00:05"
            }
        ]
    }
    ```
    """
    try:
        # 验证token
        token = get_token_from_header(authorization)
        if not token:
            raise HTTPException(status_code=401, detail="未提供认证信息")
        
        # 获取机器ID
        if machine_id:
            machine = machine_manager.get_machine(machine_id)
            if not machine:
                raise HTTPException(status_code=404, detail="机器不存在")
        else:
            machine_id = get_machine_id_from_token(token)
        
        records = machine_manager.get_history(machine_id, limit=limit)
        
        # 将 Pydantic 模型转换为字典
        data = [record.model_dump() for record in records]
        
        return ApiResponse(
            code=0,
            message="success",
            data=data,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
