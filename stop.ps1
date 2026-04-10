# 钢管回弹智能补偿系统 - PowerShell 停止脚本
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$host.ui.RawUI.WindowTitle = "钢管回弹智能补偿系统 - 停止脚本"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  钢管回弹智能补偿系统 - 停止脚本" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] 正在停止后端服务..." -ForegroundColor Yellow
$backendProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
if ($backendProcesses) {
    $backendProcesses | Stop-Process -Force
    Write-Host "      后端服务已停止" -ForegroundColor Green
} else {
    Write-Host "      后端服务未运行或已停止" -ForegroundColor Gray
}

Write-Host "[2/2] 正在停止前端服务..." -ForegroundColor Yellow
$frontendProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*vite*" }
if ($frontendProcesses) {
    $frontendProcesses | Stop-Process -Force
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
