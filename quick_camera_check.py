#!/usr/bin/env python3
"""
Quick Camera Check Script
Identifies exactly what's missing for PiCamera2 to work
"""

import subprocess
import sys

def run_cmd(cmd):
    """Run command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except:
        return False, "", "Command failed"

def check_system_packages():
    """Check system camera packages"""
    print("🔍 System Camera Packages")
    print("=" * 40)
    
    # Check libcamera packages
    success, output, error = run_cmd("dpkg -l | grep libcamera")
    if success and output:
        print("✅ libcamera packages found:")
        for line in output.split('\n')[:5]:
            if line.strip():
                print(f"   {line}")
    else:
        print("❌ No libcamera packages found")
    
    # Check PiCamera2 packages
    success, output, error = run_cmd("dpkg -l | grep picamera")
    if success and output:
        print("✅ PiCamera2 packages found:")
        for line in output.split('\n')[:5]:
            if line.strip():
                print(f"   {line}")
    else:
        print("❌ No PiCamera2 packages found")

def check_camera_interface():
    """Check camera interface status"""
    print("\n🔍 Camera Interface Status")
    print("=" * 40)
    
    # Check vcgencmd camera status
    success, output, error = run_cmd("vcgencmd get_camera")
    if success:
        print(f"✅ Camera status: {output}")
        if "detected=1" in output:
            print("   Camera module detected")
        else:
            print("   Camera module NOT detected")
    else:
        print("❌ Could not check camera status")
    
    # Check video devices
    success, output, error = run_cmd("ls /dev/video* 2>/dev/null")
    if success and output:
        print(f"✅ Video devices: {output}")
    else:
        print("❌ No video devices found")

def check_python_packages():
    """Check Python camera packages"""
    print("\n🔍 Python Camera Packages")
    print("=" * 40)
    
    # Check PiCamera2 import
    try:
        import picamera2
        print(f"✅ PiCamera2 available: {picamera2.__version__}")
        print(f"   Path: {picamera2.__file__}")
    except ImportError:
        print("❌ PiCamera2 not available")
    except Exception as e:
        print(f"❌ PiCamera2 error: {e}")
    
    # Check libcamera import
    try:
        import libcamera
        print(f"✅ Python libcamera available: {libcamera.__version__}")
    except ImportError:
        print("❌ Python libcamera not available")
    except Exception as e:
        print(f"❌ Python libcamera error: {e}")

def check_libcamera_tools():
    """Check libcamera command-line tools"""
    print("\n🔍 libcamera Command Tools")
    print("=" * 40)
    
    # Check libcamera-hello
    success, output, error = run_cmd("libcamera-hello --version")
    if success:
        print(f"✅ libcamera-hello: {output}")
    else:
        print("❌ libcamera-hello not available")
    
    # Check libcamera-still
    success, output, error = run_cmd("libcamera-still --help 2>/dev/null | head -1")
    if success:
        print(f"✅ libcamera-still: {output}")
    else:
        print("❌ libcamera-still not available")

def suggest_fixes():
    """Suggest fixes based on findings"""
    print("\n💡 Required Fixes:")
    print("=" * 40)
    
    print("1. Install missing libcamera packages:")
    print("   sudo apt install -y libcamera0 libcamera-apps libcamera-tools")
    
    print("\n2. Install PiCamera2:")
    print("   sudo apt install -y python3-picamera2 python3-picamera2-libs")
    
    print("\n3. Alternative pip install:")
    print("   pip3 install picamera2")
    
    print("\n4. Enable camera interface:")
    print("   sudo raspi-config")
    print("   Interface Options → Camera → Enable")
    
    print("\n5. Complete system update:")
    print("   sudo apt update && sudo apt full-upgrade -y")
    print("   sudo reboot")

def main():
    """Main check function"""
    print("🔍 Quick Camera System Check")
    print("=" * 50)
    
    check_system_packages()
    check_camera_interface()
    check_python_packages()
    check_libcamera_tools()
    suggest_fixes()
    
    print("\n✅ Check complete! Apply the suggested fixes above.")

if __name__ == "__main__":
    main() 