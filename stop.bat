@echo off
chcp 65001 >nul
title 回弹云控管理系统 - 停止脚本

echo [信息] 正在停止回弹云控管理系统服务...

REM 停止 Python 后端进程
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *main.py*" >nul 2>&1
taskkill /F /IM python.exe /FI "COMMANDLINE eq *main.py*" >nul 2>&1

REM 停止 Node 前端进程
taskkill /F /IM node.exe >nul 2>&1

echo [信息] 服务已停止
pause
