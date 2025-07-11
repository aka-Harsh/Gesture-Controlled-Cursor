"""
Compact Fixed-Size Main Window GUI
Clean, centered layout with all functionality organized in tabs
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager
from core.gesture_detector import GestureDetector
from core.camera_controller import CameraController
from gui.training_window import TrainingWindow

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("⚠️ Keyboard library not available. Emergency hotkey disabled.")

class CompactStyle:
    """Clean, compact styling"""
    
    COLORS = {
        'bg_main': '#f0f0f0',           # Light gray background
        'bg_card': '#ffffff',           # White cards
        'bg_header': '#2c3e50',         # Dark blue header
        'bg_button': '#3498db',         # Blue buttons
        'bg_button_hover': '#2980b9',   # Darker blue on hover
        'bg_success': '#27ae60',        # Green
        'bg_danger': '#e74c3c',         # Red
        'bg_warning': '#f39c12',        # Orange
        'bg_info': '#8e44ad',           # Purple
        
        'text_primary': '#2c3e50',      # Dark gray text
        'text_secondary': '#7f8c8d',    # Light gray text
        'text_white': '#ffffff',        # White text
        'text_accent': '#3498db',       # Blue accent
        
        'border': '#bdc3c7',            # Light border
        'border_focus': '#3498db'       # Blue focus border
    }
    
    FONTS = {
        'title': ('Arial', 16, 'bold'),
        'heading': ('Arial', 12, 'bold'),
        'body': ('Arial', 10),
        'body_bold': ('Arial', 10, 'bold'),
        'small': ('Arial', 9)
    }

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Initialize managers
        self.settings_manager = SettingsManager()
        # Update settings to only have 3 bookmarks
        bookmarks = self.settings_manager.get("bookmarks")
        if len(bookmarks) > 3:
            self.settings_manager.set("bookmarks", bookmarks[:3])
        elif len(bookmarks) < 3:
            while len(bookmarks) < 3:
                bookmarks.append("")
            self.settings_manager.set("bookmarks", bookmarks)
        
        self.gesture_detector = None
        self.camera_controller = None
        
        # Application state
        self.is_running = False
        self.training_window = None
        
        # Setup GUI
        self.setup_compact_gui()
        self.setup_emergency_stop()
        
        # Initialize components after GUI
        self.initialize_components()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        print("🎨 Compact window initialized")
    
    def setup_window(self):
        """Setup compact fixed-size window"""
        self.root.title("Gesture Cursor Controller")
        
        # Fixed size - no resizing
        window_width = 600
        window_height = 700
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(False, False)  # Fixed size
        self.root.configure(bg=CompactStyle.COLORS['bg_main'])
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.root.winfo_screenheight() // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def initialize_components(self):
        """Initialize gesture detector and camera controller"""
        try:
            self.gesture_detector = GestureDetector(self.settings_manager.settings)
            self.camera_controller = CameraController(self.settings_manager.settings, self.gesture_detector)
        except Exception as e:
            print(f"Error initializing components: {e}")
    
    def setup_compact_gui(self):
        """Setup compact GUI with all functionality organized in tabs"""
        # Header
        self.setup_header()
        
        # Create notebook for tabs
        self.setup_notebook()
        
        # Status bar
        self.setup_status_bar()
    
    def setup_header(self):
        """Setup header"""
        header_frame = tk.Frame(self.root, bg=CompactStyle.COLORS['bg_header'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title with icon
        title_frame = tk.Frame(header_frame, bg=CompactStyle.COLORS['bg_header'])
        title_frame.pack(expand=True)
        
        icon_label = tk.Label(title_frame, text="🖱️", 
                             bg=CompactStyle.COLORS['bg_header'],
                             font=('Arial', 20))
        icon_label.pack(side='left', padx=(0, 10), pady=15)
        
        title_label = tk.Label(title_frame, text="Gesture Cursor Controller",
                              bg=CompactStyle.COLORS['bg_header'],
                              fg=CompactStyle.COLORS['text_white'],
                              font=CompactStyle.FONTS['title'])
        title_label.pack(side='left', pady=15)
    
    def setup_notebook(self):
        """Setup tabbed interface with all functionality"""
        # Create notebook frame
        notebook_frame = tk.Frame(self.root, bg=CompactStyle.COLORS['bg_main'])
        notebook_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Configure notebook style
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[12, 8], font=CompactStyle.FONTS['body'])
        
        # Create tabs
        self.setup_main_tab()
        self.setup_settings_tab()
        self.setup_bookmarks_tab()
        self.setup_advanced_tab()
    
    def setup_main_tab(self):
        """Setup main control tab"""
        main_frame = tk.Frame(self.notebook, bg=CompactStyle.COLORS['bg_main'])
        self.notebook.add(main_frame, text="   Control   ")
        
        # Status indicators
        self.setup_status_section_tab(main_frame)
        
        # Control buttons
        self.setup_control_section_tab(main_frame)
        
        # Gesture guide
        self.setup_gesture_section_tab(main_frame)
    
    def setup_settings_tab(self):
        """Setup settings tab with all controls"""
        settings_frame = tk.Frame(self.notebook, bg=CompactStyle.COLORS['bg_main'])
        self.notebook.add(settings_frame, text="   Settings   ")
        
        # Create scrollable frame for settings
        canvas = tk.Canvas(settings_frame, bg=CompactStyle.COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=CompactStyle.COLORS['bg_main'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Processing mode
        self.setup_processing_section(scrollable_frame)
        
        # Sensitivity settings
        self.setup_sensitivity_section(scrollable_frame)
        
        # Performance settings
        self.setup_performance_section(scrollable_frame)
        
        # Visual settings
        self.setup_visual_section(scrollable_frame)
        
        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_bookmarks_tab(self):
        """Setup bookmarks tab"""
        bookmarks_frame = tk.Frame(self.notebook, bg=CompactStyle.COLORS['bg_main'])
        self.notebook.add(bookmarks_frame, text="   Bookmarks   ")
        
        # Header
        header_frame = tk.Frame(bookmarks_frame, bg=CompactStyle.COLORS['bg_main'])
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        title_label = tk.Label(header_frame, text="🔖 Bookmark Configuration",
                              bg=CompactStyle.COLORS['bg_main'], fg=CompactStyle.COLORS['text_primary'],
                              font=CompactStyle.FONTS['title'])
        title_label.pack(anchor='w')
        
        desc_label = tk.Label(header_frame, text="Configure up to 3 websites to open with finger gestures",
                             bg=CompactStyle.COLORS['bg_main'], fg=CompactStyle.COLORS['text_secondary'],
                             font=CompactStyle.FONTS['body'])
        desc_label.pack(anchor='w', pady=(2, 0))
        
        # Create scrollable frame for bookmarks
        canvas = tk.Canvas(bookmarks_frame, bg=CompactStyle.COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(bookmarks_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=CompactStyle.COLORS['bg_main'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bookmarks
        self.setup_bookmarks_section_tab(scrollable_frame)
        
        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_advanced_tab(self):
        """Setup advanced settings tab"""
        advanced_frame = tk.Frame(self.notebook, bg=CompactStyle.COLORS['bg_main'])
        self.notebook.add(advanced_frame, text="   Advanced   ")
        
        # Create scrollable frame for advanced settings
        canvas = tk.Canvas(advanced_frame, bg=CompactStyle.COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(advanced_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=CompactStyle.COLORS['bg_main'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Backup and restore
        self.setup_backup_section(scrollable_frame)
        
        # System information
        self.setup_system_info_section(scrollable_frame)
        
        # Training section
        self.setup_training_section(scrollable_frame)
        
        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_status_section_tab(self, parent):
        """Setup status indicators in main tab"""
        status_frame = self.create_card_tab(parent, "📊 Performance Monitor")
        
        # Status indicators in a grid
        indicators_frame = tk.Frame(status_frame, bg=CompactStyle.COLORS['bg_card'])
        indicators_frame.pack(fill='x', padx=15, pady=10)
        
        # FPS
        fps_frame = tk.Frame(indicators_frame, bg=CompactStyle.COLORS['bg_main'], relief='solid', bd=1)
        fps_frame.pack(side='left', fill='x', expand=True, padx=(0, 5), pady=2)
        
        tk.Label(fps_frame, text="FPS", bg=CompactStyle.COLORS['bg_main'],
                fg=CompactStyle.COLORS['text_secondary'], font=CompactStyle.FONTS['small']).pack(pady=(5, 0))
        
        self.fps_var = tk.StringVar(value="--")
        tk.Label(fps_frame, textvariable=self.fps_var, bg=CompactStyle.COLORS['bg_main'],
                fg=CompactStyle.COLORS['text_accent'], font=CompactStyle.FONTS['body_bold']).pack(pady=(0, 5))
        
        # Gesture
        gesture_frame = tk.Frame(indicators_frame, bg=CompactStyle.COLORS['bg_main'], relief='solid', bd=1)
        gesture_frame.pack(side='left', fill='x', expand=True, padx=5, pady=2)
        
        tk.Label(gesture_frame, text="Gesture", bg=CompactStyle.COLORS['bg_main'],
                fg=CompactStyle.COLORS['text_secondary'], font=CompactStyle.FONTS['small']).pack(pady=(5, 0))
        
        self.gesture_var = tk.StringVar(value="None")
        tk.Label(gesture_frame, textvariable=self.gesture_var, bg=CompactStyle.COLORS['bg_main'],
                fg=CompactStyle.COLORS['text_accent'], font=CompactStyle.FONTS['body_bold']).pack(pady=(0, 5))
        
        # Confidence
        confidence_frame = tk.Frame(indicators_frame, bg=CompactStyle.COLORS['bg_main'], relief='solid', bd=1)
        confidence_frame.pack(side='right', fill='x', expand=True, padx=(5, 0), pady=2)
        
        tk.Label(confidence_frame, text="Confidence", bg=CompactStyle.COLORS['bg_main'],
                fg=CompactStyle.COLORS['text_secondary'], font=CompactStyle.FONTS['small']).pack(pady=(5, 0))
        
        self.confidence_var = tk.StringVar(value="--%")
        tk.Label(confidence_frame, textvariable=self.confidence_var, bg=CompactStyle.COLORS['bg_main'],
                fg=CompactStyle.COLORS['text_accent'], font=CompactStyle.FONTS['body_bold']).pack(pady=(0, 5))
    
    def setup_control_section_tab(self, parent):
        """Setup control buttons in main tab"""
        control_frame = self.create_card_tab(parent, "⚡ Quick Controls")
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg=CompactStyle.COLORS['bg_card'])
        button_frame.pack(fill='x', padx=15, pady=15)
        
        self.start_button = self.create_button(button_frame, "🚀 Start Cursor Control", self.start_control,
                                              bg=CompactStyle.COLORS['bg_success'])
        self.start_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = self.create_button(button_frame, "⏹️ Stop Control", self.stop_control,
                                             bg=CompactStyle.COLORS['bg_danger'], state='disabled')
        self.stop_button.pack(side='left', padx=(0, 10))
        
        self.training_button = self.create_button(button_frame, "🎓 Training Mode", self.start_training,
                                                 bg=CompactStyle.COLORS['bg_info'])
        self.training_button.pack(side='right')
        
        # Emergency note
        emergency_label = tk.Label(control_frame, text="🆘 Emergency Stop: Press Ctrl+Alt+Q anytime",
                                  bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['bg_warning'],
                                  font=CompactStyle.FONTS['body'])
        emergency_label.pack(pady=(0, 15))
    
    def setup_gesture_section_tab(self, parent):
        """Setup gesture guide in main tab"""
        gesture_frame = self.create_card_tab(parent, "🤚 Gesture Guide")
        
        gestures_container = tk.Frame(gesture_frame, bg=CompactStyle.COLORS['bg_card'])
        gestures_container.pack(fill='x', padx=15, pady=10)
        
        # Simple gesture list - 6 gestures in 2 columns
        gestures = [
            ("🤏", "Pinch", "Left Click"),
            ("🤙", "Pinky Only", "Right Click"),
            ("✋", "4 Fingers", "Move Cursor"),
            ("👆", "1 Finger", "Bookmark 1"),
            ("✌️", "2 Fingers", "Bookmark 2"),
            ("🤘", "Index + Pinky", "Bookmark 3")
        ]
        
        for i, (emoji, gesture, action) in enumerate(gestures):
            row = i // 2
            col = i % 2
            
            gesture_item = tk.Frame(gestures_container, bg=CompactStyle.COLORS['bg_main'], 
                                   relief='solid', bd=1)
            gesture_item.grid(row=row, column=col, sticky='ew', padx=2, pady=2)
            
            # Configure grid weights
            gestures_container.grid_columnconfigure(0, weight=1)
            gestures_container.grid_columnconfigure(1, weight=1)
            
            item_content = tk.Frame(gesture_item, bg=CompactStyle.COLORS['bg_main'])
            item_content.pack(fill='x', padx=8, pady=6)
            
            emoji_label = tk.Label(item_content, text=emoji, bg=CompactStyle.COLORS['bg_main'],
                                  font=('Arial', 14))
            emoji_label.pack(side='left', padx=(0, 8))
            
            text_frame = tk.Frame(item_content, bg=CompactStyle.COLORS['bg_main'])
            text_frame.pack(side='left', fill='x', expand=True)
            
            gesture_label = tk.Label(text_frame, text=gesture, bg=CompactStyle.COLORS['bg_main'],
                                    fg=CompactStyle.COLORS['text_primary'], font=CompactStyle.FONTS['body_bold'])
            gesture_label.pack(anchor='w')
            
            action_label = tk.Label(text_frame, text=action, bg=CompactStyle.COLORS['bg_main'],
                                   fg=CompactStyle.COLORS['text_secondary'], font=CompactStyle.FONTS['small'])
            action_label.pack(anchor='w')
    
    def setup_processing_section(self, parent):
        """Setup processing mode section"""
        processing_frame = self.create_card_tab(parent, "🚀 Processing Mode")
        
        mode_frame = tk.Frame(processing_frame, bg=CompactStyle.COLORS['bg_card'])
        mode_frame.pack(fill='x', padx=15, pady=15)
        
        self.gpu_var = tk.BooleanVar(value=self.settings_manager.get("use_gpu"))
        
        # GPU option
        gpu_frame = tk.Frame(mode_frame, bg=CompactStyle.COLORS['bg_card'])
        gpu_frame.pack(fill='x', pady=5)
        
        gpu_radio = tk.Radiobutton(gpu_frame, text="🔥 GPU Accelerated (CUDA)",
                                  variable=self.gpu_var, value=True, command=self.update_gpu_setting,
                                  bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_primary'],
                                  font=CompactStyle.FONTS['body'], anchor='w')
        gpu_radio.pack(fill='x')
        
        gpu_desc = tk.Label(gpu_frame, text="Faster processing, lower CPU usage, requires CUDA-compatible GPU",
                           bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_secondary'],
                           font=CompactStyle.FONTS['small'])
        gpu_desc.pack(fill='x', padx=20, pady=(2, 0))
        
        # CPU option
        cpu_frame = tk.Frame(mode_frame, bg=CompactStyle.COLORS['bg_card'])
        cpu_frame.pack(fill='x', pady=5)
        
        cpu_radio = tk.Radiobutton(cpu_frame, text="💻 CPU Processing",
                                  variable=self.gpu_var, value=False, command=self.update_gpu_setting,
                                  bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_primary'],
                                  font=CompactStyle.FONTS['body'], anchor='w')
        cpu_radio.pack(fill='x')
        
        cpu_desc = tk.Label(cpu_frame, text="Compatible with all systems, uses CPU for processing",
                           bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_secondary'],
                           font=CompactStyle.FONTS['small'])
        cpu_desc.pack(fill='x', padx=20, pady=(2, 0))
    
    def setup_sensitivity_section(self, parent):
        """Setup sensitivity settings"""
        sensitivity_frame = self.create_card_tab(parent, "🎯 Cursor & Gesture Settings")
        
        settings_container = tk.Frame(sensitivity_frame, bg=CompactStyle.COLORS['bg_card'])
        settings_container.pack(fill='x', padx=15, pady=15)
        
        # Cursor sensitivity
        self.create_settings_slider(settings_container, "Cursor Sensitivity", "cursor_sensitivity", 
                                   0.1, 1.0, "Higher values = more responsive cursor movement")
        
        # Click rate
        self.create_settings_slider(settings_container, "Click Rate (clicks/sec)", "click_rate",
                                   0.5, 5.0, "Prevents spam clicking - max clicks per second")
        
        # Gesture threshold
        self.create_settings_slider(settings_container, "Gesture Recognition Threshold", "gesture_threshold",
                                   0.5, 1.0, "Higher values require more precise gestures")
        
        # Stability zone
        self.create_settings_slider(settings_container, "Hand Stability Zone (pixels)", "stability_zone",
                                   5, 50, "Reduces cursor jitter from small hand movements")
    
    def setup_performance_section(self, parent):
        """Setup performance settings"""
        performance_frame = self.create_card_tab(parent, "⚡ Performance Settings")
        
        perf_container = tk.Frame(performance_frame, bg=CompactStyle.COLORS['bg_card'])
        perf_container.pack(fill='x', padx=15, pady=15)
        
        # Camera resolution
        tk.Label(perf_container, text="Camera Resolution:",
                bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_primary'],
                font=CompactStyle.FONTS['body_bold']).pack(anchor='w', pady=(0, 5))
        
        self.resolution_var = tk.StringVar(
            value=f"{self.settings_manager.get('camera_resolution')[0]}x{self.settings_manager.get('camera_resolution')[1]}")
        
        resolutions = ["320x240", "640x480", "800x600", "1280x720"]
        for res in resolutions:
            res_radio = tk.Radiobutton(perf_container, text=res, variable=self.resolution_var, value=res,
                                      command=self.update_resolution, bg=CompactStyle.COLORS['bg_card'],
                                      fg=CompactStyle.COLORS['text_primary'], font=CompactStyle.FONTS['body'])
            res_radio.pack(anchor='w', pady=1)
    
    def setup_visual_section(self, parent):
        """Setup visual feedback settings"""
        visual_frame = self.create_card_tab(parent, "👁️ Visual Feedback")
        
        visual_container = tk.Frame(visual_frame, bg=CompactStyle.COLORS['bg_card'])
        visual_container.pack(fill='x', padx=15, pady=15)
        
        self.visual_var = tk.BooleanVar(value=self.settings_manager.get("show_visual_feedback"))
        
        visual_check = tk.Checkbutton(visual_container, text="Show gesture feedback on camera view",
                                     variable=self.visual_var, command=self.update_visual_feedback,
                                     bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_primary'],
                                     font=CompactStyle.FONTS['body'], anchor='w')
        visual_check.pack(fill='x')
        
        desc_label = tk.Label(visual_container,
                             text="Displays gesture recognition results and instructions on camera feed",
                             bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_secondary'],
                             font=CompactStyle.FONTS['small'])
        desc_label.pack(fill='x', pady=(5, 0))
    
    def setup_bookmarks_section_tab(self, parent):
        """Setup bookmarks section in tab"""
        self.bookmark_entries = []
        
        for i in range(3):
            bookmark_frame = self.create_card_tab(parent, f"🔖 Bookmark {i+1}")
            
            bookmark_container = tk.Frame(bookmark_frame, bg=CompactStyle.COLORS['bg_card'])
            bookmark_container.pack(fill='x', padx=15, pady=15)
            
            # Gesture info
            gestures = ["👆 1 Finger (Index)", "✌️ 2 Fingers (Index+Middle)", "🤘 Index + Pinky"]
            gesture_label = tk.Label(bookmark_container, text=f"Gesture: {gestures[i]}",
                                    bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_accent'],
                                    font=CompactStyle.FONTS['body_bold'])
            gesture_label.pack(anchor='w', pady=(0, 8))
            
            # URL label
            url_label = tk.Label(bookmark_container, text="Website URL:",
                                bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_primary'],
                                font=CompactStyle.FONTS['body'])
            url_label.pack(anchor='w', pady=(0, 5))
            
            # Entry and button frame
            entry_frame = tk.Frame(bookmark_container, bg=CompactStyle.COLORS['bg_card'])
            entry_frame.pack(fill='x')
            
            # URL entry
            entry = tk.Entry(entry_frame, font=CompactStyle.FONTS['body'], relief='solid', bd=1)
            entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
            entry.insert(0, self.settings_manager.get("bookmarks")[i])
            self.bookmark_entries.append(entry)
            
            # Buttons
            test_button = self.create_button(entry_frame, "🧪 Test", 
                                           lambda idx=i: self.test_bookmark(idx),
                                           bg=CompactStyle.COLORS['bg_info'], size='small')
            test_button.pack(side='right', padx=(0, 5))
            
            clear_button = self.create_button(entry_frame, "🗑️ Clear",
                                            lambda idx=i: self.clear_bookmark(idx),
                                            bg=CompactStyle.COLORS['bg_warning'], size='small')
            clear_button.pack(side='right')
        
        # Save button
        save_frame = tk.Frame(parent, bg=CompactStyle.COLORS['bg_main'])
        save_frame.pack(fill='x', padx=10, pady=10)
        
        save_button = self.create_button(save_frame, "💾 Save All Bookmarks", self.save_bookmarks,
                                        bg=CompactStyle.COLORS['bg_success'])
        save_button.pack()
    
    def setup_backup_section(self, parent):
        """Setup backup and restore section"""
        backup_frame = self.create_card_tab(parent, "💾 Backup & Restore")
        
        backup_container = tk.Frame(backup_frame, bg=CompactStyle.COLORS['bg_card'])
        backup_container.pack(fill='x', padx=15, pady=15)
        
        button_frame = tk.Frame(backup_container, bg=CompactStyle.COLORS['bg_card'])
        button_frame.pack(fill='x')
        
        export_button = self.create_button(button_frame, "📤 Export Settings", self.export_settings,
                                          bg=CompactStyle.COLORS['bg_info'])
        export_button.pack(side='left', padx=(0, 10))
        
        import_button = self.create_button(button_frame, "📥 Import Settings", self.import_settings,
                                          bg=CompactStyle.COLORS['bg_warning'])
        import_button.pack(side='left', padx=(0, 10))
        
        reset_button = self.create_button(button_frame, "🔄 Reset to Defaults", self.reset_settings,
                                         bg=CompactStyle.COLORS['bg_danger'])
        reset_button.pack(side='right')
    
    def setup_system_info_section(self, parent):
        """Setup system information section"""
        info_frame = self.create_card_tab(parent, "💻 System Information")
        
        info_container = tk.Frame(info_frame, bg=CompactStyle.COLORS['bg_card'])
        info_container.pack(fill='x', padx=15, pady=15)
        
        # Get system info
        import platform
        import cv2
        
        system_info = [
            ("Operating System", f"{platform.system()} {platform.release()}"),
            ("Python Version", platform.python_version()),
            ("OpenCV Version", cv2.__version__)]
        system_info = [
            ("Operating System", f"{platform.system()} {platform.release()}"),
            ("Python Version", platform.python_version()),
            ("OpenCV Version", cv2.__version__),
            ("Keyboard Support", "Enabled" if KEYBOARD_AVAILABLE else "Disabled"),
            ("GPU Support", "Available" if self.settings_manager.get("use_gpu") else "CPU Only")
        ]
        
        for label, value in system_info:
            info_item = tk.Frame(info_container, bg=CompactStyle.COLORS['bg_main'], relief='solid', bd=1)
            info_item.pack(fill='x', pady=2)
            
            info_content = tk.Frame(info_item, bg=CompactStyle.COLORS['bg_main'])
            info_content.pack(fill='x', padx=15, pady=8)
            
            label_widget = tk.Label(info_content, text=f"{label}:",
                                   bg=CompactStyle.COLORS['bg_main'], fg=CompactStyle.COLORS['text_primary'],
                                   font=CompactStyle.FONTS['body'])
            label_widget.pack(side='left')
            
            value_widget = tk.Label(info_content, text=value,
                                   bg=CompactStyle.COLORS['bg_main'], fg=CompactStyle.COLORS['text_accent'],
                                   font=CompactStyle.FONTS['body_bold'])
            value_widget.pack(side='right')
    
    def setup_training_section(self, parent):
        """Setup training section"""
        training_frame = self.create_card_tab(parent, "🎓 Training Mode")
        
        training_container = tk.Frame(training_frame, bg=CompactStyle.COLORS['bg_card'])
        training_container.pack(fill='x', padx=15, pady=15)
        
        desc_label = tk.Label(training_container, 
                             text="Practice your gestures to improve recognition accuracy.\nThe training mode provides real-time feedback on your hand positions.",
                             bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_primary'],
                             font=CompactStyle.FONTS['body'], justify='left')
        desc_label.pack(anchor='w', pady=(0, 15))
        
        training_button = self.create_button(training_container, "🎯 Open Training Window", self.start_training,
                                           bg=CompactStyle.COLORS['bg_info'])
        training_button.pack()
    
    def setup_status_bar(self):
        """Setup status bar"""
        status_frame = tk.Frame(self.root, bg=CompactStyle.COLORS['bg_header'], height=25)
        status_frame.pack(side='bottom', fill='x')
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Ready to start")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               bg=CompactStyle.COLORS['bg_header'], fg=CompactStyle.COLORS['text_white'],
                               font=CompactStyle.FONTS['small'])
        status_label.pack(side='left', padx=10, pady=4)
        
        # Time
        self.time_var = tk.StringVar()
        time_label = tk.Label(status_frame, textvariable=self.time_var,
                             bg=CompactStyle.COLORS['bg_header'], fg=CompactStyle.COLORS['text_white'],
                             font=CompactStyle.FONTS['small'])
        time_label.pack(side='right', padx=10, pady=4)
        
        self.update_time()
    
    def create_card_tab(self, parent, title):
        """Create a card container for tabs"""
        card_frame = tk.Frame(parent, bg=CompactStyle.COLORS['bg_card'], 
                             relief='solid', bd=1)
        card_frame.pack(fill='x', padx=10, pady=5)
        
        # Header
        header_frame = tk.Frame(card_frame, bg=CompactStyle.COLORS['bg_header'])
        header_frame.pack(fill='x')
        
        title_label = tk.Label(header_frame, text=title,
                              bg=CompactStyle.COLORS['bg_header'], fg=CompactStyle.COLORS['text_white'],
                              font=CompactStyle.FONTS['heading'])
        title_label.pack(anchor='w', padx=15, pady=8)
        
        return card_frame
    
    def create_button(self, parent, text, command, bg=None, size='normal', **kwargs):
        """Create a styled button"""
        if bg is None:
            bg = CompactStyle.COLORS['bg_button']
        
        font = CompactStyle.FONTS['small'] if size == 'small' else CompactStyle.FONTS['body']
        padx = 8 if size == 'small' else 15
        pady = 4 if size == 'small' else 8
        
        button = tk.Button(parent, text=text, command=command,
                          bg=bg, fg=CompactStyle.COLORS['text_white'],
                          font=font, relief='flat', bd=0,
                          padx=padx, pady=pady, cursor='hand2',
                          **kwargs)
        
        # Hover effects
        def on_enter(e):
            button.config(bg=self.darken_color(bg))
        
        def on_leave(e):
            button.config(bg=bg)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def create_settings_slider(self, parent, title, setting_key, min_val, max_val, description):
        """Create a settings slider with description"""
        slider_frame = tk.Frame(parent, bg=CompactStyle.COLORS['bg_card'])
        slider_frame.pack(fill='x', pady=(0, 15))
        
        # Title and value on same line
        title_frame = tk.Frame(slider_frame, bg=CompactStyle.COLORS['bg_card'])
        title_frame.pack(fill='x')
        
        title_label = tk.Label(title_frame, text=title + ":",
                              bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_primary'],
                              font=CompactStyle.FONTS['body_bold'])
        title_label.pack(side='left')
        
        current_value = self.settings_manager.get(setting_key)
        value_label = tk.Label(title_frame, 
                              text=f"{current_value:.1f}" if setting_key != 'stability_zone' else str(int(current_value)),
                              bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_accent'],
                              font=CompactStyle.FONTS['body_bold'])
        value_label.pack(side='right')
        
        # Slider
        slider_var = tk.DoubleVar(value=current_value)
        slider = tk.Scale(slider_frame, from_=min_val, to=max_val, variable=slider_var,
                         orient='horizontal', resolution=0.1 if max_val <= 10 else 1,
                         bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_primary'],
                         highlightthickness=0, showvalue=0,
                         command=lambda val, key=setting_key, lbl=value_label: self.update_settings_slider(key, val, lbl))
        slider.pack(fill='x', pady=(5, 0))
        
        # Description
        desc_label = tk.Label(slider_frame, text=description,
                             bg=CompactStyle.COLORS['bg_card'], fg=CompactStyle.COLORS['text_secondary'],
                             font=CompactStyle.FONTS['small'])
        desc_label.pack(anchor='w', pady=(2, 0))
        
        # Store references
        setattr(self, f"{setting_key}_var", slider_var)
        setattr(self, f"{setting_key}_label", value_label)
    
    def darken_color(self, color):
        """Darken a color for hover effect"""
        color_map = {
            CompactStyle.COLORS['bg_button']: CompactStyle.COLORS['bg_button_hover'],
            CompactStyle.COLORS['bg_success']: '#229954',
            CompactStyle.COLORS['bg_danger']: '#c0392b',
            CompactStyle.COLORS['bg_warning']: '#d68910',
            CompactStyle.COLORS['bg_info']: '#7d3c98'
        }
        return color_map.get(color, color)
    
    def update_time(self):
        """Update time in status bar"""
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)
    
    def setup_emergency_stop(self):
        """Setup emergency stop hotkey"""
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.add_hotkey('ctrl+alt+q', self.emergency_stop)
                print("✅ Emergency hotkey (Ctrl+Alt+Q) registered")
            except Exception as e:
                print(f"⚠️ Could not setup emergency hotkey: {e}")
    
    # Event handlers
    def emergency_stop(self):
        """Emergency stop function"""
        self.stop_control()
        messagebox.showinfo("Emergency Stop", "Cursor control stopped via emergency hotkey!")
    
    def update_gpu_setting(self):
        """Update GPU setting"""
        self.settings_manager.set("use_gpu", self.gpu_var.get())
        self.settings_manager.save_settings()
        
        # Reinitialize gesture detector
        if self.gesture_detector:
            try:
                self.gesture_detector.cleanup()
            except:
                pass
        self.gesture_detector = GestureDetector(self.settings_manager.settings)
    
    def update_settings_slider(self, setting_key, value, label):
        """Update settings slider"""
        float_value = float(value)
        self.settings_manager.set(setting_key, float_value)
        self.settings_manager.save_settings()
        
        # Update label
        if setting_key == "stability_zone":
            label.config(text=str(int(float_value)))
        else:
            label.config(text=f"{float_value:.1f}")
    
    def update_resolution(self):
        """Update camera resolution"""
        res_str = self.resolution_var.get()
        width, height = map(int, res_str.split('x'))
        self.settings_manager.set("camera_resolution", [width, height])
        self.settings_manager.save_settings()
    
    def update_visual_feedback(self):
        """Update visual feedback setting"""
        self.settings_manager.set("show_visual_feedback", self.visual_var.get())
        self.settings_manager.save_settings()
    
    def test_bookmark(self, index):
        """Test opening a bookmark URL"""
        url = self.bookmark_entries[index].get().strip()
        if url:
            try:
                import webbrowser
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                webbrowser.open(url)
                messagebox.showinfo("Success", f"Opened bookmark {index+1} successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open URL: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Please enter a URL first")
    
    def clear_bookmark(self, index):
        """Clear a bookmark entry"""
        self.bookmark_entries[index].delete(0, 'end')
    
    def save_bookmarks(self):
        """Save all bookmark URLs"""
        bookmarks = []
        for entry in self.bookmark_entries:
            bookmarks.append(entry.get().strip())
        
        self.settings_manager.set("bookmarks", bookmarks)
        if self.settings_manager.save_settings():
            messagebox.showinfo("Success", "All bookmarks saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save bookmarks")
    
    def export_settings(self):
        """Export settings to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if self.settings_manager.export_settings(filename):
                messagebox.showinfo("Success", "Settings exported successfully!")
            else:
                messagebox.showerror("Error", "Failed to export settings")
    
    def import_settings(self):
        """Import settings from file"""
        filename = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            if self.settings_manager.import_settings(filename):
                messagebox.showinfo("Success", "Settings imported successfully!\nRestart the application to apply all changes.")
                self.refresh_gui()
            else:
                messagebox.showerror("Error", "Failed to import settings")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        result = messagebox.askyesno("Confirm Reset", 
                                    "Are you sure you want to reset all settings to defaults?\nThis action cannot be undone.")
        
        if result:
            if self.settings_manager.reset_to_defaults():
                messagebox.showinfo("Success", "Settings reset to defaults!\nRestart the application to apply all changes.")
                self.refresh_gui()
            else:
                messagebox.showerror("Error", "Failed to reset settings")
    
    def refresh_gui(self):
        """Refresh GUI with current settings"""
        try:
            # Update GUI elements with current settings
            self.gpu_var.set(self.settings_manager.get("use_gpu"))
            self.visual_var.set(self.settings_manager.get("show_visual_feedback"))
            
            # Update slider values
            for setting in ["cursor_sensitivity", "click_rate", "gesture_threshold", "stability_zone"]:
                var = getattr(self, f"{setting}_var", None)
                if var:
                    var.set(self.settings_manager.get(setting))
            
            # Update bookmark entries
            bookmarks = self.settings_manager.get("bookmarks")
            for i, entry in enumerate(self.bookmark_entries):
                entry.delete(0, 'end')
                if i < len(bookmarks):
                    entry.insert(0, bookmarks[i])
            
            # Update resolution
            res = self.settings_manager.get("camera_resolution")
            self.resolution_var.set(f"{res[0]}x{res[1]}")
        except Exception as e:
            print(f"Error refreshing GUI: {e}")
    
    def start_control(self):
        """Start cursor control"""
        if not self.is_running:
            try:
                self.is_running = True
                self.start_button.config(state='disabled', bg=CompactStyle.COLORS['text_secondary'])
                self.stop_button.config(state='normal', bg=CompactStyle.COLORS['bg_danger'])
                self.status_var.set("Starting cursor control...")
                
                # Ensure components are initialized
                if not self.camera_controller:
                    self.initialize_components()
                
                # Start camera controller
                if self.camera_controller and self.camera_controller.start_camera():
                    self.status_var.set("Cursor control active - Camera window opened")
                    self.start_performance_monitoring()
                else:
                    self.stop_control()
                    messagebox.showerror("Error", "Failed to start camera!")
            except Exception as e:
                self.stop_control()
                messagebox.showerror("Error", f"Failed to start cursor control: {str(e)}")
    
    def stop_control(self):
        """Stop cursor control"""
        if self.is_running:
            try:
                self.is_running = False
                self.start_button.config(state='normal', bg=CompactStyle.COLORS['bg_success'])
                self.stop_button.config(state='disabled', bg=CompactStyle.COLORS['text_secondary'])
                self.status_var.set("Stopping cursor control...")
                
                # Stop camera controller
                if self.camera_controller:
                    self.camera_controller.stop_camera()
                
                # Clean up gesture detector safely
                if self.gesture_detector:
                    try:
                        self.gesture_detector.cleanup()
                    except Exception as e:
                        print(f"Error during cleanup: {e}")
                
                self.status_var.set("Cursor control stopped")
            except Exception as e:
                print(f"Error stopping control: {e}")
                self.status_var.set("Error stopping cursor control")
    
    def start_training(self):
        """Start training mode"""
        try:
            if self.training_window is None or not hasattr(self.training_window, 'window') or not self.training_window.window.winfo_exists():
                self.training_window = TrainingWindow(self.root, self.settings_manager)
            else:
                self.training_window.window.lift()
                self.training_window.window.focus()
        except Exception as e:
            print(f"Error starting training: {e}")
            messagebox.showerror("Training Error", f"Failed to start training mode: {str(e)}")
    
    def start_performance_monitoring(self):
        """Start performance monitoring"""
        def update_performance():
            if self.is_running and self.camera_controller:
                try:
                    perf_data = self.camera_controller.get_performance_data()
                    self.fps_var.set(f"{perf_data['fps']:.1f}")
                    self.gesture_var.set(perf_data['gesture'])
                    self.confidence_var.set(f"{perf_data['confidence']:.0%}")
                except Exception as e:
                    print(f"Performance monitoring error: {e}")
                
                # Schedule next update
                self.root.after(1000, update_performance)
        
        update_performance()
    
    def on_closing(self):
        """Handle application closing"""
        try:
            if self.is_running:
                self.stop_control()
            
            # Save settings before closing
            self.settings_manager.save_settings()
            
            # Clean up emergency hotkey
            if KEYBOARD_AVAILABLE:
                try:
                    keyboard.unhook_all()
                except:
                    pass
            
            # Close training window if open
            if self.training_window and hasattr(self.training_window, 'window'):
                try:
                    if self.training_window.window.winfo_exists():
                        self.training_window.window.destroy()
                except:
                    pass
            
            self.root.destroy()
            print("👋 Application closed successfully")
        except Exception as e:
            print(f"Error during closing: {e}")
            self.root.destroy()