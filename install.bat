@echo off
echo Starting CodeReviewAI Installation for Windows...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python could not be found. Please install Python.
    pause
    exit /b 1
)

set VENV_DIR=%USERPROFILE%\.code_review_ai_venv
echo Creating virtual environment at %VENV_DIR% ...
python -m venv "%VENV_DIR%"

echo Installing dependencies...
"%VENV_DIR%\Scripts\pip.exe" install --upgrade pip --no-cache-dir
"%VENV_DIR%\Scripts\pip.exe" install . --no-cache-dir

echo.
echo ======================================================
echo Installation complete!
echo ======================================================
echo To run the tool from anywhere, you need to add it to your PATH.
echo Run this exact command in PowerShell to add it permanently:
echo.
echo [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:USERPROFILE\.code_review_ai_venv\Scripts", "User")
echo.
echo After running that, close this window, open a new terminal, and type 'cr' to start!
echo ======================================================
pause
