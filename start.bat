@echo off
chcp 65001 >nul
title 回弹云控管理系统 - 环境检测与启动

setlocal EnableDelayedExpansion

echo.
echo  ============================================
echo    回弹云控管理系统 - 环境检测
echo  ============================================
echo.

set "PYTHON_OK=0"
set "NODE_OK=0"
set "PIP_OK=0"
set "NPM_OK=0"
set "BACKEND_DEPS_OK=0"
set "FRONTEND_DEPS_OK=0"
set "MISSING_COUNT=0"

REM ---- 检测 Python ----
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%a in ('python --version 2^>^&1') do set "PYTHON_VER=%%a"
    echo  [✓] Python  ................ !PYTHON_VER!
    set "PYTHON_OK=1"
) else (
    echo  [✗] Python  ................ 未检测到
    set /a MISSING_COUNT+=1
)

REM ---- 检测 pip ----
python -m pip --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%a in ('python -m pip --version 2^>^&1') do set "PIP_VER=%%a"
    echo  [✓] pip     ................ 已安装
    set "PIP_OK=1"
) else (
    echo  [✗] pip     ................ 未检测到
    set /a MISSING_COUNT+=1
)

REM ---- 检测 Node.js ----
node --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%a in ('node --version 2^>^&1') do set "NODE_VER=%%a"
    echo  [✓] Node.js ................ !NODE_VER!
    set "NODE_OK=1"
) else (
    echo  [✗] Node.js ................ 未检测到
    set /a MISSING_COUNT+=1
)

REM ---- 检测 npm ----
npm --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%a in ('npm --version 2^>^&1') do set "NPM_VER=%%a"
    echo  [✓] npm     ................ v!NPM_VER!
    set "NPM_OK=1"
) else (
    echo  [✗] npm     ................ 未检测到
    set /a MISSING_COUNT+=1
)

REM ---- 检测后端依赖 ----
if !PYTHON_OK! equ 1 (
    python -c "import fastapi, uvicorn, sqlalchemy" >nul 2>&1
    if !errorlevel! equ 0 (
        echo  [✓] 后端依赖 ............... 已安装
        set "BACKEND_DEPS_OK=1"
    ) else (
        echo  [✗] 后端依赖 ............... 未安装 (将自动安装)
    )
) else (
    echo  [-] 后端依赖 ............... 跳过 (未检测到 Python)
)

REM ---- 检测前端依赖 ----
if exist "frontend\node_modules" (
    echo  [✓] 前端依赖 ............... 已安装
    set "FRONTEND_DEPS_OK=1"
) else (
    echo  [✗] 前端依赖 ............... 未安装 (将自动安装)
)

echo.
echo  ============================================

if !MISSING_COUNT! gtr 0 (
    echo.
    echo  [错误] 检测到 !MISSING_COUNT! 项环境缺失，请先安装：
    echo.
    if !PYTHON_OK! equ 0 (
        echo    - Python 3.10+  ............ 项目目录下有 python-*.exe 安装包
    )
    if !NODE_OK! equ 0 (
        echo    - Node.js 18+   ............ 项目目录下有 node-*.msi 安装包
    )
    echo.
    echo  安装完成后，重新运行本脚本即可启动。
    echo.
    echo  也可以手动安装：
    echo    1. 双击项目目录下的 python-*.exe 安装 Python
    echo    2. 双击项目目录下的 node-*.msi 安装 Node.js
    echo    3. 安装时勾选 "Add to PATH" 选项
    echo.
    pause
    exit /b 1
)

echo  [通过] 环境检测全部通过，正在启动系统...
echo.

cd /d "%~dp0"
python start.py
