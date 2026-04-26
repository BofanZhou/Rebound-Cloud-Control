#!/usr/bin/env python3
"""
回弹云控管理系统 - 统一启动脚本
同时启动后端(FastAPI)和前端(Vite)
用法: python start.py
      或双击 start.bat
"""
import os
import sys
import subprocess
import time
import signal

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

processes = []


def shutdown(signum=None, frame=None):
    """停止所有服务"""
    print("\n[系统] 正在停止所有服务...")
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
    # 等待优雅关闭，超时则强制杀死
    for proc in processes:
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
    print("[系统] 所有服务已停止")
    sys.exit(0)


def main():
    # 注册信号处理 (Ctrl+C)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("=" * 50)
    print("  回弹云控管理系统 V1.0 - 启动脚本")
    print("=" * 50)
    print()

    # 检查目录
    if not os.path.isdir(BACKEND_DIR):
        print(f"[错误] 后端目录不存在: {BACKEND_DIR}")
        sys.exit(1)
    if not os.path.isdir(FRONTEND_DIR):
        print(f"[错误] 前端目录不存在: {FRONTEND_DIR}")
        sys.exit(1)

    # 启动后端
    print("[系统] 正在启动后端服务...")
    python_exe = os.path.join(BACKEND_DIR, "venv313", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable

    backend_proc = subprocess.Popen(
        [python_exe, "main.py"],
        cwd=BACKEND_DIR,
        # 不捕获输出，直接显示在当前窗口
        stdout=None,
        stderr=None,
    )
    processes.append(backend_proc)
    print(f"       后端 PID: {backend_proc.pid}")
    print("       地址: http://localhost:8000")
    print("       API文档: http://localhost:8000/docs")
    print()

    # 等待后端初始化
    time.sleep(2)

    # 启动前端（直接调用 vite.cmd，绕过 PowerShell 执行策略限制）
    print("[系统] 正在启动前端服务...")
    vite_cmd = os.path.join(FRONTEND_DIR, "node_modules", ".bin", "vite.cmd")
    if not os.path.exists(vite_cmd):
        print(f"[错误] 找不到 vite.cmd，请先运行 npm install")
        shutdown()
        return

    frontend_proc = subprocess.Popen(
        [vite_cmd, "--host"],
        cwd=FRONTEND_DIR,
        # 不捕获输出，直接显示在当前窗口
        stdout=None,
        stderr=None,
    )
    processes.append(frontend_proc)
    print(f"       前端 PID: {frontend_proc.pid}")
    print("       地址: http://localhost:5173")
    print()

    # 等待前端初始化
    time.sleep(2)

    print("=" * 50)
    print("  服务启动完成！")
    print("=" * 50)
    print()
    print("访问地址:")
    print("  - 前端页面: http://localhost:5173")
    print("  - 后端 API: http://localhost:8000")
    print("  - API 文档: http://localhost:8000/docs")
    print()
    print("默认账号:")
    print("  管理员:   admin       / admin123")
    print("  维修人员: maintenance / maint123")
    print("  操作员:   operator    / oper123")
    print()
    print("按 Ctrl+C 停止所有服务")
    print()

    # 等待子进程结束
    try:
        while True:
            backend_status = backend_proc.poll()
            frontend_status = frontend_proc.poll()

            if backend_status is not None:
                print(f"[系统] 后端服务异常退出 (code={backend_status})")
                break
            if frontend_status is not None:
                print(f"[系统] 前端服务异常退出 (code={frontend_status})")
                break

            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()


if __name__ == "__main__":
    main()
