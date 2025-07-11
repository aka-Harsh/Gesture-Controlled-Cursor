"""
Enhanced Hand Gesture Cursor Controller
Main Application Entry Point
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    """Main function to run the application"""
    print("🖱️ Enhanced Gesture Cursor Controller")
    print("=" * 50)
    print("🚀 Starting application...")
    
    try:
        # Create main window
        root = tk.Tk()
        app = MainWindow(root)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        messagebox.showerror("Application Error", f"Failed to start application:\n{str(e)}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()