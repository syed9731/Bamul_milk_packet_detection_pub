#!/usr/bin/env python3
"""
PiCamera2 v0.3.12 Specific Test Script
Tests for the transform attribute error and compatibility issues
"""

import sys
import time

def check_picamera2_details():
    """Check PiCamera2 installation details"""
    print("🔍 PiCamera2 Installation Details")
    print("=" * 50)
    
    try:
        import picamera2
        print(f"✅ PiCamera2 imported successfully")
        print(f"   Version: {picamera2.__version__}")
        print(f"   File path: {picamera2.__file__}")
        
        # Check if it's from apt or pip
        if '/usr/lib/python3/dist-packages/' in picamera2.__file__:
            print("   Source: apt package")
        elif '/usr/local/lib/python3' in picamera2.__file__:
            print("   Source: pip install")
        else:
            print("   Source: unknown")
            
        return True
        
    except ImportError as e:
        print(f"❌ PiCamera2 import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_libcamera_availability():
    """Check libcamera availability"""
    print("\n🔍 libcamera Availability Check")
    print("=" * 50)
    
    # Check system libcamera packages
    try:
        import subprocess
        result = subprocess.run(['dpkg', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            libcamera_packages = [line for line in result.stdout.split('\n') if 'libcamera' in line]
            if libcamera_packages:
                print("✅ libcamera packages found:")
                for pkg in libcamera_packages[:5]:  # Show first 5
                    print(f"   {pkg}")
            else:
                print("❌ No libcamera packages found")
        else:
            print("❌ Could not check system packages")
    except Exception as e:
        print(f"❌ Error checking packages: {e}")
    
    # Check Python libcamera
    try:
        import libcamera
        print(f"✅ Python libcamera available: {libcamera.__version__}")
    except ImportError:
        print("❌ Python libcamera not available")
    except Exception as e:
        print(f"❌ Error with Python libcamera: {e}")

def test_picamera2_configuration():
    """Test PiCamera2 configuration creation"""
    print("\n🔍 Testing PiCamera2 Configuration")
    print("=" * 50)
    
    try:
        from picamera2 import Picamera2
        
        print("  Creating Picamera2 object...")
        picam2 = Picamera2()
        print("  ✅ Picamera2 object created")
        
        print("  Testing basic configuration...")
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        print("  ✅ Basic configuration created")
        
        # Check config object
        print("  Checking configuration object...")
        print(f"    Type: {type(config)}")
        print(f"    Main size: {config.main['size']}")
        print(f"    Main format: {config.main['format']}")
        
        # Check for transform attribute
        print("  Checking for transform attribute...")
        if hasattr(config, 'transform'):
            print("  ✅ Transform attribute found")
            print(f"    Transform value: {config.transform}")
        else:
            print("  ❌ Transform attribute NOT found")
            print("  This is the source of your error!")
        
        # Check other attributes
        print("  Checking other attributes...")
        attrs = ['main', 'lores', 'raw', 'buffer_count']
        for attr in attrs:
            if hasattr(config, attr):
                print(f"    ✅ {attr}: {getattr(config, attr)}")
            else:
                print(f"    ❌ {attr}: Not found")
        
        return True
        
    except AttributeError as e:
        if "transform" in str(e):
            print(f"  ❌ Transform attribute error: {e}")
            print("  This confirms the compatibility issue!")
            return False
        else:
            print(f"  ❌ Other attribute error: {e}")
            return False
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_camera_initialization():
    """Test camera initialization"""
    print("\n🔍 Testing Camera Initialization")
    print("=" * 50)
    
    try:
        from picamera2 import Picamera2
        
        print("  Creating camera...")
        picam2 = Picamera2()
        
        print("  Creating configuration...")
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        
        print("  Configuring camera...")
        picam2.configure(config)
        print("  ✅ Camera configured successfully")
        
        print("  Starting camera...")
        picam2.start()
        print("  ✅ Camera started successfully")
        
        print("  Waiting for camera to stabilize...")
        time.sleep(2)
        
        print("  Testing frame capture...")
        frame = picam2.capture_array()
        print(f"  ✅ Frame captured: {frame.shape}")
        
        print("  Closing camera...")
        picam2.close()
        print("  ✅ Camera closed successfully")
        
        return True
        
    except AttributeError as e:
        if "transform" in str(e):
            print(f"  ❌ Transform attribute error during initialization: {e}")
            return False
        else:
            print(f"  ❌ Other attribute error: {e}")
            return False
    except Exception as e:
        print(f"  ❌ Initialization error: {e}")
        return False

def suggest_v0_3_12_fixes():
    """Suggest fixes specific to PiCamera2 v0.3.12"""
    print("\n💡 Fixes for PiCamera2 v0.3.12")
    print("=" * 40)
    
    print("1. Install missing libcamera dependencies:")
    print("   sudo apt install -y libcamera0 libcamera-apps libcamera-tools python3-libcamera")
    
    print("\n2. Reinstall PiCamera2 with dependencies:")
    print("   sudo apt remove python3-picamera2")
    print("   sudo apt autoremove")
    print("   sudo apt install -y python3-picamera2")
    
    print("\n3. Alternative: Use pip install:")
    print("   sudo apt remove python3-picamera2")
    print("   pip3 install picamera2")
    
    print("\n4. Check system compatibility:")
    print("   sudo apt update && sudo apt full-upgrade")
    print("   sudo reboot")
    
    print("\n5. Verify camera interface:")
    print("   sudo raspi-config")
    print("   Interface Options → Camera → Enable")

def main():
    """Main test function for v0.3.12"""
    print("🧪 PiCamera2 v0.3.12 Compatibility Test")
    print("=" * 60)
    
    # Check installation details
    if not check_picamera2_details():
        print("\n❌ PiCamera2 installation issue detected.")
        return
    
    # Check libcamera availability
    check_libcamera_availability()
    
    # Test configuration (this should trigger the transform error)
    if not test_picamera2_configuration():
        print("\n❌ Configuration issue confirmed - transform attribute missing.")
        suggest_v0_3_12_fixes()
        return
    
    # Test full camera initialization
    if not test_camera_initialization():
        print("\n❌ Camera initialization failed.")
        suggest_v0_3_12_fixes()
        return
    
    print("\n✅ All tests passed! PiCamera2 v0.3.12 is working correctly.")
    print("The transform attribute error should be resolved.")

if __name__ == "__main__":
    main() 