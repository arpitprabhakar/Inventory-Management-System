@echo off
setlocal enabledelayedexpansion
title Inventory Manager - Setup
color 0A

echo.
echo =================================================
echo    Inventory Manager -- Dependency Installer
echo =================================================
echo.


:: ── 1. Check Python ───────────────────────────────
echo [>>] Checking Python 3...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo  Please download and install Python from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During installation, check the box that says
    echo  "Add Python to PATH" before clicking Install Now.
    echo.
    goto FAILED
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [OK]  Found %PY_VER%


:: ── 2. Check pip ──────────────────────────────────
echo.
echo [>>] Checking pip...

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] pip not found. Attempting to install via ensurepip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo [ERROR] Could not install pip. Please reinstall Python.
        goto FAILED
    )
)
echo [OK]  pip is available


:: ── 3. Upgrade pip ────────────────────────────────
echo.
echo [>>] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK]  pip upgraded


:: ── 4. Install tkinter notice ─────────────────────
echo.
echo [>>] Checking tkinter...

python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] tkinter is missing.
    echo.
    echo  tkinter is bundled with the official Python installer.
    echo  To fix this:
    echo    1. Open the Python installer again
    echo    2. Choose "Modify"
    echo    3. Ensure "tcl/tk and IDLE" is checked
    echo    4. Complete the installation and re-run this script
    echo.
    goto FAILED
)
echo [OK]  tkinter is available


:: ── 5. Install pandas and numpy ───────────────────
echo.
echo [>>] Installing pandas...
python -m pip install pandas
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install pandas.
    goto FAILED
)
echo [OK]  pandas installed

echo.
echo [>>] Installing numpy...
python -m pip install numpy
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install numpy.
    goto FAILED
)
echo [OK]  numpy installed


:: ── 6. Verify all imports ─────────────────────────
echo.
echo [>>] Verifying all imports...
echo.

python -c ^
"import sys; ^
mods = ['tkinter','pandas','numpy','os','csv','datetime']; ^
ok = True; ^
[print('  [OK]  ' + m) if __import__(m) or True else None for m in mods]; ^
" 2>&1

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] One or more imports failed.
    goto FAILED
)


:: ── Done ──────────────────────────────────────────
echo.
echo =================================================
echo    Setup complete! You are good to go.
echo =================================================
echo.
echo  Run the app with:
echo     python inventory_manager.py
echo.
echo  Or just double-click inventory_manager.py
echo  if .py files are associated with Python.
echo.
pause
exit /b 0


:FAILED
echo.
echo =================================================
echo    Setup failed. Check the errors above.
echo =================================================
echo.
pause
exit /b 1
