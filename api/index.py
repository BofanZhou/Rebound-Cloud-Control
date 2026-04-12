import sys
import os

os.environ['VERCEL'] = '1'
os.environ['DATA_DIR'] = '/tmp/data'

backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")
