# 回弹云控管理系统 —— PowerShell 一键启动脚本
# 同时启动后端 (FastAPI) 和前端 (Vite)

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$LocalVenvDir = Join-Path $BackendDir ".venv_local"

function Write-Log($Label, $Message, $Color = "White") {
    $Time = Get-Date -Format "HH:mm:ss"
    Write-Host "[$Time] [$Label] $Message" -ForegroundColor $Color
}

function Test-VenvPython($PythonPath) {
    if (-not (Test-Path $PythonPath)) {
        return $false
    }

    $VenvDir = Split-Path -Parent (Split-Path -Parent $PythonPath)
    $CfgPath = Join-Path $VenvDir "pyvenv.cfg"
    if (-not (Test-Path $CfgPath)) {
        return $false
    }

    $Cfg = @{}
    Get-Content $CfgPath | ForEach-Object {
        if ($_ -match "=") {
            $parts = $_ -split "=", 2
            $Cfg[$parts[0].Trim().ToLower()] = $parts[1].Trim()
        }
    }

    if ($Cfg.ContainsKey("executable") -and -not (Test-Path $Cfg["executable"])) {
        Write-Log "启动器" "跳过不可移植虚拟环境: $PythonPath" "Yellow"
        return $false
    }

    if ($Cfg.ContainsKey("home") -and -not (Test-Path $Cfg["home"])) {
        Write-Log "启动器" "跳过不可移植虚拟环境: $PythonPath" "Yellow"
        return $false
    }

    try {
        & $PythonPath --version *> $null
        return ($LASTEXITCODE -eq 0)
    } catch {
        Write-Log "启动器" "虚拟环境无法运行: $PythonPath" "Yellow"
        return $false
    }
}

function Test-BackendDependencies($PythonExe) {
    try {
        & $PythonExe -c "import fastapi, uvicorn, sqlalchemy" *> $null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Ensure-LocalBackendVenv($PythonCmd) {
    $LocalPython = Join-Path $LocalVenvDir "Scripts\python.exe"
    if (Test-VenvPython $LocalPython) {
        return $LocalPython
    }

    Write-Log "启动器" "正在创建本机后端虚拟环境..." "Yellow"
    $Args = @("-m", "venv", $LocalVenvDir)
    if (Test-Path $LocalVenvDir) {
        $Args = @("-m", "venv", "--clear", $LocalVenvDir)
    }
    & $PythonCmd @Args
    if ($LASTEXITCODE -ne 0) {
        Write-Log "启动器" "创建后端虚拟环境失败" "Red"
        return $null
    }

    if (-not (Test-VenvPython $LocalPython)) {
        Write-Log "启动器" "新建的虚拟环境不可用" "Red"
        return $null
    }

    return $LocalPython
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
$PythonExe = $null
$VenvPaths = @(
    (Join-Path $BackendDir ".venv_local\Scripts\python.exe"),
    (Join-Path $BackendDir "venv313\Scripts\python.exe"),
    (Join-Path $BackendDir "venv\Scripts\python.exe"),
    (Join-Path $RootDir ".venv_local\Scripts\python.exe"),
    (Join-Path $RootDir "venv313\Scripts\python.exe"),
    (Join-Path $RootDir "venv\Scripts\python.exe")
)
foreach ($vp in $VenvPaths) {
    if (Test-VenvPython $vp) {
        $PythonExe = $vp
        break
    }
}

if (-not $PythonExe) {
    $PythonExe = Ensure-LocalBackendVenv $PythonCmd
}

if (-not $PythonExe) {
    $PythonExe = $PythonCmd
}

if (-not (Test-BackendDependencies $PythonExe)) {
    Write-Log "启动器" "后端依赖未安装，正在执行 pip install..." "Yellow"
    & $PythonExe -m pip install --upgrade pip
    & $PythonExe -m pip install -r (Join-Path $BackendDir "requirements.txt")
    if ($LASTEXITCODE -ne 0) {
        Write-Log "启动器" "后端依赖安装失败" "Red"
        exit 1
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
