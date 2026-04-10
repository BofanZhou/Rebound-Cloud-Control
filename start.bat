@echo off
chcp 65001 >nul
title 钢管回弹智能补偿系统 - 启动脚本

echo ============================================
echo   钢管回弹智能补偿系统 - 启动脚本
echo ============================================
echo.

REM 设置项目路径
set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"

REM 检查目录是否存在
if not exist "%BACKEND_DIR%" (
    echo [错误] 后端目录不存在: %BACKEND_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo [错误] 前端目录不存在: %FRONTEND_DIR%
    pause
    exit /b 1
)

echo [1/3] 正在启动后端服务...
echo       地址: http://localhost:8000
echo       API文档: http://localhost:8000/docs
echo.

REM 启动后端服务（在新窗口）
start "后端服务 - 钢管回弹系统" cmd /k "cd /d "%BACKEND_DIR%" && .\venv313\Scripts\python main.py"

REM 等待后端启动
timeout /t 3 /nobreak >nul

echo [2/3] 正在启动前端服务...
echo       地址: http://localhost:5173
echo.

REM 启动前端服务（在新窗口）
start "前端服务 - 钢管回弹系统" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"

REM 等待前端启动
timeout /t 3 /nobreak >nul

echo [3/3] 服务启动完成！
echo.
echo ============================================
echo   访问地址:
echo   - 前端页面: http://localhost:5173
echo   - 后端API:  http://localhost:8000
echo   - API文档:  http://localhost:8000/docs
echo ============================================
echo.
echo 默认账号:
echo   管理员:     admin / admin123
echo   维修人员:   maintenance / maint123
echo   操作员:     operator / oper123
echo.
echo 按任意键关闭此窗口（服务继续在后台运行）
pause >nul
