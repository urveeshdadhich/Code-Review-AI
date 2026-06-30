@echo off
echo Uninstalling Java CodeReviewAI...

set "BIN_FILE=%USERPROFILE%\.local\bin\cr.bat"
if exist "%BIN_FILE%" (
    del "%BIN_FILE%"
    echo Removed executable: %BIN_FILE%
) else (
    echo Executable %BIN_FILE% not found.
)

set "INSTALL_DIR=%USERPROFILE%\.code_review_ai_java"
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
    echo Removed app directory: %INSTALL_DIR%
) else (
    echo App directory %INSTALL_DIR% not found.
)

set "ENV_FILE=%USERPROFILE%\.code_review_ai.env"
if exist "%ENV_FILE%" (
    set /p DEL_KEYS="Do you want to remove your saved API keys? (y/N) "
    if /I "%DEL_KEYS%"=="y" (
        del "%ENV_FILE%"
        echo Removed API keys file: %ENV_FILE%
    ) else (
        echo Kept API keys file.
    )
)

echo.
echo Note: JDK 21 and Maven were NOT uninstalled, as they might be used by other applications.
echo.
echo Uninstallation completely finished!
pause
