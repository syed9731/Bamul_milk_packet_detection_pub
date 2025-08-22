#!/usr/bin/env python3
"""
Simple PiCamera2 Test Script
Tests basic functionality and checks for common errors
"""

import sys
import time

def test_picamera2_import():
    """Test PiCamera2 import"""
    print("🔍 Testing PiCamera2 import...")
    
    try:
        from picamera2 import Picamera2
        print("✅ PiCamera2 import successful")
        return True
    except ImportError as e:
        print(f"❌ PiCamera2 import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False

def test_picamera2_basic():
    """Test basic PiCamera2 functionality"""
    print("\n🔍 Testing basic PiCamera2 functionality...")
    
    try:
        from picamera2 import Picamera2
        
        # Create camera object
        print("  Creating Picamera2 object...")
        picam2 = Picamera2()
        print("  ✅ Picamera2 object created")
        
        # Test configuration creation
        print("  Testing configuration creation...")
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        print("  ✅ Configuration created successfully")
        
        # Check config attributes
        print("  Checking configuration attributes...")
        print(f"    Main size: {config.main['size']}")
        print(f"    Main format: {config.main['format']}")
        
        # Test camera configuration
        print("  Testing camera configuration...")
        picam2.configure(config)
        print("  ✅ Camera configured successfully")
        
        # Test camera start
        print("  Testing camera start...")
        picam2.start()
        print("  ✅ Camera started successfully")
        
        # Wait for camera to stabilize
        print("  Waiting for camera to stabilize...")
        time.sleep(2)
        
        # Test frame capture
        print("  Testing frame capture...")
        frame = picam2.capture_array()
        print(f"  ✅ Frame captured successfully: {frame.shape}")
        
        # Clean up
        picam2.close()
        print("  ✅ Camera closed successfully")
        
        return True
        
    except AttributeError as e:
        if "transform" in str(e):
            print(f"  ❌ Transform attribute error: {e}")
            print("  This indicates a libcamera/PiCamera2 version mismatch")
            return False
        else:
            print(f"  ❌ Attribute error: {e}")
            return False
    except Exception as e:
        print(f"  ❌ Error during testing: {e}")
        return False

def test_libcamera_info():
    """Test libcamera system info"""
    print("\n🔍 Testing libcamera system info...")
    
    try:
        import subprocess
        
        # Check libcamera-hello
        result = subprocess.run(['libcamera-hello', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ libcamera-hello version: {result.stdout.strip()}")
        else:
            print("❌ libcamera-hello not working")
            
    except FileNotFoundError:
        print("❌ libcamera-hello not found")
    except Exception as e:
        print(f"❌ Error checking libcamera: {e}")

def suggest_fixes():
    """Suggest fixes based on test results"""
    print("\n💡 Suggested Fixes:")
    print("=" * 40)
    
    print("1. Complete system update:")
    print("   sudo apt update && sudo apt full-upgrade -y")
    print("   sudo reboot")
    
    print("\n2. Reinstall PiCamera2:")
    print("   sudo apt remove python3-picamera2")
    print("   sudo apt autoremove")
    print("   sudo apt install python3-picamera2")
    
    print("\n3. Alternative pip install:")
    print("   pip3 install picamera2")
    
    print("\n4. Check camera interface:")
    print("   sudo raspi-config")
    print("   Interface Options → Camera → Enable")
    
    print("\n5. Check libcamera packages:")
    print("   dpkg -l | grep libcamera")

def main():
    """Main test function"""
    print("🧪 PiCamera2 Simple Test")
    print("=" * 40)
    
    # Test import
    if not test_picamera2_import():
        print("\n❌ PiCamera2 import failed. Check installation.")
        suggest_fixes()
        return
    
    # Test basic functionality
    if not test_picamera2_basic():
        print("\n❌ PiCamera2 basic functionality failed.")
        suggest_fixes()
        return
    
    # Test libcamera info
    test_libcamera_info()
    
    print("\n✅ All tests passed! PiCamera2 is working correctly.")
    print("You can now run your main detection script.")

if __name__ == "__main__":
    main() 