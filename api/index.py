"""
Vercel Serverless Functions entry point for the backend API.
Imports the main FastAPI app from backend/ and wraps with Mangum.
"""
import os
import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Vercel serverless filesystem is read-only except /tmp.
# Force data paths to writable temp directories.
os.environ.setdefault("VERCEL", "1")
os.environ.setdefault("USER_DATA_DIR", "/tmp/data")
os.environ.setdefault("MACHINE_DATA_DIR", "/tmp/data/machines")
os.environ.setdefault("DATA_DIR", os.environ["USER_DATA_DIR"])

Path(os.environ["USER_DATA_DIR"]).mkdir(parents=True, exist_ok=True)
Path(os.environ["MACHINE_DATA_DIR"]).mkdir(parents=True, exist_ok=True)

from main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")
