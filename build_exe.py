"""
Build script to create standalone .exe file
Run this script to generate the executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def create_icon():
    """Create a simple icon file (optional)"""
    # You can replace this with your own icon file
    # For now, we'll use the default PyInstaller icon
    icon_path = "icon.ico"
    if not os.path.exists(icon_path):
        print("ℹ️ No custom icon found, using default")
        return None
    return icon_path

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI only)
        "--name=GestureCursorController", # Executable name
        "--distpath=dist",              # Output directory
        "--workpath=build",             # Temporary build directory
        "--specpath=.",                 # Spec file location
        "--clean",                      # Clean cache
        "--noconfirm",                  # Overwrite without asking
        "main.py"                       # Main script
    ]
    
    # Add icon if available
    icon_path = create_icon()
    if icon_path:
        cmd.extend(["--icon", icon_path])
    
    # Add hidden imports for common issues
    hidden_imports = [
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "cv2",
        "mediapipe",
        "numpy",
        "pyautogui",
        "keyboard",
        "threading",
        "json",
        "webbrowser",
        "platform",
        "datetime",
        "math",
        "time",
        "os",
        "sys"
    ]
    
    for module in hidden_imports:
        cmd.extend(["--hidden-import", module])
    
    # Add data files if any (like settings templates)
    # cmd.extend(["--add-data", "assets;assets"])  # Uncomment if you have assets
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_installer_readme():
    """Create a README file for distribution"""
    readme_content = """
# 🖱️ Gesture Cursor Controller

## What is this?
This is a hand gesture-controlled mouse application that lets you control your computer cursor using hand gestures captured by your webcam.

## 🚀 Quick Start
1. **Double-click** `GestureCursorController.exe` to start the application
2. **Allow camera access** when prompted
3. **Click "Start Cursor Control"** in the app
4. **Use hand gestures** to control your mouse:
   - 🤏 **Pinch** = Left Click
   - 🤙 **Pinky Only** = Right Click  
   - ✋ **4 Fingers** = Move Cursor
   - 👆 **1 Finger** = Bookmark 1
   - ✌️ **2 Fingers** = Bookmark 2
   - 🤘 **Index + Pinky** = Bookmark 3

## 📋 System Requirements
- **Windows 10/11** (64-bit)
- **Webcam** (built-in or external)
- **4GB RAM** minimum
- **Good lighting** for best gesture recognition

## ⚙️ Features
- **Real-time gesture recognition**
- **Customizable sensitivity settings**
- **Bookmark websites** with gestures
- **Training mode** to practice gestures
- **Emergency stop** with Ctrl+Alt+Q

## 🆘 Troubleshooting
- **Camera not working?** Check if other apps are using the camera
- **Gestures not recognized?** Try the Training Mode to practice
- **App won't start?** Run as Administrator
- **Performance issues?** Close other heavy applications

## 🔒 Privacy & Security
- **No data collection** - everything runs locally
- **No internet required** - works completely offline
- **Camera access** - only used for gesture recognition
- **Settings saved locally** - in gesture_settings.json

## 📞 Support
If you encounter any issues, please check the troubleshooting section above.

---
**Gesture Cursor Controller v1.0**
Created with ❤️ for hands-free computing
"""
    
    with open("dist/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("📝 README.txt created")

def create_batch_installer():
    """Create a simple batch file for easy installation"""
    batch_content = """@echo off
echo 🖱️ Gesture Cursor Controller
echo ========================
echo.
echo This will start the Gesture Cursor Controller
echo Make sure your webcam is connected and working
echo.
pause
echo.
echo Starting application...
GestureCursorController.exe
"""
    
    with open("dist/Start_Gesture_Controller.bat", "w") as f:
        f.write(batch_content)
    print("📄 Start_Gesture_Controller.bat created")

def cleanup_build_files():
    """Clean up temporary build files"""
    build_dir = "build"
    spec_file = "GestureCursorController.spec"
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print(f"🧹 Cleaned up {build_dir}")
    
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"🧹 Cleaned up {spec_file}")

def create_distribution_package():
    """Create the final distribution package"""
    print("\n🎁 Creating distribution package...")
    
    dist_dir = "dist"
    package_dir = "GestureCursorController_v1.0"
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    
    # Create package directory
    os.makedirs(package_dir, exist_ok=True)
    
    # Copy executable
    exe_path = os.path.join(dist_dir, "GestureCursorController.exe")
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, package_dir)
        print(f"📦 Copied executable to {package_dir}")
    
    # Copy additional files
    additional_files = [
        (os.path.join(dist_dir, "README.txt"), "README.txt"),
        (os.path.join(dist_dir, "Start_Gesture_Controller.bat"), "Start_Gesture_Controller.bat")
    ]
    
    for src, dst in additional_files:
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(package_dir, dst))
    
    print(f"✅ Distribution package created: {package_dir}/")
    print(f"📁 Package size: {get_directory_size(package_dir):.1f} MB")

def get_directory_size(directory):
    """Get directory size in MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)  # Convert to MB

def main():
    """Main build process"""
    print("🏗️ Building Gesture Cursor Controller Executable")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ main.py not found! Please run this script from the project root directory.")
        sys.exit(1)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build executable
    if build_executable():
        # Create additional files
        create_installer_readme()
        create_batch_installer()
        
        # Create distribution package
        create_distribution_package()
        
        # Clean up
        cleanup_build_files()
        
        print("\n🎉 Build completed successfully!")
        print("📂 Your executable is ready in: GestureCursorController_v1.0/")
        print("📤 You can now distribute this folder to others")
        print("\n💡 To create a ZIP file for easy sharing:")
        print("   Right-click 'GestureCursorController_v1.0' folder → Send to → Compressed folder")
    else:
        print("❌ Build failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()