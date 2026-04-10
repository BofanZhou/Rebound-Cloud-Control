@echo off
chcp 65001 >nul
title 钢管回弹智能补偿系统 - 停止脚本

echo ============================================
echo   钢管回弹智能补偿系统 - 停止脚本
echo ============================================
echo.

echo [1/2] 正在停止后端服务...
taskkill /FI "WINDOWTITLE eq 后端服务 - 钢管回弹系统*" /F >nul 2>&1
if %errorlevel% == 0 (
    echo       后端服务已停止
) else (
    echo       后端服务未运行或已停止
)

echo [2/2] 正在停止前端服务...
taskkill /FI "WINDOWTITLE eq 前端服务 - 钢管回弹系统*" /F >nul 2>&1
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
