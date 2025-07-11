"""
Training Window Module
Provides gesture training and practice mode
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import threading
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gesture_detector import GestureDetector

class TrainingWindow:
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings_manager = settings_manager
        
        # Create training window
        self.window = tk.Toplevel(parent)
        self.setup_window()
        
        # Initialize components
        self.gesture_detector = GestureDetector(settings_manager.settings)
        self.cap = None
        self.is_training = False
        self.training_thread = None
        
        # Training statistics
        self.gesture_stats = {
            "One Finger": 0,
            "Two Fingers": 0,
            "Three Fingers": 0,
            "Four Fingers": 0,
            "All Fingers": 0,
            "Pinch": 0,
            "Peace": 0,
            "Fist": 0
        }
        
        # Setup GUI
        self.setup_gui()
        
        # Bind close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        print("🎓 Training window initialized")
    
    def setup_window(self):
        """Setup training window properties"""
        self.window.title("🎓 Gesture Training Mode")
        self.window.geometry("800x700")
        self.window.minsize(600, 500)
        
        # Center window relative to parent
        self.window.transient(self.parent)
        
        # Position relative to parent
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        x = parent_x + 50
        y = parent_y + 50
        self.window.geometry(f"800x700+{x}+{y}")
        
        # Color scheme (matching main window)
        self.colors = {
            'primary': '#2563eb',
            'secondary': '#f59e0b',
            'success': '#10b981',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'info': '#06b6d4',
            'light': '#f8fafc',
            'dark': '#1e293b',
            'background': '#ffffff',
            'surface': '#f1f5f9'
        }
        
        self.window.configure(bg=self.colors['light'])
    
    def setup_gui(self):
        """Setup training GUI"""
        # Header
        self.setup_header()
        
        # Main content
        self.setup_content()
        
        # Control panel
        self.setup_control_panel()
        
        # Statistics panel
        self.setup_statistics_panel()
    
    def setup_header(self):
        """Setup header section"""
        header_frame = tk.Frame(self.window, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text="🎓 Gesture Training Mode",
                              bg=self.colors['primary'], fg='white',
                              font=('Segoe UI', 18, 'bold'))
        title_label.pack(side='left', padx=20, pady=20)
        
        # Status indicator
        self.training_status_var = tk.StringVar(value="Ready to start training")
        status_label = tk.Label(header_frame, textvariable=self.training_status_var,
                               bg=self.colors['primary'], fg='white',
                               font=('Segoe UI', 12))
        status_label.pack(side='right', padx=20, pady=20)
    
    def setup_content(self):
        """Setup main content area"""
        content_frame = tk.Frame(self.window, bg=self.colors['light'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Instructions card
        self.setup_instructions_card(content_frame)
        
        # Current gesture display
        self.setup_gesture_display_card(content_frame)
    
    def setup_instructions_card(self, parent):
        """Setup instructions card"""
        instructions_frame = self.create_card(parent, "📖 Training Instructions")
        
        instructions_text = """
Welcome to Gesture Training Mode! This mode helps you practice and perfect your hand gestures.

🎯 How to use Training Mode:
1. Click 'Start Training' to begin camera capture
2. Position your hand clearly in front of the camera
3. Practice different gestures and watch the real-time feedback
4. Try to achieve high confidence scores (above 80%)
5. The system will track your gesture accuracy and provide tips

💡 Tips for better gesture recognition:
• Ensure good lighting conditions
• Keep your hand within the camera frame
• Make distinct, clear gestures
• Hold gestures steady for better recognition
• Practice each gesture multiple times
        """
        
        instructions_label = tk.Label(instructions_frame, text=instructions_text,
                                     bg=self.colors['background'], fg=self.colors['dark'],
                                     font=('Segoe UI', 10), justify='left', anchor='nw')
        instructions_label.pack(fill='both', expand=True, padx=20, pady=15)
    
    def setup_gesture_display_card(self, parent):
        """Setup current gesture display card"""
        gesture_frame = self.create_card(parent, "🤚 Current Gesture Detection")
        
        # Gesture info container
        info_container = tk.Frame(gesture_frame, bg=self.colors['background'])
        info_container.pack(fill='x', padx=20, pady=15)
        
        # Current gesture
        self.current_gesture_var = tk.StringVar(value="None")
        gesture_label = tk.Label(info_container, text="Current Gesture:",
                                bg=self.colors['background'], fg=self.colors['dark'],
                                font=('Segoe UI', 12, 'bold'))
        gesture_label.pack(anchor='w')
        
        gesture_value_label = tk.Label(info_container, textvariable=self.current_gesture_var,
                                      bg=self.colors['background'], fg=self.colors['primary'],
                                      font=('Segoe UI', 16, 'bold'))
        gesture_value_label.pack(anchor='w', pady=(5, 15))
        
        # Confidence
        self.confidence_var = tk.StringVar(value="0%")
        confidence_label = tk.Label(info_container, text="Recognition Confidence:",
                                   bg=self.colors['background'], fg=self.colors['dark'],
                                   font=('Segoe UI', 12, 'bold'))
        confidence_label.pack(anchor='w')
        
        confidence_value_label = tk.Label(info_container, textvariable=self.confidence_var,
                                         bg=self.colors['background'], fg=self.colors['success'],
                                         font=('Segoe UI', 16, 'bold'))
        confidence_value_label.pack(anchor='w', pady=(5, 15))
        
        # Tips
        self.tips_var = tk.StringVar(value="Position your hand clearly in front of the camera")
        tips_label = tk.Label(info_container, text="Tip:",
                             bg=self.colors['background'], fg=self.colors['dark'],
                             font=('Segoe UI', 12, 'bold'))
        tips_label.pack(anchor='w')
        
        tips_value_label = tk.Label(info_container, textvariable=self.tips_var,
                                   bg=self.colors['background'], fg=self.colors['info'],
                                   font=('Segoe UI', 11), wraplength=600, justify='left')
        tips_value_label.pack(anchor='w', pady=(5, 0))
    
    def setup_control_panel(self):
        """Setup control panel"""
        control_frame = tk.Frame(self.window, bg=self.colors['light'])
        control_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Control buttons
        button_container = tk.Frame(control_frame, bg=self.colors['light'])
        button_container.pack()
        
        # Start training button
        self.start_training_button = tk.Button(button_container,
                                              text="🎯 Start Training",
                                              command=self.start_training,
                                              bg=self.colors['success'], fg='white',
                                              font=('Segoe UI', 12, 'bold'),
                                              relief='flat', padx=20, pady=10,
                                              cursor='hand2')
        self.start_training_button.pack(side='left', padx=(0, 10))
        
        # Stop training button
        self.stop_training_button = tk.Button(button_container,
                                             text="⏹️ Stop Training",
                                             command=self.stop_training,
                                             bg=self.colors['danger'], fg='white',
                                             font=('Segoe UI', 12, 'bold'),
                                             relief='flat', padx=20, pady=10,
                                             cursor='hand2', state='disabled')
        self.stop_training_button.pack(side='left', padx=(0, 10))
        
        # Reset stats button
        self.reset_stats_button = tk.Button(button_container,
                                           text="🔄 Reset Statistics",
                                           command=self.reset_statistics,
                                           bg=self.colors['warning'], fg='white',
                                           font=('Segoe UI', 12, 'bold'),
                                           relief='flat', padx=20, pady=10,
                                           cursor='hand2')
        self.reset_stats_button.pack(side='left')
    
    def setup_statistics_panel(self):
        """Setup statistics panel"""
        stats_frame = self.create_card(self.window, "📊 Training Statistics")
        
        # Statistics container
        stats_container = tk.Frame(stats_frame, bg=self.colors['background'])
        stats_container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Create statistics display
        self.stats_labels = {}
        
        # Create two columns for statistics
        left_column = tk.Frame(stats_container, bg=self.colors['background'])
        left_column.pack(side='left', fill='both', expand=True)
        
        right_column = tk.Frame(stats_container, bg=self.colors['background'])
        right_column.pack(side='right', fill='both', expand=True)
        
        # Split gestures between columns
        gestures_left = ["One Finger", "Two Fingers", "Three Fingers", "Four Fingers"]
        gestures_right = ["All Fingers", "Pinch", "Peace", "Fist"]
        
        for i, gesture in enumerate(gestures_left):
            self.create_stat_item(left_column, gesture)
        
        for i, gesture in enumerate(gestures_right):
            self.create_stat_item(right_column, gesture)
    
    def create_stat_item(self, parent, gesture_name):
        """Create a statistics item"""
        item_frame = tk.Frame(parent, bg=self.colors['surface'], relief='solid', bd=1)
        item_frame.pack(fill='x', padx=5, pady=2)
        
        # Gesture name
        name_label = tk.Label(item_frame, text=gesture_name,
                             bg=self.colors['surface'], fg=self.colors['dark'],
                             font=('Segoe UI', 10, 'bold'))
        name_label.pack(side='left', padx=10, pady=5)
        
        # Count
        count_var = tk.StringVar(value="0")
        count_label = tk.Label(item_frame, textvariable=count_var,
                              bg=self.colors['surface'], fg=self.colors['primary'],
                              font=('Segoe UI', 10, 'bold'))
        count_label.pack(side='right', padx=10, pady=5)
        
        self.stats_labels[gesture_name] = count_var
    
    def create_card(self, parent, title):
        """Create a card container"""
        card_frame = tk.Frame(parent, bg=self.colors['background'], relief='solid', bd=1)
        card_frame.pack(fill='x', pady=5)
        
        # Header
        header_frame = tk.Frame(card_frame, bg=self.colors['primary'])
        header_frame.pack(fill='x')
        
        title_label = tk.Label(header_frame, text=title,
                              bg=self.colors['primary'], fg='white',
                              font=('Segoe UI', 12, 'bold'))
        title_label.pack(anchor='w', padx=15, pady=8)
        
        return card_frame
    
    def start_training(self):
        """Start training mode"""
        if not self.is_training:
            self.is_training = True
            self.start_training_button.config(state='disabled')
            self.stop_training_button.config(state='normal')
            self.training_status_var.set("Training active - Camera starting...")
            
            # Start training thread
            self.training_thread = threading.Thread(target=self.training_loop, daemon=True)
            self.training_thread.start()
    
    def stop_training(self):
        """Stop training mode safely"""
        if self.is_training:
            self.is_training = False
            self.start_training_button.config(state='normal')
            self.stop_training_button.config(state='disabled')
            self.training_status_var.set("Training stopped")
            
            # Clean up camera safely
            try:
                if self.cap:
                    self.cap.release()
                    self.cap = None
            except Exception as e:
                print(f"Error releasing training camera: {e}")
            
            try:
                cv2.destroyAllWindows()
            except Exception as e:
                print(f"Error closing training windows: {e}")
    
    def on_closing(self):
        """Handle window closing safely"""
        try:
            if self.is_training:
                self.stop_training()
            
            # Clean up gesture detector safely
            if self.gesture_detector:
                try:
                    self.gesture_detector.cleanup()
                except Exception as e:
                    print(f"Training cleanup error: {e}")
            
            # Destroy window
            self.window.destroy()
            print("🎓 Training window closed")
        except Exception as e:
            print(f"Error closing training window: {e}")
            try:
                self.window.destroy()
            except:
                pass
    
    def training_loop(self):
        """Main training loop"""
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            
            # Set camera resolution
            width, height = self.settings_manager.get("camera_resolution")
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            if not self.cap.isOpened():
                messagebox.showerror("Camera Error", "Cannot open camera for training!")
                self.stop_training()
                return
            
            self.training_status_var.set("Training active - Practice your gestures!")
            
            while self.is_training:
                success, img = self.cap.read()
                if not success:
                    break
                
                # Flip image for mirror effect
                img = cv2.flip(img, 1)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Process hand detection
                result_hands = self.gesture_detector.hands.process(img_rgb)
                h, w, _ = img.shape
                
                gesture_name = "None"
                confidence = 0.0
                
                if result_hands.multi_hand_landmarks:
                    for hand_landmarks in result_hands.multi_hand_landmarks:
                        # Draw landmarks
                        self.gesture_detector.mp_draw.draw_landmarks(
                            img, hand_landmarks, self.gesture_detector.mp_hands.HAND_CONNECTIONS)
                        
                        # Detect gesture
                        gesture_name, confidence, lmList = self.gesture_detector.detect_gesture(hand_landmarks, w, h)
                        
                        # Update statistics if confidence is high enough
                        if confidence > 0.7 and gesture_name in self.gesture_stats:
                            self.gesture_stats[gesture_name] += 1
                
                # Update GUI
                self.update_training_display(gesture_name, confidence)
                
                # Add training overlay to image
                self.add_training_overlay(img, gesture_name, confidence)
                
                # Display image
                cv2.imshow("🎓 Gesture Training - Camera Feed", img)
                
                # Make window stay on top
                try:
                    cv2.setWindowProperty("🎓 Gesture Training - Camera Feed", cv2.WND_PROP_TOPMOST, 1)
                except:
                    pass
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        except Exception as e:
            messagebox.showerror("Training Error", f"Training error: {str(e)}")
        finally:
            self.stop_training()
    
    def update_training_display(self, gesture_name, confidence):
        """Update training display with current gesture info"""
        self.current_gesture_var.set(gesture_name)
        self.confidence_var.set(f"{confidence:.1%}")
        
        # Update tips based on confidence
        if confidence < 0.5:
            self.tips_var.set("Make your gesture more distinct and clear. Ensure good lighting.")
        elif confidence < 0.7:
            self.tips_var.set("Good! Try to hold the gesture more steadily for better recognition.")
        elif confidence < 0.9:
            self.tips_var.set("Great! Your gesture is being recognized well. Keep practicing!")
        else:
            self.tips_var.set("Excellent! Perfect gesture recognition. Try the next gesture!")
        
        # Update statistics display
        for gesture, count in self.gesture_stats.items():
            if gesture in self.stats_labels:
                self.stats_labels[gesture].set(str(count))
    
    def add_training_overlay(self, img, gesture_name, confidence):
        """Add training overlay to camera image"""
        # Semi-transparent background for text
        overlay = img.copy()
        cv2.rectangle(overlay, (10, 10), (630, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
        
        # Training info
        cv2.putText(img, "🎓 TRAINING MODE", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        cv2.putText(img, f"Current Gesture: {gesture_name}", (20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.putText(img, f"Confidence: {confidence:.1%}", (20, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Confidence indicator
        confidence_color = (0, 255, 0) if confidence > 0.8 else (0, 255, 255) if confidence > 0.5 else (0, 0, 255)
        quality_text = "EXCELLENT" if confidence > 0.8 else "GOOD" if confidence > 0.5 else "PRACTICE MORE"
        cv2.putText(img, f"Quality: {quality_text}", (20, 130),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, confidence_color, 2)
        
        # Instructions
        cv2.putText(img, "Press 'q' to close camera", (450, 130),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def reset_statistics(self):
        """Reset training statistics"""
        result = messagebox.askyesno("Reset Statistics", 
                                    "Are you sure you want to reset all training statistics?")
        if result:
            for gesture in self.gesture_stats:
                self.gesture_stats[gesture] = 0
            
            # Update display
            for gesture, count in self.gesture_stats.items():
                if gesture in self.stats_labels:
                    self.stats_labels[gesture].set("0")
            
            messagebox.showinfo("Statistics Reset", "All training statistics have been reset!")
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_training:
            self.stop_training()
        
        # Clean up gesture detector
        self.gesture_detector.cleanup()
        
        self.window.destroy()
        print("🎓 Training window closed")