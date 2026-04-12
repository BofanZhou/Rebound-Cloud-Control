import sys
import os

# 设置环境变量
os.environ['VERCEL'] = '1'
os.environ['DATA_DIR'] = '/tmp/data'

# 确保数据目录存在
try:
    os.makedirs('/tmp/data', exist_ok=True)
    os.makedirs('/tmp/data/machines', exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create data directories: {e}")

# 添加 backend 到路径
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# 添加当前目录到路径（用于导入 app）
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 延迟导入 main，确保路径设置完成
try:
    from main import app
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except Exception as e:
    import traceback
    error_msg = f"Failed to initialize app: {str(e)}\n{traceback.format_exc()}"
    print(error_msg)
    
    # 创建一个简单的错误处理应用
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/")
    @app.get("/api/{path:path}")
    async def error_handler(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": f"Server initialization error: {str(e)}", "data": None}
        )
    
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
