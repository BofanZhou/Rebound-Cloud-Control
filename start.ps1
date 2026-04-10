# 钢管回弹智能补偿系统 - PowerShell 启动脚本
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$host.ui.RawUI.WindowTitle = "钢管回弹智能补偿系统 - 启动脚本"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  钢管回弹智能补偿系统 - 启动脚本" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 设置项目路径
$PROJECT_ROOT = $PSScriptRoot
$BACKEND_DIR = Join-Path $PROJECT_ROOT "backend"
$FRONTEND_DIR = Join-Path $PROJECT_ROOT "frontend"

# 检查目录是否存在
if (-not (Test-Path $BACKEND_DIR)) {
    Write-Host "[错误] 后端目录不存在: $BACKEND_DIR" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

if (-not (Test-Path $FRONTEND_DIR)) {
    Write-Host "[错误] 前端目录不存在: $FRONTEND_DIR" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "[1/3] 正在启动后端服务..." -ForegroundColor Yellow
Write-Host "      地址: http://localhost:8000" -ForegroundColor Gray
Write-Host "      API文档: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

# 启动后端服务
$backendProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$BACKEND_DIR'; .\venv313\Scripts\python main.py" -WindowStyle Normal -PassThru

# 等待后端启动
Start-Sleep -Seconds 3

Write-Host "[2/3] 正在启动前端服务..." -ForegroundColor Yellow
Write-Host "      地址: http://localhost:5173" -ForegroundColor Gray
Write-Host ""

# 启动前端服务
$frontendProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$FRONTEND_DIR'; npm run dev" -WindowStyle Normal -PassThru

# 等待前端启动
Start-Sleep -Seconds 3

Write-Host "[3/3] 服务启动完成！" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  访问地址:" -ForegroundColor Cyan
Write-Host "  - 前端页面: http://localhost:5173" -ForegroundColor White
Write-Host "  - 后端API:  http://localhost:8000" -ForegroundColor White
Write-Host "  - API文档:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "默认账号:" -ForegroundColor Yellow
Write-Host "  管理员:     admin / admin123" -ForegroundColor White
Write-Host "  维修人员:   maintenance / maint123" -ForegroundColor White
Write-Host "  操作员:     operator / oper123" -ForegroundColor White
Write-Host ""
Write-Host "按任意键关闭此窗口（服务继续在后台运行）..." -ForegroundColor Gray
[void][System.Console]::ReadKey($true)
