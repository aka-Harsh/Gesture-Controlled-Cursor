@echo off
echo 🖱️ Cursor Controller Setup
echo ==========================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found!
python --version

:: Create virtual environment
echo.
echo 📦 Creating virtual environment...
python -m venv hand_gesture_env

:: Activate virtual environment
echo ⚡ Activating virtual environment...
call hand_gesture_env\Scripts\activate.bat

:: Upgrade pip
echo.
echo 🔧 Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo.
echo 📚 Installing dependencies...
echo    - OpenCV (Computer Vision)
echo    - MediaPipe (Hand Tracking)
echo    - PyAutoGUI (System Control)
echo    - NumPy (Math Operations)
pip install -r requirements.txt

:: Install PyInstaller for building
echo.
echo 🔨 Installing PyInstaller...
pip install pyinstaller

echo.
echo ==========================
echo ✅ SETUP COMPLETED!
echo ==========================
echo.
echo 🎮 To run the application:
echo    1. run.bat  (Quick start)
echo    2. python main.py  (Manual)
echo.
echo 🔨 To build executable:
echo    1. python build.py
echo.
echo 🖱️ Ready for cursor control!
echo.
pause