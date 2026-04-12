"""
Vercel Serverless Functions entry point for the backend API.
"""
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

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
)

APP_VERSION = "0.2.1"
APP_NAME = "Steel Pipe Springback Compensation API"

app = FastAPI(
    title=APP_NAME,
    description="Prototype with multi-machine management and authentication",
    version=APP_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

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


# Note: In Vercel, the /api prefix is already handled by the routing
# So we don't add /api prefix here
app.include_router(recommend_router, prefix="")
app.include_router(device_router, prefix="")
app.include_router(history_router, prefix="")
app.include_router(auth_router, prefix="")
app.include_router(machines_router, prefix="")


@app.get("/")
async def root():
    return {
        "code": 0,
        "message": "success",
        "data": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "status": "running",
            "docs": "/api/docs",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "code": 0,
        "message": "success",
        "data": {"status": "healthy"},
    }


# Vercel Serverless Function handler
from mangum import Mangum
handler = Mangum(app, lifespan="off")
