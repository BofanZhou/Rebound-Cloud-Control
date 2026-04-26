@echo off
setlocal EnableDelayedExpansion

title 回弹云控管理系统 - 环境检测与启动

set "PYTHON_OK=0"
set "NODE_OK=0"
set "PIP_OK=0"
set "NPM_OK=0"
set "BACKEND_DEPS_OK=0"
set "FRONTEND_DEPS_OK=0"
set "MISSING_COUNT=0"
set "PYTHON_VER=未知"
set "NODE_VER=未知"

echo.
echo  ============================================
echo    回弹云控管理系统 - 环境检测
echo  ============================================
echo.

REM ---- 检测 Python ----
python --version >nul 2>nul
if errorlevel 1 (
    echo   [FAIL] Python  ................ 未检测到
    set /a MISSING_COUNT+=1
) else (
    for /f "tokens=*" %%a in ('python --version 2^>nul') do set "PYTHON_VER=%%a"
    echo   [OK]   Python  ................ %PYTHON_VER%
    set "PYTHON_OK=1"
)

REM ---- 检测 pip ----
if %PYTHON_OK%==1 (
    python -m pip --version >nul 2>nul
    if errorlevel 1 (
        echo   [FAIL] pip     ................ 未检测到
        set /a MISSING_COUNT+=1
    ) else (
        echo   [OK]   pip     ................ 已安装
        set "PIP_OK=1"
    )
) else (
    echo   [SKIP] pip     ................ (未检测到 Python)
)

REM ---- 检测 Node.js ----
node --version >nul 2>nul
if errorlevel 1 (
    echo   [FAIL] Node.js ................ 未检测到
    set /a MISSING_COUNT+=1
) else (
    for /f "tokens=*" %%a in ('node --version 2^>nul') do set "NODE_VER=%%a"
    echo   [OK]   Node.js ................ %NODE_VER%
    set "NODE_OK=1"
)

REM ---- 检测 npm ----
if %NODE_OK%==1 (
    npm --version >nul 2>nul
    if errorlevel 1 (
        echo   [FAIL] npm     ................ 未检测到
        set /a MISSING_COUNT+=1
    ) else (
        echo   [OK]   npm     ................ 已安装
        set "NPM_OK=1"
    )
) else (
    echo   [SKIP] npm     ................ (未检测到 Node.js)
)

REM ---- 检测后端依赖 ----
if %PYTHON_OK%==1 (
    python -c "import fastapi, uvicorn, sqlalchemy" >nul 2>nul
    if errorlevel 1 (
        echo   [FAIL] 后端依赖 ............... 未安装 (将自动安装)
    ) else (
        echo   [OK]   后端依赖 ............... 已安装
        set "BACKEND_DEPS_OK=1"
    )
) else (
    echo   [SKIP] 后端依赖 ............... (未检测到 Python)
)

REM ---- 检测前端依赖 ----
if exist "frontend\node_modules" (
    echo   [OK]   前端依赖 ............... 已安装
    set "FRONTEND_DEPS_OK=1"
) else (
    echo   [FAIL] 前端依赖 ............... 未安装 (将自动安装)
)

echo.
echo  ============================================

if %MISSING_COUNT% gtr 0 (
    echo.
    echo   [错误] 检测到 %MISSING_COUNT% 项环境缺失，请先安装：
    echo.
    if %PYTHON_OK%==0 (
        echo      - Python 3.10+  : 项目目录下有 python-*.exe 安装包
    )
    if %NODE_OK%==0 (
        echo      - Node.js 18+   : 项目目录下有 node-*.msi 安装包
    )
    echo.
    echo   安装完成后，重新运行本脚本即可启动。
    echo.
    echo   安装提示：
    echo      1. 双击 python-*.exe 安装 Python（勾选 "Add Python to PATH"）
    echo      2. 双击 node-*.msi 安装 Node.js
    echo      3. 安装完成后关闭本窗口，重新双击 start.bat
    echo.
    pause
    exit /b 1
)

echo   [通过] 环境检测全部通过，正在启动系统...
echo.

cd /d "%~dp0"
python start.py

REM 如果 start.py 异常退出，暂停显示错误
echo.
echo   系统已停止运行。
pause
