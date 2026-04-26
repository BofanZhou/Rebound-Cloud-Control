# 回弹云控管理系统 —— PowerShell 停止脚本

Write-Host "[信息] 正在停止回弹云控管理系统服务..." -ForegroundColor Cyan

# 停止 Python 后端
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*main.py*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

# 停止 Node 前端
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "[信息] 服务已停止" -ForegroundColor Green
