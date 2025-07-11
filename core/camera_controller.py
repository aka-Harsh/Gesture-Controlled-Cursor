"""
Camera Controller Module
Handles camera operations and video display
"""

import cv2
import threading
import time
import tkinter as tk
from tkinter import messagebox

class CameraController:
    def __init__(self, settings, gesture_detector):
        self.settings = settings
        self.gesture_detector = gesture_detector
        self.cap = None
        self.is_running = False
        self.camera_thread = None
        self.camera_window = None
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
    def initialize_camera(self):
        """Initialize camera with settings"""
        try:
            self.cap = cv2.VideoCapture(0)
            
            # Set camera resolution
            width, height = self.settings["camera_resolution"]
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Set FPS if possible
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.cap.isOpened():
                raise Exception("Cannot open camera")
            
            print("✅ Camera initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            messagebox.showerror("Camera Error", f"Failed to initialize camera:\n{str(e)}")
            return False
    
    def start_camera(self):
        """Start camera in a separate thread"""
        if not self.initialize_camera():
            return False
        
        self.is_running = True
        self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.camera_thread.start()
        return True
    
    def stop_camera(self):
        """Stop camera and cleanup safely"""
        print("🛑 Stopping camera...")
        self.is_running = False
        
        # Wait a moment for the camera loop to stop
        import time
        time.sleep(0.5)
        
        # Clean up camera
        if self.cap:
            try:
                self.cap.release()
                self.cap = None
            except Exception as e:
                print(f"Error releasing camera: {e}")
        
        # Close OpenCV windows
        try:
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Error closing windows: {e}")
        
        # Don't join the thread from within itself
        # Just set the flag and let it finish naturally
        
        print("🧹 Camera cleaned up")
    
    def _camera_loop(self):
        """Main camera loop with better error handling"""
        # Get screen size for cursor mapping
        import pyautogui
        wScr, hScr = pyautogui.size()
        
        # Create always-on-top camera window
        self._setup_camera_window()
        
        try:
            while self.is_running:
                if not self.cap or not self.cap.isOpened():
                    print("❌ Camera not available")
                    break
                
                success, img = self.cap.read()
                if not success:
                    print("❌ Failed to read camera frame")
                    break
                
                # Flip image for mirror effect (from original)
                img = cv2.flip(img, 1)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Process hand detection only if gesture detector is available
                if self.gesture_detector and self.gesture_detector.hands:
                    try:
                        result_hands = self.gesture_detector.hands.process(img_rgb)
                        h, w, _ = img.shape
                        
                        # Process gestures and get current gesture info
                        gesture_name, confidence = self.gesture_detector.process_gesture_commands(
                            result_hands, img, wScr, hScr, w, h
                        )
                    except Exception as e:
                        print(f"Gesture processing error: {e}")
                        gesture_name, confidence = "Error", 0.0
                else:
                    gesture_name, confidence = "No Detector", 0.0
                
                # Add UI elements to camera feed
                self._add_camera_ui(img, gesture_name, confidence)
                
                # Update performance counter
                self._update_fps()
                
                # Display the camera feed
                window_name = "🖱️ Gesture Cursor Controller - Camera Feed"
                cv2.imshow(window_name, img)
                
                # Make window always on top and non-minimizable
                self._maintain_window_properties()
                
                # Check for quit (but don't rely on it for stopping)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except Exception as e:
            print(f"Camera loop error: {e}")
        finally:
            # Clean shutdown
            self.is_running = False
            print("🎥 Camera loop ended")
    
    def _camera_loop(self):
        """Main camera loop"""
        # Get screen size for cursor mapping
        import pyautogui
        wScr, hScr = pyautogui.size()
        
        # Create always-on-top camera window
        self._setup_camera_window()
        
        while self.is_running:
            try:
                success, img = self.cap.read()
                if not success:
                    print("❌ Failed to read camera frame")
                    break
                
                # Flip image for mirror effect (from original)
                img = cv2.flip(img, 1)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Process hand detection
                result_hands = self.gesture_detector.hands.process(img_rgb)
                h, w, _ = img.shape
                
                # Process gestures and get current gesture info
                gesture_name, confidence = self.gesture_detector.process_gesture_commands(
                    result_hands, img, wScr, hScr, w, h
                )
                
                # Add UI elements to camera feed
                self._add_camera_ui(img, gesture_name, confidence)
                
                # Update performance counter
                self._update_fps()
                
                # Display the camera feed
                cv2.imshow("🖱️ Gesture Cursor Controller - Camera Feed", img)
                
                # Make window always on top and non-minimizable
                self._maintain_window_properties()
                
                # Check for quit (but don't rely on it for stopping)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            except Exception as e:
                print(f"Camera loop error: {e}")
                break
        
        self.stop_camera()
    
    def _setup_camera_window(self):
        """Setup camera window properties"""
        window_name = "🖱️ Gesture Cursor Controller - Camera Feed"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)
        
        # Try to set window properties (OS dependent)
        try:
            cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
        except:
            pass
    
    def _maintain_window_properties(self):
        """Maintain window always on top property"""
        try:
            window_name = "🖱️ Gesture Cursor Controller - Camera Feed"
            cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
        except:
            pass
    
    def _add_camera_ui(self, img, gesture_name, confidence):
        """Add UI elements to camera image"""
        # Add instructions overlay (from original but enhanced)
        overlay_alpha = 0.7
        overlay = img.copy()
        
        # Semi-transparent background for text
        cv2.rectangle(overlay, (10, 10), (630, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, overlay_alpha, img, 1 - overlay_alpha, 0, img)
        
        # Instructions text (from original)
        instructions = [
            "Point finger to move cursor",
            "Pinch to click", 
            "Peace sign for right click",
            "1-4 fingers for bookmarks",
            "All fingers to move cursor",
            "Press 'q' to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(img, instruction, (15, 35 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Current gesture info
        cv2.putText(img, f"Gesture: {gesture_name}", (15, 220), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, f"Confidence: {confidence:.1%}", (15, 250), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, f"FPS: {self.current_fps:.1f}", (15, 280), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Status indicator
        status_color = (0, 255, 0) if gesture_name != "None" else (0, 0, 255)
        cv2.circle(img, (600, 30), 10, status_color, -1)
        cv2.putText(img, "ACTIVE" if gesture_name != "None" else "IDLE", 
                   (550, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)
    
    def _update_fps(self):
        """Update FPS counter"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def get_performance_data(self):
        """Get current performance data"""
        return {
            "fps": self.current_fps,
            "gesture": self.gesture_detector.current_gesture,
            "confidence": self.gesture_detector.gesture_confidence
        }