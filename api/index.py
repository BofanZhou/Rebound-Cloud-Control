import os
import sys
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR.parent / 'backend'

os.environ.setdefault('VERCEL', '1')
os.environ.setdefault('USER_DATA_DIR', '/tmp/data')
os.environ.setdefault('MACHINE_DATA_DIR', '/tmp/data/machines')

# Backward-compatible fallback for existing services.
os.environ.setdefault('DATA_DIR', os.environ['USER_DATA_DIR'])

for path in (Path(os.environ['USER_DATA_DIR']), Path(os.environ['MACHINE_DATA_DIR'])):
    path.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BACKEND_DIR))

try:
    from main import app
    from mangum import Mangum

    handler = Mangum(app, lifespan='off')
except Exception as exc:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from mangum import Mangum

    print(f'Failed to initialize app: {exc}')
    print(traceback.format_exc())

    app = FastAPI()

    @app.get('/')
    @app.get('/api/{path:path}')
    async def error_handler(path: str = ''):
        return JSONResponse(
            status_code=500,
            content={
                'code': 500,
                'message': f'Server initialization error: {exc}',
                'data': {},
            },
        )

    handler = Mangum(app, lifespan='off')
