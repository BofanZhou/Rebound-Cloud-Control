"""
Vercel Serverless Function Entry
将 backend 代码包装为 Vercel 可用的入口
"""
import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# 导入 FastAPI 应用
from main import app

# Vercel 需要这个 handler
from mangum import Mangum

# 包装 FastAPI 应用
handler = Mangum(app, lifespan="off")
