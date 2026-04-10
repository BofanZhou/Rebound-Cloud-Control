"""
参数推荐路由
POST /api/recommend
"""
from fastapi import APIRouter, HTTPException
from ..models.schemas import ApiResponse, RecommendRequest, RecommendResult
from ..services.rule_engine import RuleEngine

router = APIRouter(prefix="/recommend", tags=["推荐参数"])


@router.post("", response_model=ApiResponse)
async def recommend(params: RecommendRequest):
    """
    获取推荐参数
    
    根据输入的管径、壁厚、材质和目标角度，
    使用规则引擎计算推荐补偿值。
    
    请求示例：
    ```json
    {
        "diameter": 50,
        "thickness": 5,
        "material": "普通钢",
        "target_angle": 90
    }
    ```
    
    响应示例：
    ```json
    {
        "code": 0,
        "message": "success",
        "data": {
            "recommended_angle": 92.0,
            "recommended_offset": 2.0,
            "explanation": "基于普通钢材质，基础补偿值为+2.0°。综合补偿值为+2.00°",
            "timestamp": "2024-01-01T12:00:00"
        }
    }
    ```
    """
    try:
        result = RuleEngine.calculate_recommendation(
            diameter=params.diameter,
            thickness=params.thickness,
            material=params.material,
            target_angle=params.target_angle,
        )
        
        return ApiResponse(
            code=0,
            message="success",
            data=result,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
