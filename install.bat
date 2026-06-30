@echo off
echo Starting Java CodeReviewAI Installation for Windows...

:: Check if javac is available
javac -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] JDK 21 is not installed or not in PATH!
    echo Please install JDK 21 and Maven manually from:
    echo - https://adoptium.net/
    echo - https://maven.apache.org/
    exit /b 1
)

:: Check if mvn is available
mvn -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Maven is not installed or not in PATH!
    echo Please install Maven manually.
    exit /b 1
)

echo Compiling Native Java Executable...
call mvn clean package
if %errorlevel% neq 0 (
    echo [ERROR] Maven build failed!
    exit /b 1
)

set "INSTALL_DIR=%USERPROFILE%\.code_review_ai_java"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
copy /Y target\code-review-ai-1.0-shaded.jar "%INSTALL_DIR%\app.jar" >nul

set "BIN_DIR=%USERPROFILE%\.local\bin"
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

echo @echo off > "%BIN_DIR%\cr.bat"
echo java -jar "%INSTALL_DIR%\app.jar" %%* >> "%BIN_DIR%\cr.bat"

echo.
echo =========================================================
echo Installation complete! 
echo Make sure "%BIN_DIR%" is added to your Windows PATH environment variable.
echo You can then run 'cr' from anywhere in the command prompt.
echo =========================================================
pause
