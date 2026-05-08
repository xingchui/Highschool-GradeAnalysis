@echo off
REM Build script for Grade Analysis App v3.0.0

set APP_VERSION=v3.0.0
set APP_NAME=GradeAnalysisApp_%APP_VERSION%

echo ============================================
echo Grade Analysis App %APP_VERSION% - Build Script
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

echo Building Grade Analysis App %APP_VERSION%...
echo.

REM Build with PyInstaller using the new app factory structure
pyinstaller --onefile ^
    --name %APP_NAME% ^
    --version-file "version.txt" ^
    --add-data "templates;templates" ^
    --add-data "config.json;." ^
    --add-data "README.md;." ^
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
    --hidden-import=app.routes.rankings ^
    --hidden-import=app.routes.statistics ^
    --hidden-import=app.routes.trend ^
    --hidden-import=app.routes.config ^
    --hidden-import=app.utils ^
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
<<<<<<< HEAD
echo Output: dist\GradeAnalysisApp.exe
echo Version: 3.0.0
=======
echo Output: dist\%APP_NAME%.exe
echo Version: %APP_VERSION%
>>>>>>> e26772c (release: v3.0.0)
echo ============================================
pause
