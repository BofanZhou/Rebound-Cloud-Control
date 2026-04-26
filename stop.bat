@echo off
chcp 65001 >nul
title 回弹云控管理系统 - 停止脚本

echo ============================================
echo   回弹云控管理系统 - 停止脚本
echo ============================================
echo.

echo [1/2] 正在停止后端服务...
taskkill /F /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE like *main.py*" >nul 2>&1
if %errorlevel% == 0 (
    echo       后端服务已停止
) else (
    echo       后端服务未运行或已停止
)

echo [2/2] 正在停止前端服务...
taskkill /F /FI "IMAGENAME eq node.exe" /FI "COMMANDLINE like *vite*" >nul 2>&1
if %errorlevel% == 0 (
    echo       前端服务已停止
) else (
    echo       前端服务未运行或已停止
)

echo.
echo ============================================
echo   所有服务已停止
echo ============================================
echo.
pause
