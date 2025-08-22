#!/usr/bin/env python3
"""
Camera Diagnostic Script for Raspberry Pi
Helps troubleshoot PiCamera and OpenCV camera issues
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and return result"""
    print(f"\n🔍 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Success: {result.stdout.strip()}")
            return result.stdout.strip()
        else:
            print(f"❌ Error: {result.stderr.strip()}")
            return None
    except subprocess.TimeoutExpired:
        print("⏰ Timeout: Command took too long")
        return None
    except Exception as e:
        print(f"💥 Exception: {e}")
        return None

def check_system_info():
    """Check basic system information"""
    print("🖥️  System Information")
    print("=" * 50)
    
    # Check OS
    if os.path.exists('/etc/os-release'):
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('PRETTY_NAME'):
                    print(f"OS: {line.split('=')[1].strip().strip('\"')}")
                    break
    
    # Check Python version
    print(f"Python: {sys.version}")
    
    # Check if running on Pi
    if os.path.exists('/proc/device-tree/model'):
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
            print(f"Device: {model}")

def check_camera_hardware():
    """Check camera hardware status"""
    print("\n📷 Camera Hardware Check")
    print("=" * 50)
    
    # Check vcgencmd camera status
    camera_status = run_command("vcgencmd get_camera", "Camera hardware status")
    
    if camera_status:
        if "detected=1" in camera_status:
            print("✅ Camera module detected")
        else:
            print("❌ Camera module NOT detected")
            
        if "supported=1" in camera_status:
            print("✅ Camera module supported")
        else:
            print("❌ Camera module NOT supported")
    
    # Check video devices
    video_devices = run_command("ls /dev/video*", "Video devices")
    
    if video_devices:
        print(f"✅ Video devices found: {video_devices}")
    else:
        print("❌ No video devices found")
    
    # Check camera interface
    camera_interface = run_command("ls /dev/video* 2>/dev/null | wc -l", "Number of video devices")
    if camera_interface and camera_interface.strip() != "0":
        print(f"✅ Found {camera_interface.strip()} video device(s)")
    else:
        print("❌ No video devices available")

def check_camera_software():
    """Check camera software availability"""
    print("\n💻 Camera Software Check")
    print("=" * 50)
    
    # Check PiCamera2
    try:
        import picamera2
        print("✅ PiCamera2 is available")
        
        # Try to initialize
        try:
            from picamera2 import Picamera2
            print("✅ PiCamera2 can be imported")
        except Exception as e:
            print(f"❌ PiCamera2 import error: {e}")
            
    except ImportError:
        print("❌ PiCamera2 is NOT available")
        print("   Install with: sudo apt install python3-picamera2")
    
    # Check OpenCV
    try:
        import cv2
        print("✅ OpenCV is available")
        print(f"   Version: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV is NOT available")
        print("   Install with: pip3 install opencv-python")
    
    # Check numpy
    try:
        import numpy as np
        print("✅ NumPy is available")
    except ImportError:
        print("❌ NumPy is NOT available")
        print("   Install with: pip3 install numpy")

def test_camera_interfaces():
    """Test actual camera interfaces"""
    print("\n🧪 Camera Interface Testing")
    print("=" * 50)
    
    # Test OpenCV camera
    print("\n📹 Testing OpenCV Camera...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ OpenCV camera opened successfully")
            
            # Get camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"   Resolution: {width}x{height}")
            print(f"   FPS: {fps:.1f}")
            
            # Try to capture a frame
            ret, frame = cap.read()
            if ret:
                print("✅ Frame capture successful")
                print(f"   Frame shape: {frame.shape}")
            else:
                print("❌ Frame capture failed")
            
            cap.release()
        else:
            print("❌ OpenCV camera failed to open")
    except Exception as e:
        print(f"❌ OpenCV camera test error: {e}")
    
    # Test PiCamera2
    print("\n📷 Testing PiCamera2...")
    try:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        print("✅ PiCamera2 object created")
        
        # Try to configure
        try:
            config = picam2.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
            print("✅ PiCamera2 configuration created")
            
            # Try to configure camera
            picam2.configure(config)
            print("✅ PiCamera2 configured successfully")
            
            # Try to start
            picam2.start()
            print("✅ PiCamera2 started successfully")
            
            # Wait a moment
            time.sleep(1)
            
            # Try to capture
            try:
                frame = picam2.capture_array()
                print("✅ PiCamera2 frame capture successful")
                print(f"   Frame shape: {frame.shape}")
            except Exception as e:
                print(f"❌ PiCamera2 frame capture failed: {e}")
            
            # Clean up
            picam2.close()
            print("✅ PiCamera2 closed successfully")
            
        except Exception as e:
            print(f"❌ PiCamera2 configuration error: {e}")
            
    except Exception as e:
        print(f"❌ PiCamera2 test error: {e}")

def check_permissions():
    """Check camera permissions"""
    print("\n🔐 Permission Check")
    print("=" * 50)
    
    # Check if user is in video group
    groups = run_command("groups", "User groups")
    if groups and "video" in groups:
        print("✅ User is in video group")
    else:
        print("❌ User is NOT in video group")
        print("   Fix with: sudo usermod -a -G video $USER")
    
    # Check video device permissions
    video_perms = run_command("ls -la /dev/video* 2>/dev/null", "Video device permissions")
    if video_perms:
        print("✅ Video device permissions:")
        print(video_perms)
    else:
        print("❌ No video devices found for permission check")

def suggest_solutions():
    """Suggest solutions based on findings"""
    print("\n💡 Suggested Solutions")
    print("=" * 50)
    
    print("1. Enable Camera in raspi-config:")
    print("   sudo raspi-config")
    print("   Interface Options → Camera → Enable → Reboot")
    
    print("\n2. Install PiCamera2:")
    print("   sudo apt update")
    print("   sudo apt install python3-picamera2")
    
    print("\n3. Add user to video group:")
    print("   sudo usermod -a -G video $USER")
    print("   # Then logout/login or reboot")
    
    print("\n4. Check camera ribbon cable connection")
    print("   - Ensure cable is seated properly")
    print("   - Try reseating the camera module")
    
    print("\n5. Test with simple command:")
    print("   python3 test_camera.py")
    
    print("\n6. Check for camera conflicts:")
    print("   sudo pkill -f picamera")
    print("   sudo pkill -f python3")

def main():
    """Main diagnostic function"""
    print("🔍 Raspberry Pi Camera Diagnostic Tool")
    print("=" * 60)
    
    check_system_info()
    check_camera_hardware()
    check_camera_software()
    test_camera_interfaces()
    check_permissions()
    suggest_solutions()
    
    print("\n✅ Diagnostic complete!")
    print("Check the output above for issues and solutions.")

if __name__ == "__main__":
    main() 