"""
Steel pipe springback compensation system backend service.
"""
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import (
    recommend_router,
    device_router,
    history_router,
    auth_router,
    machines_router,
    websocket_router,
    training_router,
)
from app.db import init_db

APP_VERSION = "0.2.1"
APP_NAME = "Steel Pipe Springback Compensation API"

app = FastAPI(
    title=APP_NAME,
    description="Prototype with multi-machine management and authentication",
    version=APP_VERSION,
)


@app.on_event("startup")
async def startup_event():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": message, "data": {}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "validation failed",
            "data": {"errors": exc.errors()},
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, _exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "internal server error", "data": {}},
    )


app.include_router(recommend_router, prefix="/api")
app.include_router(device_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(machines_router, prefix="/api")
app.include_router(training_router, prefix="/api")
app.include_router(websocket_router)

# Vercel rewrite behavior can vary by project settings.
# Register non-/api paths as compatibility fallback.
app.include_router(recommend_router)
app.include_router(device_router)
app.include_router(history_router)
app.include_router(auth_router)
app.include_router(machines_router)
app.include_router(training_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {
        "code": 0,
        "message": "success",
        "data": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "status": "running",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "code": 0,
        "message": "success",
        "data": {"status": "healthy"},
    }


if __name__ == "__main__":
    import uvicorn

    # Hot reload is useful for manual development, but the launcher should
    # default to a single stable process on new deployment machines.
    reload_enabled = os.environ.get("REBOUND_RELOAD", "0") == "1"
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload_enabled,
        log_level="info",
    )
