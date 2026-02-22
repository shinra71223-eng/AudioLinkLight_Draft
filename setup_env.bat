@echo off
REM ============================================
REM AudioLinkLight - Demucs Environment Setup
REM ============================================
REM Run this script on a new PC to set up the
REM Python virtual environment with Demucs.
REM Requires: Python 3.10+ installed on the system
REM ============================================

echo.
echo ========================================
echo  AudioLinkLight - Environment Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check if .venv already exists
if exist ".venv\Scripts\python.exe" (
    echo [INFO] .venv already exists. Skipping creation.
    echo [INFO] To recreate, delete the .venv folder first.
    goto :install_packages
)

echo [1/3] Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

:install_packages
echo [2/3] Installing packages (this may take a while)...
echo       - PyTorch + torchaudio
echo       - Demucs 4.0.1
echo.

.venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Package installation failed.
    pause
    exit /b 1
)

REM Create separated folders if missing
echo [3/3] Creating output directories...
if not exist "separated\fast" mkdir "separated\fast"
if not exist "separated\hq" mkdir "separated\hq"

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo  .venv created with Demucs %DEMUCS_VER%
echo  separated/fast/ and separated/hq/ ready
echo.
echo  Open AudioLinkLight_V00.toe in
echo  TouchDesigner to start working.
echo ========================================
pause
