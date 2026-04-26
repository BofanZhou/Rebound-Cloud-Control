@echo off
setlocal EnableExtensions

title Rebound Cloud Control - Launcher

set "ROOT=%~dp0"
set "EXIT_CODE=0"
set "MISSING=0"
set "PYTHON_EXE="

pushd "%ROOT%" >nul 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Cannot enter project directory:
    echo         "%ROOT%"
    set "EXIT_CODE=1"
    goto END
)

echo.
echo ============================================
echo   Rebound Cloud Control - Environment Check
echo ============================================
echo.

where python >nul 2>nul
if not errorlevel 1 set "PYTHON_EXE=python"

if not defined PYTHON_EXE (
    where py >nul 2>nul
    if not errorlevel 1 set "PYTHON_EXE=py"
)

if defined PYTHON_EXE (
    echo [OK]   Python is installed.
) else (
    echo [FAIL] Python is not installed or not in PATH.
    echo        Install python-*.exe and enable "Add Python to PATH".
    set "MISSING=1"
)

where npm >nul 2>nul
if not errorlevel 1 (
    echo [OK]   Node.js/npm is installed.
) else (
    echo [FAIL] Node.js/npm is not installed or not in PATH.
    echo        Install node-*.msi and reopen this script.
    set "MISSING=1"
)

if not exist "%ROOT%start.py" (
    echo [FAIL] start.py is missing.
    set "MISSING=1"
)

echo.
echo ============================================

if "%MISSING%"=="1" (
    echo.
    echo [ERROR] Environment check failed. Install missing dependencies first.
    set "EXIT_CODE=1"
    goto END
)

echo [OK] Environment check passed. Starting system...
echo.

if /I "%PYTHON_EXE%"=="py" (
    py -3 start.py
) else (
    python start.py
)
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if not "%EXIT_CODE%"=="0" (
    echo [ERROR] start.py exited with code %EXIT_CODE%.
) else (
    echo [INFO] start.py exited normally.
)

:END
echo.
echo Press any key to close this window...
pause >nul
popd >nul 2>nul
exit /b %EXIT_CODE%
