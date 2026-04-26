# 回弹云控管理系统 —— PowerShell 一键启动脚本
# 同时启动后端 (FastAPI) 和前端 (Vite)

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"

function Write-Log($Label, $Message, $Color = "White") {
    $Time = Get-Date -Format "HH:mm:ss"
    Write-Host "[$Time] [$Label] $Message" -ForegroundColor $Color
}

# 检查 Python
$PythonCmd = $null
foreach ($cmd in @("python", "python3")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $PythonCmd = $cmd
        break
    }
}
if (-not $PythonCmd) {
    Write-Log "启动器" "错误：未检测到 Python，请安装 Python 3.10+" "Red"
    exit 1
}

# 检查 Node.js
if (-not (Get-Command "npm" -ErrorAction SilentlyContinue)) {
    Write-Log "启动器" "错误：未检测到 Node.js / npm，请安装 Node.js 18+" "Red"
    exit 1
}

# 检查前端依赖
if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Log "启动器" "前端依赖未安装，正在执行 npm install..." "Yellow"
    Set-Location $FrontendDir
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Log "启动器" "前端依赖安装失败" "Red"
        exit 1
    }
    Set-Location $RootDir
}

# 查找 Python 解释器（优先虚拟环境）
$PythonExe = $PythonCmd
$VenvPaths = @(
    (Join-Path $BackendDir "venv313\Scripts\python.exe"),
    (Join-Path $BackendDir "venv\Scripts\python.exe"),
    (Join-Path $RootDir "venv313\Scripts\python.exe"),
    (Join-Path $RootDir "venv\Scripts\python.exe")
)
foreach ($vp in $VenvPaths) {
    if (Test-Path $vp) {
        $PythonExe = $vp
        break
    }
}

Write-Log "启动器" "========================================" "Green"
Write-Log "启动器" "  回弹云控管理系统 —— 一键启动" "Green"
Write-Log "启动器" "========================================" "Green"
Write-Log "启动器" "使用 Python: $PythonExe" "Cyan"

# 启动后端
Write-Log "启动器" "正在启动后端服务 (FastAPI) ..." "Cyan"
$BackendProc = Start-Process -FilePath $PythonExe -ArgumentList "main.py" -WorkingDirectory $BackendDir -PassThru -NoNewWindow -RedirectStandardOutput (Join-Path $env:TEMP "rc_backend.log")

Start-Sleep -Seconds 2

# 启动前端
Write-Log "启动器" "正在启动前端服务 (Vite) ..." "Magenta"
$FrontendProc = Start-Process -FilePath "npm" -ArgumentList "run","dev" -WorkingDirectory $FrontendDir -PassThru -NoNewWindow -RedirectStandardOutput (Join-Path $env:TEMP "rc_frontend.log")

Write-Log "启动器" "系统启动完成！" "Green"
Write-Log "启动器" "前端地址: http://localhost:5173" "Green"
Write-Log "启动器" "后端地址: http://localhost:8000" "Green"
Write-Log "启动器" "API 文档: http://localhost:8000/docs" "Green"
Write-Log "启动器" "按 Ctrl+C 停止服务" "Yellow"

# 实时输出日志（后台任务）
$LogJobs = @()
$LogJobs += Start-Job -ScriptBlock {
    param($Path, $Label, $Color)
    while ($true) {
        if (Test-Path $Path) {
            Get-Content $Path -Wait -Tail 0 | ForEach-Object {
                $t = Get-Date -Format "HH:mm:ss"
                Write-Host "[$t] [$Label] $_" -ForegroundColor $Color
            }
        }
        Start-Sleep -Seconds 1
    }
} -ArgumentList (Join-Path $env:TEMP "rc_backend.log"), "后端", "Cyan"

$LogJobs += Start-Job -ScriptBlock {
    param($Path, $Label, $Color)
    while ($true) {
        if (Test-Path $Path) {
            Get-Content $Path -Wait -Tail 0 | ForEach-Object {
                $t = Get-Date -Format "HH:mm:ss"
                Write-Host "[$t] [$Label] $_" -ForegroundColor $Color
            }
        }
        Start-Sleep -Seconds 1
    }
} -ArgumentList (Join-Path $env:TEMP "rc_frontend.log"), "前端", "Magenta"

# 等待退出
try {
    while ($true) {
        Start-Sleep -Seconds 1
        if ($BackendProc.HasExited -or $FrontendProc.HasExited) {
            Write-Log "启动器" "子进程已退出，正在停止..." "Yellow"
            break
        }
    }
} finally {
    Write-Log "启动器" "正在停止服务..." "Yellow"
    Stop-Process -Id $BackendProc.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $FrontendProc.Id -Force -ErrorAction SilentlyContinue
    $LogJobs | Stop-Job -ErrorAction SilentlyContinue
    $LogJobs | Remove-Job -ErrorAction SilentlyContinue
    Write-Log "启动器" "服务已停止" "Green"
}
