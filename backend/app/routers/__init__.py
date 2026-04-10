# Routers package
from .recommend import router as recommend_router
from .device import router as device_router
from .history import router as history_router
from .auth import router as auth_router
from .machines import router as machines_router

__all__ = [
    "recommend_router", 
    "device_router", 
    "history_router",
    "auth_router",
    "machines_router",
]
