from fastapi import FastAPI
from mangum import Mangum
import sys
import os

# 设置 Vercel 环境变量，使用 /tmp 作为数据目录
os.environ['VERCEL'] = '1'
os.environ['DATA_DIR'] = '/tmp/data'

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# 导入 FastAPI 应用
from main import app

# Vercel Serverless Function 需要这个 handler
handler = Mangum(app, lifespan="off")
