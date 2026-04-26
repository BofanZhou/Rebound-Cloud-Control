@echo off

title 回弹云控管理系统 - 环境检测与启动

echo.
echo  ============================================
echo    回弹云控管理系统 - 环境检测
echo  ============================================
echo.

set MISSING=0

REM ---- 检测 Python ----
python --version >nul 2>nul
if errorlevel 1 goto PYTHON_MISSING
echo   [OK]   Python  ................ 已安装
goto PYTHON_DONE
:PYTHON_MISSING
echo   [FAIL] Python  ................ 未安装
echo          请双击目录下的 python-*.exe 进行安装
echo          安装时务必勾选 "Add Python to PATH"
set MISSING=1
:PYTHON_DONE

REM ---- 检测 Node.js ----
node --version >nul 2>nul
if errorlevel 1 goto NODE_MISSING
echo   [OK]   Node.js ................ 已安装
goto NODE_DONE
:NODE_MISSING
echo   [FAIL] Node.js ................ 未安装
echo          请双击目录下的 node-*.msi 进行安装
set MISSING=1
:NODE_DONE

echo.
echo  ============================================

if %MISSING%==1 (
    echo.
    echo   [错误] 环境检测未通过，请按上方提示安装缺失项。
    echo          安装完成后，重新双击本脚本即可启动。
    echo.
    pause
    exit /b 1
)

echo   [通过] 环境检测全部通过，正在启动系统...
echo.

cd /d "%~dp0"
python start.py

REM 如果 start.py 退出，暂停显示
echo.
echo   系统已停止运行，按任意键关闭窗口。
pause >nul
