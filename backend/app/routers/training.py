"""
模型训练路由
POST /training/upload           - 上传 CSV 并立即解析缓存
GET  /training/status           - 获取训练状态与结果
POST /training/start            - 启动训练（使用缓存的解析数据）
POST /training/predict          - 单次预测
POST /training/predict-iterative - 迭代预测
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from ..models.schemas import ApiResponse
from ..services.training import (
    training_state, parse_csv, start_training,
    predict_one, predict_iterative,
)

router = APIRouter(prefix="/training", tags=["模型训练"])


@router.post("/upload", response_model=ApiResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """上传 CSV 训练数据集

    CSV 格式:
    material,diameter,thickness,target_angle,result
    普通钢,50,5,90,0
    高强钢,60,8,45,1
    不锈钢,40,3,30,2

    result: 0=角度偏小, 1=角度合适, 2=角度偏大
    """
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="仅支持 CSV 文件")

    try:
        content = (await file.read()).decode('utf-8-sig')
    except UnicodeDecodeError:
        try:
            content = (await file.read()).decode('gbk')
        except Exception:
            raise HTTPException(status_code=400, detail="无法解码文件，请使用 UTF-8 编码")

    records = parse_csv(content)
    if len(records) < 10:
        raise HTTPException(status_code=400, detail=f"有效记录不足 ({len(records)} 条)，至少需要 10 条")

    training_state.set_records(records)
    training_state.message = f"数据集加载成功，共 {len(records)} 条记录"

    return ApiResponse(
        code=0,
        message="success",
        data={"count": len(records), "sample": records[:5]},
    )


@router.get("/status", response_model=ApiResponse)
async def get_training_status():
    """获取训练状态、损失曲线、准确率、混淆矩阵"""
    return ApiResponse(code=0, message="success", data=training_state.to_dict())


@router.post("/start", response_model=ApiResponse)
async def start_training_api(
    epochs: int = Form(80),
    batch_size: int = Form(32),
    learning_rate: float = Form(0.001),
):
    """启动训练（使用已缓存的数据集）"""
    if training_state.is_training:
        raise HTTPException(status_code=400, detail="训练正在进行中")

    records = training_state.get_records()
    if len(records) < 10:
        raise HTTPException(status_code=400, detail="请先上传数据集")

    ok = start_training(records, epochs=epochs, batch_size=batch_size, lr=learning_rate)
    if not ok:
        raise HTTPException(status_code=400, detail="无法启动训练")

    return ApiResponse(code=0, message="success", data={"message": "训练已启动", "epochs": epochs})


@router.post("/predict", response_model=ApiResponse)
async def predict(
    material: str = Form(...),
    diameter: float = Form(..., ge=10, le=500),
    thickness: float = Form(..., ge=1, le=50),
    target_angle: float = Form(..., ge=0, le=180),
):
    """单次预测"""
    result = predict_one(material, diameter, thickness, target_angle)
    return ApiResponse(code=0, message="success", data=result)


@router.post("/predict-iterative", response_model=ApiResponse)
async def predict_iterative_api(
    material: str = Form(...),
    diameter: float = Form(..., ge=10, le=500),
    thickness: float = Form(..., ge=1, le=50),
    target_angle: float = Form(..., ge=0, le=180),
    max_iterations: int = Form(20),
    step: float = Form(0.5),
):
    """迭代预测 —— 自动调整角度直到模型输出'角度合适'"""
    result = predict_iterative(material, diameter, thickness, target_angle, max_iterations, step)
    return ApiResponse(code=0, message="success", data=result)
