@echo off
REM ============================================
REM AudioLinkLight - Environment Setup
REM ============================================
REM Run this on a new PC to set up everything.
REM Requires: Python 3.10+, Internet connection
REM ============================================

echo.
echo ========================================
echo  AudioLinkLight - Environment Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM ---- Step 1: Python venv ----
if exist ".venv\Scripts\python.exe" (
    echo [1/4] .venv already exists. Skipping.
) else (
    echo [1/4] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create .venv
        pause
        exit /b 1
    )
)

echo [2/4] Installing Python packages...
.venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed
    pause
    exit /b 1
)

REM ---- Step 3: FFmpeg ----
if exist "bin\ffmpeg.exe" (
    echo [3/4] FFmpeg already exists. Skipping.
) else (
    echo [3/4] Downloading FFmpeg...
    mkdir bin 2>nul

    REM Download ffmpeg release (essentials build)
    set FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
    set FFMPEG_ZIP=bin\ffmpeg_download.zip

    echo       Downloading from %FFMPEG_URL%
    powershell -Command "Invoke-WebRequest -Uri '%FFMPEG_URL%' -OutFile '%FFMPEG_ZIP%'" 2>nul
    if errorlevel 1 (
        echo       [Fallback] Trying curl...
        curl -L -o "%FFMPEG_ZIP%" "%FFMPEG_URL%"
    )

    if exist "%FFMPEG_ZIP%" (
        echo       Extracting ffmpeg.exe...
        powershell -Command "$zip = [System.IO.Compression.ZipFile]::OpenRead('%FFMPEG_ZIP%'); $entry = $zip.Entries | Where-Object { $_.Name -eq 'ffmpeg.exe' } | Select-Object -First 1; if ($entry) { [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, 'bin\ffmpeg.exe', $true) }; $zip.Dispose()"
        del "%FFMPEG_ZIP%" 2>nul
        if exist "bin\ffmpeg.exe" (
            echo       FFmpeg installed successfully!
        ) else (
            echo       [WARNING] Could not extract ffmpeg.exe. Please download manually:
            echo       https://www.gyan.dev/ffmpeg/builds/
            echo       Place ffmpeg.exe in the bin\ folder.
        )
    ) else (
        echo       [WARNING] Download failed. Please download FFmpeg manually:
        echo       https://www.gyan.dev/ffmpeg/builds/
        echo       Place ffmpeg.exe in the bin\ folder.
    )
)

REM ---- Step 4: Create folders ----
echo [4/4] Creating directories...
if not exist "separated\fast" mkdir "separated\fast"
if not exist "separated\hq" mkdir "separated\hq"
if not exist "media\music" mkdir "media\music"

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo  Next steps:
echo  1. Place music files in media\music\
echo  2. Open AudioLinkLight_V00.toe in TouchDesigner
echo.
if not exist "bin\ffmpeg.exe" (
    echo  [!] FFmpeg was not installed automatically.
    echo      Download from https://www.gyan.dev/ffmpeg/builds/
    echo      Place ffmpeg.exe in the bin\ folder.
    echo.
)
pause
