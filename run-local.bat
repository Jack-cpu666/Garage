@echo off
echo ==================================================================================
echo METROPOLIS PARKING MANAGEMENT SYSTEM - LOCAL TESTING
echo ==================================================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Ask about Selenium
set /p selenium="Do you want to enable auto token refresh? (requires Chrome/Edge/Firefox) [y/N]: "
if /i "%selenium%"=="y" (
    echo Installing Selenium for auto token refresh...
    pip install selenium==4.16.0
    set AUTO_TOKEN_REFRESH=true
) else (
    set AUTO_TOKEN_REFRESH=false
)

REM Set environment variables for testing
for /f %%i in ('python -c "import secrets; print(secrets.token_hex(32))"') do set SECRET_KEY=%%i
set ADMIN_PASSWORD=admin
set PORT=10000

echo.
echo ==================================================================================
echo Setup complete!
echo ==================================================================================
echo.
echo Your login credentials:
echo    Password: admin
echo.
echo Starting server at: http://localhost:10000
echo.
echo Press Ctrl+C to stop the server
echo ==================================================================================

REM Run the application
python app.py

pause
