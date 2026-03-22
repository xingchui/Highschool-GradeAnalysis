@echo off
REM Build script for Grade Analysis App v2.0

echo ============================================
echo Grade Analysis App v2.0 - Build Script
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Create dist folder if not exists
if not exist dist mkdir dist

echo Building Grade Analysis App...
echo.

REM Build with PyInstaller using the new app factory structure
pyinstaller --onefile ^
    --name GradeAnalysisApp ^
    --add-data "templates;templates" ^
    --add-data "config.json;." ^
    --hidden-import=flask ^
    --hidden-import=werkzeug ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=xlrd ^
    --hidden-import=plotly ^
    --hidden-import=jinja2 ^
    --hidden-import=markupsafe ^
    --hidden-import=click ^
    --hidden-import=itsdangerous ^
    --hidden-import=app ^
    --hidden-import=app.core ^
    --hidden-import=app.core.data_service ^
    --hidden-import=app.core.grade_service ^
    --hidden-import=app.routes ^
    --hidden-import=app.routes.main ^
    --hidden-import=app.routes.api ^
    run.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build complete!
echo Output: dist\GradeAnalysisApp.exe
echo ============================================
pause
