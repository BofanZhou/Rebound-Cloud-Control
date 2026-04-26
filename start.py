#!/usr/bin/env python3
"""
回弹云控管理系统 —— 一键启动脚本
自动检测并安装缺失依赖，同时启动后端 (FastAPI) 和前端 (Vite)。
"""
import os
import sys
import subprocess
import threading
import time
import shutil
from pathlib import Path

# 颜色代码
COLORS = {
    "backend": "\033[36m",   # 青色
    "frontend": "\033[35m",  # 紫色
    "info": "\033[32m",      # 绿色
    "warn": "\033[33m",      # 黄色
    "error": "\033[31m",     # 红色
    "reset": "\033[0m",
}

procs = []
shutdown_event = threading.Event()


def log(label: str, text: str, level: str = "info"):
    color = COLORS.get(level, COLORS["info"])
    reset = COLORS["reset"]
    timestamp = time.strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] [{label}]{reset} {text}", flush=True)


def stream_output(proc, label, color_key):
    try:
        for line in iter(proc.stdout.readline, b""):
            if not line:
                break
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                log(label, text, color_key)
    except Exception:
        pass


def check_command(cmd):
    """跨平台检测命令是否存在（Windows 下能识别 .cmd/.bat/.exe）"""
    return shutil.which(cmd) is not None


def find_python():
    """查找可用的 Python 解释器，优先虚拟环境"""
    backend_dir = Path(__file__).parent / "backend"
    venv_paths = [
        backend_dir / "venv313" / "Scripts" / "python.exe",
        backend_dir / "venv" / "Scripts" / "python.exe",
        Path(__file__).parent / "venv313" / "Scripts" / "python.exe",
        Path(__file__).parent / "venv" / "Scripts" / "python.exe",
    ]
    for vp in venv_paths:
        if vp.exists():
            return str(vp)
    for cmd in ("python", "python3", "py"):
        if check_command(cmd):
            return cmd
    return None


def run_and_stream(cmd, label, color_key, cwd=None):
    """运行命令并实时输出日志，返回 exit code"""
    log(label, f"执行: {' '.join(str(c) for c in cmd)}", color_key)
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    for line in iter(proc.stdout.readline, b""):
        if not line:
            break
        text = line.decode("utf-8", errors="replace").rstrip()
        if text:
            log(label, text, color_key)
    proc.wait()
    return proc.returncode


def check_backend_installed(python_exe):
    """检测后端核心依赖是否已安装"""
    try:
        subprocess.run(
            [python_exe, "-c", "import fastapi, uvicorn, sqlalchemy"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except Exception:
        return False


def get_python_version(python_exe):
    try:
        result = subprocess.run(
            [python_exe, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True,
        )
        return result.stdout.strip() or result.stderr.strip()
    except Exception:
        return "未知"


def install_backend(python_exe, backend_dir):
    """自动安装后端依赖"""
    req_file = backend_dir / "requirements.txt"
    if not req_file.exists():
        log("启动器", f"找不到依赖文件: {req_file}", "error")
        return False

    log("启动器", "后端核心依赖缺失，正在自动安装...", "warn")
    log("启动器", f"Python 版本: {get_python_version(python_exe)}", "info")
    log("启动器", "首次安装约需 1~5 分钟，请耐心等待...", "warn")

    # 先尝试升级 pip（避免旧版 pip 导致安装失败）
    log("启动器", "正在检查 pip 版本...", "info")
    run_and_stream(
        [python_exe, "-m", "pip", "install", "--upgrade", "pip", "-q"],
        "pip", "info"
    )

    mirrors = [
        ("清华源", ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "--trusted-host", "pypi.tuna.tsinghua.edu.cn"]),
        ("阿里云", ["-i", "https://mirrors.aliyun.com/pypi/simple/", "--trusted-host", "mirrors.aliyun.com"]),
        ("官方源", []),
    ]

    for name, extra_args in mirrors:
        log("启动器", f"尝试使用 {name} 安装依赖...", "info")
        cmd = [python_exe, "-m", "pip", "install", "-r", str(req_file)] + extra_args
        ret = run_and_stream(cmd, "pip", "info")

        if ret == 0:
            log("启动器", f"使用 {name} 安装成功", "info")
            break
        else:
            log("启动器", f"使用 {name} 安装失败，尝试下一个源...", "warn")
    else:
        log("启动器", "所有镜像源均安装失败，请检查网络或代理设置", "error")
        log("启动器", f"手动安装命令: cd backend && {python_exe} -m pip install -r requirements.txt", "error")
        return False

    # 安装完成后再次验证
    if not check_backend_installed(python_exe):
        log("启动器", "依赖安装后验证失败，可能部分包未正确安装", "error")
        return False

    log("启动器", "后端依赖安装完成并通过验证", "info")
    return True


def install_frontend(frontend_dir):
    """自动安装前端依赖"""
    log("启动器", "前端依赖未安装，正在执行 npm install...", "warn")
    ret = run_and_stream(["npm", "install"], "npm", "info", cwd=str(frontend_dir))
    if ret != 0:
        log("启动器", "前端依赖安装失败，请手动执行 cd frontend && npm install", "error")
        return False
    log("启动器", "前端依赖安装完成", "info")
    return True


def main():
    root = Path(__file__).parent.resolve()
    backend_dir = root / "backend"
    frontend_dir = root / "frontend"

    print("=" * 60)
    print("  回弹云控管理系统 —— 一键启动脚本")
    print("=" * 60)

    # 1. 检查 Python
    python_exe = find_python()
    if not python_exe:
        log("启动器", "错误：未检测到 Python，请安装 Python 3.10+", "error")
        sys.exit(1)
    log("启动器", f"使用 Python: {python_exe}", "info")

    # 2. 检查 Node.js
    if not check_command("npm"):
        log("启动器", "错误：未检测到 Node.js / npm，请安装 Node.js 18+", "error")
        sys.exit(1)

    # 3. 检查并安装后端依赖
    log("启动器", "正在检查后端的 Python 依赖...", "info")
    if not check_backend_installed(python_exe):
        if not install_backend(python_exe, backend_dir):
            sys.exit(1)
    else:
        log("启动器", "后端依赖已就绪", "info")

    # 4. 检查并安装前端依赖
    if not (frontend_dir / "node_modules").exists():
        if not install_frontend(frontend_dir):
            sys.exit(1)
    else:
        log("启动器", "前端依赖已就绪", "info")

    # 5. 启动后端
    log("启动器", "正在启动后端服务 (FastAPI) ...", "info")
    backend_proc = subprocess.Popen(
        [python_exe, "main.py"],
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    procs.append(backend_proc)
    backend_thread = threading.Thread(target=stream_output, args=(backend_proc, "后端", "backend"))
    backend_thread.daemon = True
    backend_thread.start()

    # 等待后端就绪
    time.sleep(2)

    # 6. 启动前端
    log("启动器", "正在启动前端服务 (Vite) ...", "info")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )
    procs.append(frontend_proc)
    frontend_thread = threading.Thread(target=stream_output, args=(frontend_proc, "前端", "frontend"))
    frontend_thread.daemon = True
    frontend_thread.start()

    log("启动器", "系统启动完成！", "info")
    log("启动器", "前端地址: http://localhost:5173", "info")
    log("启动器", "后端地址: http://localhost:8000", "info")
    log("启动器", "API 文档: http://localhost:8000/docs", "info")
    log("启动器", "按 Ctrl+C 停止服务", "warn")

    # 等待退出
    try:
        while not shutdown_event.is_set():
            time.sleep(0.5)
            for p in procs:
                if p.poll() is not None:
                    time.sleep(1)
                    if p.poll() is not None:
                        log("启动器", f"子进程已退出 (code={p.returncode})", "warn")
                        shutdown_event.set()
                        break
    except KeyboardInterrupt:
        log("启动器", "收到退出信号，正在停止服务...", "warn")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
        log("启动器", "服务已停止", "info")
        sys.exit(0)


if __name__ == "__main__":
    main()
