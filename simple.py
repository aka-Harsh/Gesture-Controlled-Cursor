import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math

def simple_cursor_control():
    """Simple cursor control without GUI"""
    
    # Get screen size
    wScr, hScr = pyautogui.size()
    print(f"🖥️ Screen size: {wScr}x{hScr}")
    
    # Initialize MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils
    
    # Initialize camera
    print("📹 Initializing camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open camera!")
        return False
    
    print("✅ Camera opened successfully")
    print("\n🎮 Controls:")
    print("   👆 Point finger - Move cursor")
    print("   🤏 Pinch - Left click")
    print("   ✌️ Peace sign - Right click")
    print("   ❌ Press 'q' to quit")
    print("\n🚀 Starting cursor control...")
    
    # Configure PyAutoGUI
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.01
    
    def get_distance(p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    
    try:
        while True:
            success, img = cap.read()
            if not success:
                print("❌ Failed to read frame")
                break
            
            # Flip image for mirror effect
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Process hand detection
            result_hands = hands.process(img_rgb)
            h, w, _ = img.shape
            
            if result_hands.multi_hand_landmarks:
                for hand_landmarks in result_hands.multi_hand_landmarks:
                    # Draw landmarks
                    mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Get landmark positions
                    lmList = []
                    for id, lm in enumerate(hand_landmarks.landmark):
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmList.append((cx, cy))
                    
                    if len(lmList) >= 21:
                        # Key positions
                        index_tip = lmList[8]    # Index finger tip
                        thumb_tip = lmList[4]    # Thumb tip
                        middle_tip = lmList[12]  # Middle finger tip
                        
                        x1, y1 = index_tip
                        x2, y2 = thumb_tip
                        x3, y3 = middle_tip
                        
                        # 1. Move cursor with index finger
                        screen_x = np.interp(x1, [0, w], [0, wScr])
                        screen_y = np.interp(y1, [0, h], [0, hScr])
                        pyautogui.moveTo(screen_x, screen_y)
                        
                        # Draw cursor indicator
                        cv2.circle(img, index_tip, 8, (0, 255, 0), -1)
                        cv2.putText(img, 'CURSOR', (x1 + 15, y1 - 15), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        # 2. Click with pinch
                        pinch_distance = get_distance(index_tip, thumb_tip)
                        if pinch_distance < 40:
                            pyautogui.click()
                            cv2.circle(img, index_tip, 15, (0, 0, 255), 3)
                            cv2.circle(img, thumb_tip, 15, (0, 0, 255), 3)
                            cv2.line(img, index_tip, thumb_tip, (0, 0, 255), 3)
                            cv2.putText(img, 'CLICK!', (x1, y1 - 40), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        # 3. Right click with peace sign
                        # Check finger states
                        fingers_up = []
                        # Thumb
                        fingers_up.append(1 if lmList[4][0] > lmList[3][0] else 0)
                        # Index
                        fingers_up.append(1 if lmList[8][1] < lmList[6][1] else 0)
                        # Middle
                        fingers_up.append(1 if lmList[12][1] < lmList[10][1] else 0)
                        # Ring
                        fingers_up.append(1 if lmList[16][1] < lmList[14][1] else 0)
                        # Pinky
                        fingers_up.append(1 if lmList[20][1] < lmList[18][1] else 0)
                        
                        # Peace sign: index and middle up, others down
                        if fingers_up == [0, 1, 1, 0, 0]:
                            pyautogui.rightClick()
                            cv2.putText(img, 'RIGHT CLICK!', (x1, y1 - 80), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Show instructions on screen
            cv2.putText(img, "Point finger to move cursor", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(img, "Pinch to click", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(img, "Peace sign for right click", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(img, "Press 'q' to quit", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display image
            cv2.imshow("Simple Cursor Controller", img)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        print("🧹 Cleaned up resources")
    
    return True

if __name__ == "__main__":
    print("🖱️ Simple Cursor Controller")
    print("=" * 30)
    
    if simple_cursor_control():
        print("✅ Cursor controller finished successfully")
    else:
        print("❌ Cursor controller failed to start")
    
    input("Press Enter to exit...")