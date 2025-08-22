#!/usr/bin/env python3
"""
Camera Configuration Checker for Raspberry Pi
Checks and fixes common camera configuration issues
"""

import subprocess
import os
import sys

def check_camera_config():
    """Check current camera configuration"""
    print("Checking camera configuration...")
    
    # Check if camera is enabled in config
    try:
        result = subprocess.run(['vcgencmd', 'get_camera'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Camera status: {result.stdout.strip()}")
        else:
            print("Could not get camera status via vcgencmd")
    except FileNotFoundError:
        print("vcgencmd not available")
    
    # Check camera device files
    camera_devices = []
    for i in range(10):  # Check first 10 video devices
        device = f"/dev/video{i}"
        if os.path.exists(device):
            camera_devices.append(device)
    
    if camera_devices:
        print(f"Camera devices found: {camera_devices}")
    else:
        print("No camera devices found")
    
    # Check camera firmware
    try:
        result = subprocess.run(['vcgencmd', 'version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Firmware version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("Could not get firmware version")
    
    # Check camera module info
    try:
        result = subprocess.run(['vcgencmd', 'get_mem', 'gpu'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"GPU memory: {result.stdout.strip()}")
    except FileNotFoundError:
        print("Could not get GPU memory info")

def check_camera_interface():
    """Check which camera interface is available"""
    print("\nChecking camera interfaces...")
    
    # Check for PiCamera2
    try:
        import picamera2
        print("✓ PiCamera2 is available")
        
        # Try to initialize
        try:
            from picamera2 import Picamera2
            picam2 = Picamera2()
            print("✓ PiCamera2 can be initialized")
            picam2.close()
        except Exception as e:
            print(f"✗ PiCamera2 initialization failed: {e}")
            
    except ImportError:
        print("✗ PiCamera2 is not available")
    
    # Check for OpenCV camera
    try:
        import cv2
        print("✓ OpenCV is available")
        
        # Try to open camera
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ OpenCV camera can be opened")
            cap.release()
        else:
            print("✗ OpenCV camera cannot be opened")
            
    except ImportError:
        print("✗ OpenCV is not available")

def suggest_fixes():
    """Suggest fixes for common camera issues"""
    print("\nSuggested fixes for color issues:")
    print("1. Check if camera module is properly connected")
    print("2. Ensure camera is enabled in raspi-config")
    print("3. Try different camera interfaces (PiCamera2 vs OpenCV)")
    print("4. Check camera firmware version")
    print("5. Verify camera module compatibility")
    
    print("\nFor color inversion issues specifically:")
    print("1. The code has been updated to handle both camera types")
    print("2. PiCamera2 outputs RGB, OpenCV outputs BGR")
    print("3. Run the updated code with --use-picamera2 flag")
    print("4. Or use OpenCV camera without the flag")

def main():
    print("Raspberry Pi Camera Configuration Checker")
    print("=" * 50)
    
    check_camera_config()
    check_camera_interface()
    suggest_fixes()
    
    print("\nTo test the color fix:")
    print("python3 test_color_fix.py")
    print("python3 raspberry_milk_detector.py --use-picamera2")

if __name__ == "__main__":
    main() 