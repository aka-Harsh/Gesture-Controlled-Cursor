import cv2
import sys

def test_camera():
    """Test if camera is working"""
    print("🔍 Testing camera...")
    
    # Try different camera backends
    backends = [
        (cv2.CAP_DSHOW, "DirectShow (Windows)"),
        (cv2.CAP_ANY, "Default backend"),
        (0, "Basic camera")
    ]
    
    for backend, name in backends:
        print(f"\n📹 Trying {name}...")
        
        try:
            if backend == 0:
                cap = cv2.VideoCapture(0)
            else:
                cap = cv2.VideoCapture(0, backend)
            
            if cap.isOpened():
                print(f"✅ {name} - SUCCESS")
                
                # Test reading frames
                ret, frame = cap.read()
                if ret:
                    h, w, c = frame.shape
                    print(f"   📐 Resolution: {w}x{h}")
                    print(f"   🎨 Channels: {c}")
                    
                    # Show camera feed for 3 seconds
                    print("   📺 Showing camera feed for 3 seconds...")
                    import time
                    start_time = time.time()
                    
                    while time.time() - start_time < 3:
                        ret, frame = cap.read()
                        if ret:
                            cv2.imshow("Camera Test", frame)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                    
                    cv2.destroyAllWindows()
                    cap.release()
                    print("   ✅ Camera test successful!")
                    return True
                else:
                    print(f"   ❌ {name} - Can't read frames")
            else:
                print(f"   ❌ {name} - Can't open camera")
            
            if cap:
                cap.release()
                
        except Exception as e:
            print(f"   ❌ {name} - Error: {e}")
    
    print("\n❌ No working camera found!")
    return False

def test_mediapipe():
    """Test MediaPipe installation"""
    print("\n🤖 Testing MediaPipe...")
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe imported successfully")
        
        # Test hands model
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        print("✅ MediaPipe Hands model loaded")
        hands.close()
        
        return True
    except Exception as e:
        print(f"❌ MediaPipe error: {e}")
        return False

def test_pyautogui():
    """Test PyAutoGUI"""
    print("\n🖱️ Testing PyAutoGUI...")
    
    try:
        import pyautogui
        
        # Get screen size
        width, height = pyautogui.size()
        print(f"✅ Screen size: {width}x{height}")
        
        # Test getting mouse position
        x, y = pyautogui.position()
        print(f"✅ Current mouse position: ({x}, {y})")
        
        return True
    except Exception as e:
        print(f"❌ PyAutoGUI error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Cursor Controller - System Test")
    print("=" * 40)
    
    # Test all components
    camera_ok = test_camera()
    mediapipe_ok = test_mediapipe()
    pyautogui_ok = test_pyautogui()
    
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS")
    print("=" * 40)
    print(f"📹 Camera: {'✅ PASS' if camera_ok else '❌ FAIL'}")
    print(f"🤖 MediaPipe: {'✅ PASS' if mediapipe_ok else '❌ FAIL'}")
    print(f"🖱️ PyAutoGUI: {'✅ PASS' if pyautogui_ok else '❌ FAIL'}")
    
    if camera_ok and mediapipe_ok and pyautogui_ok:
        print("\n🎉 All tests passed! Your system is ready.")
        print("💡 You can now run: python main.py")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        
        if not camera_ok:
            print("   📹 Camera: Check if webcam is connected and not used by other apps")
        if not mediapipe_ok:
            print("   🤖 MediaPipe: Try reinstalling with: pip install mediapipe")
        if not pyautogui_ok:
            print("   🖱️ PyAutoGUI: Try reinstalling with: pip install pyautogui")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()