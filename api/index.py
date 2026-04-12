"""
Vercel Serverless Function Entry
将 backend 代码包装为 Vercel 可用的入口
"""
import sys
import os
import traceback

# 设置 Vercel 环境变量，使用 /tmp 作为数据目录
os.environ['VERCEL'] = '1'
os.environ['DATA_DIR'] = '/tmp/data'

# 添加 backend 目录到路径
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

try:
    # 导入 FastAPI 应用
    from main import app
    
    # Vercel 需要这个 handler
    from mangum import Mangum
    
    # 包装 FastAPI 应用
    handler = Mangum(app, lifespan="off")
    
except Exception as e:
    # 记录详细的错误信息到 stderr
    error_msg = f"Error initializing app: {str(e)}\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr)
    
    # 创建一个简单的错误应用
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/{path:path}")
    @app.post("/{path:path}")
    @app.put("/{path:path}")
    @app.delete("/{path:path}")
    async def error_handler(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Server initialization failed",
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )
    
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
