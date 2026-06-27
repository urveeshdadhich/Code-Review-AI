@echo off
echo Starting CodeReviewAI Uninstallation for Windows...

set VENV_DIR=%USERPROFILE%\.code_review_ai_venv
if exist "%VENV_DIR%" (
    echo Removing virtual environment at %VENV_DIR% ...
    rmdir /s /q "%VENV_DIR%"
)

set CONFIG_FILE=%USERPROFILE%\.code_review_ai.env
if exist "%CONFIG_FILE%" (
    set /p DEL_CONFIG="Do you also want to delete your saved API keys at %CONFIG_FILE%? (y/N): "
    if /i "%DEL_CONFIG%"=="y" (
        del "%CONFIG_FILE%"
        echo Deleted config file.
    ) else (
        echo Kept config file intact.
    )
)

echo.
echo ======================================================
echo Uninstallation complete!
echo ======================================================
pause
