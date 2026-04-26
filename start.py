#!/usr/bin/env python3
"""
回弹云控管理系统 —— 一键启动脚本
同时启动后端 (FastAPI) 和前端 (Vite)，并实时显示彩色日志。
"""
import os
import sys
import subprocess
import threading
import time
import signal
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


def check_command(cmd, name):
    """跨平台检测命令是否存在（Windows 下能识别 .cmd/.bat）"""
    if shutil.which(cmd):
        return True
    return False


def check_backend_deps():
    backend_dir = Path(__file__).parent / "backend"
    venv_paths = [
        backend_dir / "venv313" / "Scripts" / "python.exe",
        backend_dir / "venv" / "Scripts" / "python.exe",
        backend_dir / ".." / "venv313" / "Scripts" / "python.exe",
        backend_dir / ".." / "venv" / "Scripts" / "python.exe",
    ]
    for vp in venv_paths:
        if vp.exists():
            return str(vp)
    # fallback to system python
    return sys.executable


def main():
    root = Path(__file__).parent.resolve()
    backend_dir = root / "backend"
    frontend_dir = root / "frontend"

    print("=" * 60)
    print("  回弹云控管理系统 —— 一键启动脚本")
    print("=" * 60)

    # 检查 Python
    if not check_command("python", "Python") and not check_command("python3", "Python"):
        log("启动器", "错误：未检测到 Python，请安装 Python 3.10+", "error")
        sys.exit(1)

    # 检查 Node.js
    if not check_command("npm", "Node.js"):
        log("启动器", "错误：未检测到 Node.js / npm，请安装 Node.js 18+", "error")
        sys.exit(1)

    # 检查前端依赖
    if not (frontend_dir / "node_modules").exists():
        log("启动器", "前端依赖未安装，正在执行 npm install...", "warn")
        ret = subprocess.call(["npm", "install"], cwd=str(frontend_dir), shell=True)
        if ret != 0:
            log("启动器", "前端依赖安装失败，请手动执行 cd frontend && npm install", "error")
            sys.exit(1)

    # 选择 Python 解释器
    python_exe = check_backend_deps()
    log("启动器", f"使用 Python: {python_exe}", "info")

    # 启动后端
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

    # 启动前端
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
            # 检查子进程是否意外退出
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
