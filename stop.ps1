# 回弹云控管理系统 - PowerShell 停止脚本
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$host.ui.RawUI.WindowTitle = "回弹云控管理系统 - 停止脚本"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  回弹云控管理系统 - 停止脚本" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 停止后端 (python main.py)
Write-Host "[1/2] 正在停止后端服务..." -ForegroundColor Yellow
$backendProcesses = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like "*main.py*" }
if ($backendProcesses) {
    foreach ($proc in $backendProcesses) {
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Write-Host "      后端服务已停止" -ForegroundColor Green
} else {
    Write-Host "      后端服务未运行或已停止" -ForegroundColor Gray
}

# 停止前端 (vite)
Write-Host "[2/2] 正在停止前端服务..." -ForegroundColor Yellow
$frontendProcesses = Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -like "*vite*" }
if ($frontendProcesses) {
    foreach ($proc in $frontendProcesses) {
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Write-Host "      前端服务已停止" -ForegroundColor Green
} else {
    Write-Host "      前端服务未运行或已停止" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  所有服务已停止" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "按回车键退出"
