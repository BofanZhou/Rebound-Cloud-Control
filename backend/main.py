"""
钢管回弹智能补偿系统 - 后端服务
FastAPI 主入口

启动命令：
    uvicorn main:app --reload --port 8000

或：
    python main.py
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    recommend_router, 
    device_router, 
    history_router,
    auth_router,
    machines_router,
)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="钢管回弹智能补偿系统 API",
    description="多机管理版本 - 支持机器登录和用户登录",
    version="0.2.0",
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(recommend_router, prefix="/api")
app.include_router(device_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(machines_router, prefix="/api")


@app.get("/")
async def root():
    """根路径，返回服务信息"""
    return {
        "name": "钢管回弹智能补偿系统 API",
        "version": "0.2.0",
        "status": "running",
        "docs": "/docs",
        "features": [
            "多机管理",
            "用户认证",
            "机器登录",
            "维修/管理模式",
        ]
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # 直接运行此文件启动服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
