"""
Gesture Detection Module
Simplified with only working gestures
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time
import webbrowser

class GestureDetector:
    def __init__(self, settings):
        self.settings = settings
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = None
        
        # Cursor control variables (from original)
        self.prev_x = 0
        self.prev_y = 0
        self.last_click_time = 0
        self.last_right_click_time = 0
        self.last_gesture_time = 0
        self.current_gesture = "None"
        self.gesture_confidence = 0
        
        # Initialize MediaPipe based on GPU setting
        self.initialize_mediapipe()
        
        # Configure PyAutoGUI (from original)
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
    
    def initialize_mediapipe(self):
        """Initialize MediaPipe with appropriate settings"""
        try:
            if self.settings["use_gpu"]:
                self.hands = self.mp_hands.Hands(
                    max_num_hands=1, 
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.5,
                    model_complexity=1
                )
            else:
                self.hands = self.mp_hands.Hands(
                    max_num_hands=1, 
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.5
                )
            print("✅ MediaPipe hands initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing MediaPipe: {e}")
            self.hands = None
    
    def get_distance(self, p1, p2):
        """Calculate distance between two points (from original)"""
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    
    def detect_fingers(self, lmList):
        """Detect finger states (from original logic)"""
        if len(lmList) < 21:
            return []
        
        fingers_up = []
        
        # Thumb (from original)
        fingers_up.append(1 if lmList[4][0] > lmList[3][0] else 0)
        
        # Index (from original)
        fingers_up.append(1 if lmList[8][1] < lmList[6][1] else 0)
        
        # Middle (from original)
        fingers_up.append(1 if lmList[12][1] < lmList[10][1] else 0)
        
        # Ring (from original)
        fingers_up.append(1 if lmList[16][1] < lmList[14][1] else 0)
        
        # Pinky (from original)
        fingers_up.append(1 if lmList[20][1] < lmList[18][1] else 0)
        
        return fingers_up
    
    def detect_gesture(self, hand_landmarks, w, h):
        """Detect hand gesture - SIMPLIFIED with only working gestures"""
        lmList = []
        for id, lm in enumerate(hand_landmarks.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append((cx, cy))
        
        if len(lmList) < 21:
            return "Unknown", 0.0, lmList
        
        # Get finger states using original logic
        fingers_up = self.detect_fingers(lmList)
        finger_count = sum(fingers_up)
        
        # Get key positions (from original)
        index_tip = lmList[8]
        thumb_tip = lmList[4]
        pinky_tip = lmList[20]
        
        # Calculate pinch distance (from original)
        pinch_distance = self.get_distance(index_tip, thumb_tip)
        
        confidence = 0.9  # High confidence for working gestures
        
        # SIMPLIFIED GESTURE SET - Only 6 working gestures
        
        # 1. Pinch detection (from original) - LEFT CLICK
        if pinch_distance < 40:
            return "Pinch", confidence, lmList
        
        # 2. Pinky only - RIGHT CLICK  
        elif fingers_up == [0, 0, 0, 0, 1]:  # Only pinky up
            return "Pinky", confidence, lmList
        
        # 3. Index only - BOOKMARK 1
        elif fingers_up == [0, 1, 0, 0, 0]:  # Only index finger
            return "One Finger", confidence, lmList
        
        # 4. Index + Middle - BOOKMARK 2
        elif fingers_up == [0, 1, 1, 0, 0]:  # Index + Middle
            return "Two Fingers", confidence, lmList
        
        # 5. Index + Pinky (rock sign) - BOOKMARK 3
        elif fingers_up == [0, 1, 0, 0, 1]:  # Index + Pinky
            return "Index Pinky", confidence, lmList
        
        # 6. Four fingers (no thumb) - CURSOR MOVEMENT
        elif fingers_up == [0, 1, 1, 1, 1]:  # 4 fingers (no thumb)
            return "Four Fingers", confidence, lmList
        
        else:
            return "Unknown", 0.3, lmList
    
    def process_cursor_movement(self, lmList, wScr, hScr, w, h):
        """Process cursor movement (from original with smoothing)"""
        index_tip = lmList[8]
        x1, y1 = index_tip
        
        # Original screen mapping
        screen_x = np.interp(x1, [0, w], [0, wScr])
        screen_y = np.interp(y1, [0, h], [0, hScr])
        
        # Apply smoothing factor
        if self.prev_x == 0 and self.prev_y == 0:
            self.prev_x, self.prev_y = screen_x, screen_y
        
        smoothing_factor = self.settings["cursor_sensitivity"]
        smoothed_x = self.prev_x * (1 - smoothing_factor) + screen_x * smoothing_factor
        smoothed_y = self.prev_y * (1 - smoothing_factor) + screen_y * smoothing_factor
        
        # Apply stability zone
        distance_moved = self.get_distance((self.prev_x, self.prev_y), (smoothed_x, smoothed_y))
        if distance_moved > self.settings["stability_zone"]:
            pyautogui.moveTo(smoothed_x, smoothed_y)
            self.prev_x, self.prev_y = smoothed_x, smoothed_y
        
        return index_tip
    
    def process_left_click(self, lmList, img):
        """Process left click with rate limiting"""
        current_time = time.time()
        click_cooldown = 1.0 / self.settings["click_rate"]
        
        if current_time - self.last_click_time > click_cooldown:
            pyautogui.click()
            self.last_click_time = current_time
            
            if self.settings["show_visual_feedback"]:
                index_tip = lmList[8]
                thumb_tip = lmList[4]
                cv2.circle(img, index_tip, 15, (0, 0, 255), 3)
                cv2.circle(img, thumb_tip, 15, (0, 0, 255), 3)
                cv2.line(img, index_tip, thumb_tip, (0, 0, 255), 3)
                cv2.putText(img, 'LEFT CLICK!', (index_tip[0], index_tip[1] - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    def process_right_click(self, lmList, img):
        """Process right click with rate limiting"""
        current_time = time.time()
        click_cooldown = 1.0 / self.settings["click_rate"]
        
        if current_time - self.last_right_click_time > click_cooldown:
            pyautogui.rightClick()
            self.last_right_click_time = current_time
            
            if self.settings["show_visual_feedback"]:
                pinky_tip = lmList[20]
                cv2.circle(img, pinky_tip, 15, (255, 255, 0), 3)
                cv2.putText(img, 'RIGHT CLICK!', (pinky_tip[0], pinky_tip[1] - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    def process_bookmarks(self, gesture_name, img, lmList):
        """Process bookmark gestures - ONLY 3 BOOKMARKS"""
        current_time = time.time()
        bookmark_cooldown = 2.0  # 2 second cooldown for bookmarks
        
        gesture_to_index = {
            "One Finger": 0,      # Index finger → Bookmark 1
            "Two Fingers": 1,     # Index + Middle → Bookmark 2  
            "Index Pinky": 2      # Index + Pinky → Bookmark 3
        }
        
        if gesture_name in gesture_to_index:
            if current_time - self.last_gesture_time > bookmark_cooldown:
                bookmark_index = gesture_to_index[gesture_name]
                url = self.settings["bookmarks"][bookmark_index] if bookmark_index < len(self.settings["bookmarks"]) else ""
                
                if url:
                    try:
                        if not url.startswith(('http://', 'https://')):
                            url = 'https://' + url
                        webbrowser.open(url)
                        self.last_gesture_time = current_time
                        
                        if self.settings["show_visual_feedback"]:
                            cv2.putText(img, f'OPENING BOOKMARK {bookmark_index + 1}', 
                                       (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    except Exception as e:
                        print(f"Error opening bookmark: {e}")
    
    def process_gesture_commands(self, result_hands, img, wScr, hScr, w, h):
        """Main gesture processing function - SIMPLIFIED"""
        if not result_hands.multi_hand_landmarks:
            return "None", 0.0
        
        for hand_landmarks in result_hands.multi_hand_landmarks:
            # Draw landmarks
            if self.settings["show_visual_feedback"]:
                self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            # Detect gesture
            gesture_name, confidence, lmList = self.detect_gesture(hand_landmarks, w, h)
            
            # Only process if confidence is above threshold
            if confidence < self.settings["gesture_threshold"]:
                continue
            
            # Store current gesture info
            self.current_gesture = gesture_name
            self.gesture_confidence = confidence
            
            # Process gestures
            if gesture_name == "Four Fingers":
                # Move cursor
                cursor_pos = self.process_cursor_movement(lmList, wScr, hScr, w, h)
                
                if self.settings["show_visual_feedback"]:
                    cv2.circle(img, cursor_pos, 8, (0, 255, 0), -1)
                    cv2.putText(img, 'CURSOR', (cursor_pos[0] + 15, cursor_pos[1] - 15), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            elif gesture_name == "Pinch":
                # Left click
                self.process_left_click(lmList, img)
            
            elif gesture_name == "Pinky":
                # Right click  
                self.process_right_click(lmList, img)
            
            elif gesture_name in ["One Finger", "Two Fingers", "Index Pinky"]:
                # Bookmarks (only 3)
                self.process_bookmarks(gesture_name, img, lmList)
            
            return gesture_name, confidence
        
        return "None", 0.0
    
    def cleanup(self):
        """Clean up MediaPipe resources safely"""
        try:
            if self.hands:
                self.hands.close()
                print("✅ MediaPipe hands cleaned up")
        except Exception as e:
            print(f"Cleanup error (non-critical): {e}")
        finally:
            self.hands = None