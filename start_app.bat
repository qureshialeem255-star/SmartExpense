@echo off
title Smart Expense Management System
echo ===================================================
echo     SMART EXPENSE MANAGEMENT SYSTEM (FLASK + AI)
echo ===================================================
echo.

set PYTHON_EXEC="C:\Users\aziza\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe"

if exist %PYTHON_EXEC% (
    echo [INFO] Using verified Python 3.11 environment...
    %PYTHON_EXEC% run.py
) else (
    echo [INFO] Falling back to system python...
    python run.py
)

pause

