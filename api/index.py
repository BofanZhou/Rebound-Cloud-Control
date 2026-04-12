"""
Vercel Serverless Function Entry
"""
import sys
import os

# 设置 Vercel 环境变量
os.environ['VERCEL'] = '1'
os.environ['DATA_DIR'] = '/tmp/data'

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# 懒加载：延迟导入，避免冷启动时的问题
_app = None

def get_app():
    global _app
    if _app is None:
        from main import app
        _app = app
    return _app

# 创建延迟加载的 handler
class LazyHandler:
    def __init__(self):
        self._handler = None
    
    async def __call__(self, scope, receive, send):
        if self._handler is None:
            from mangum import Mangum
            app = get_app()
            self._handler = Mangum(app, lifespan="off")
        return await self._handler(scope, receive, send)

handler = LazyHandler()
