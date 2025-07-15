"""
Fix script to complete the build process
Run this after the main build to fix the Unicode issue
"""

import os
import shutil

def create_batch_installer():
    """Create a simple batch file for easy installation"""
    batch_content = """@echo off
echo Gesture Cursor Controller
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
    
    os.makedirs("dist", exist_ok=True)
    with open("dist/Start_Gesture_Controller.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    print("✅ Start_Gesture_Controller.bat created")

def create_distribution_package():
    """Create the final distribution package"""
    print("🎁 Creating distribution package...")
    
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
        
        # Get file size
        file_size = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"📊 Executable size: {file_size:.1f} MB")
    else:
        print("❌ Executable not found!")
        return False
    
    # Copy additional files
    additional_files = [
        ("dist/README.txt", "README.txt"),
        ("dist/Start_Gesture_Controller.bat", "Start_Gesture_Controller.bat")
    ]
    
    for src, dst in additional_files:
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(package_dir, dst))
            print(f"📄 Copied {dst}")
    
    print(f"✅ Distribution package created: {package_dir}/")
    return True

def cleanup_build_files():
    """Clean up temporary build files"""
    files_to_remove = [
        "build",
        "GestureCursorController.spec",
        "__pycache__"
    ]
    
    for item in files_to_remove:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
                print(f"🧹 Cleaned up directory: {item}")
            else:
                os.remove(item)
                print(f"🧹 Cleaned up file: {item}")

def verify_build():
    """Verify that the build was successful"""
    required_files = [
        "dist/GestureCursorController.exe",
        "GestureCursorController_v1.0/GestureCursorController.exe",
        "GestureCursorController_v1.0/README.txt",
        "GestureCursorController_v1.0/Start_Gesture_Controller.bat"
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / (1024 * 1024) if file_path.endswith('.exe') else 0
            status = f"({size:.1f} MB)" if size > 0 else ""
            print(f"✅ {file_path} {status}")
        else:
            print(f"❌ Missing: {file_path}")
            all_good = False
    
    return all_good

def main():
    """Fix and complete the build"""
    print("🔧 Fixing and completing the build...")
    print("=" * 40)
    
    # Create missing files
    create_batch_installer()
    
    # Create distribution package
    if create_distribution_package():
        # Clean up build files
        cleanup_build_files()
        
        # Verify everything is ready
        print("\n🔍 Verifying build...")
        if verify_build():
            print("\n🎉 Build completed successfully!")
            print("📂 Your executable is ready in: GestureCursorController_v1.0/")
            print("📤 You can now distribute this folder to others")
            print("\n💡 Next steps:")
            print("   1. Test the executable on another computer")
            print("   2. Create a ZIP file: Right-click folder → Send to → Compressed folder")
            print("   3. Upload to your chosen marketplace (GitHub, Itch.io, etc.)")
        else:
            print("❌ Some files are missing. Please check the errors above.")
    else:
        print("❌ Failed to create distribution package.")

if __name__ == "__main__":
    main()