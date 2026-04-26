@echo off
chcp 65001 >nul
title 回弹云控管理系统 - 启动脚本

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 找不到 Python，请确保 Python 已安装并添加到 PATH
    pause
    exit /b 1
)

REM 使用 Python 统一启动脚本（在一个窗口中显示前后端日志）
cd /d "%~dp0"
python start.py
