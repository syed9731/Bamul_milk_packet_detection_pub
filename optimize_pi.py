#!/usr/bin/env python3
"""
Raspberry Pi Performance Optimizer for Milk Detection
Helps find optimal settings for real-time performance
"""

import subprocess
import time
import psutil
import os
import sys

def check_system_info():
    """Check Raspberry Pi system information"""
    print("🔍 Checking Raspberry Pi System Information...")
    
    try:
        # Check CPU info
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = f.read()
            if 'Raspberry Pi' in cpu_info:
                print("✅ Raspberry Pi detected")
            else:
                print("⚠️  Not running on Raspberry Pi")
        
        # Check memory
        memory = psutil.virtual_memory()
        print(f"💾 RAM: {memory.total / (1024**3):.1f} GB")
        
        # Check CPU cores
        cpu_count = psutil.cpu_count()
        print(f"🖥️  CPU Cores: {cpu_count}")
        
        # Check temperature
        try:
            temp = subprocess.check_output(['vcgencmd', 'measure_temp']).decode()
            print(f"🌡️  Temperature: {temp.strip()}")
        except:
            print("🌡️  Temperature: Unable to read")
            
        # Check GPU memory
        try:
            gpu_mem = subprocess.check_output(['vcgencmd', 'get_mem', 'gpu']).decode()
            print(f"🎮 GPU Memory: {gpu_mem.strip()}")
        except:
            print("🎮 GPU Memory: Unable to read")
            
    except Exception as e:
        print(f"❌ Error checking system info: {e}")

def check_camera():
    """Check camera availability"""
    print("\n📷 Checking Camera...")
    
    # Check PiCamera2
    try:
        import picamera2
        print("✅ PiCamera2 available")
    except ImportError:
        print("❌ PiCamera2 not available")
    
    # Check OpenCV camera
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ OpenCV camera available")
            cap.release()
        else:
            print("❌ OpenCV camera not working")
    except:
        print("❌ OpenCV camera error")
    
    # Check camera interface
    try:
        result = subprocess.run(['vcgencmd', 'get_camera'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"📹 Camera Interface: {result.stdout.strip()}")
    except:
        print("📹 Camera Interface: Unable to check")

def check_tflite():
    """Check TFLite runtime"""
    print("\n🤖 Checking TFLite Runtime...")
    
    try:
        import tflite_runtime.interpreter as tflite
        print("✅ tflite-runtime available (optimized for Pi)")
    except ImportError:
        try:
            import tensorflow as tf
            print("⚠️  Using tensorflow (not optimized for Pi)")
        except ImportError:
            print("❌ No TFLite runtime available")
            return False
    return True

def run_performance_test():
    """Run performance test with different settings"""
    print("\n🚀 Running Performance Tests...")
    
    test_configs = [
        {"resolution": "320x240", "fps": 15, "mode": "speed"},
        {"resolution": "640x480", "fps": 15, "mode": "balanced"},
        {"resolution": "1280x720", "fps": 10, "mode": "quality"},
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n🧪 Testing: {config['resolution']} @ {config['fps']} FPS ({config['mode']} mode)")
        
        # Run detection for 10 seconds
        cmd = [
            "python3", "raspberry_milk_detector.py",
            "--resolution", config["resolution"],
            "--target-fps", str(config["fps"]),
            "--performance-mode", config["mode"],
            "--use-picamera2"
        ]
        
        try:
            # Start the process
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Let it run for 10 seconds
            time.sleep(10)
            
            # Terminate gracefully
            process.terminate()
            process.wait(timeout=5)
            
            print(f"✅ Test completed for {config['resolution']}")
            results.append(config)
            
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"❌ Test failed for {config['resolution']}")
        except Exception as e:
            print(f"❌ Error testing {config['resolution']}: {e}")
    
    return results

def generate_optimization_report():
    """Generate optimization recommendations"""
    print("\n📊 Performance Optimization Report")
    print("=" * 50)
    
    print("\n🎯 Quick Wins:")
    print("1. Use PiCamera2 instead of USB camera")
    print("2. Lower resolution to 320x240 or 640x480")
    print("3. Set target FPS to 15 or lower")
    print("4. Use 'speed' performance mode")
    
    print("\n⚙️  Recommended Settings:")
    print("For Real-time (15+ FPS):")
    print("  --resolution 320x240 --target-fps 15 --performance-mode speed")
    print("\nFor Balanced (10-15 FPS):")
    print("  --resolution 640x480 --target-fps 15 --performance-mode balanced")
    print("\nFor Quality (5-10 FPS):")
    print("  --resolution 1280x720 --target-fps 10 --performance-mode quality")
    
    print("\n🔧 System Optimizations:")
    print("1. Close unnecessary applications")
    print("2. Disable Bluetooth: sudo systemctl stop bluetooth")
    print("3. Disable WiFi if using Ethernet")
    print("4. Increase GPU memory in raspi-config")
    print("5. Ensure adequate cooling (temperature < 70°C)")
    
    print("\n📱 Runtime Controls:")
    print("Press '1' - Process every frame (best quality)")
    print("Press '2' - Process every 2nd frame (2x faster)")
    print("Press '3' - Process every 3rd frame (3x faster)")
    print("Press 's' - Save current frame")
    print("Press 'q' - Quit detection")

def main():
    print("🍓 Raspberry Pi Performance Optimizer")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("raspberry_milk_detector.py"):
        print("❌ Error: raspberry_milk_detector.py not found in current directory")
        print("Please run this script from the raspberry folder")
        return
    
    # System checks
    check_system_info()
    check_camera()
    
    if not check_tflite():
        print("\n❌ TFLite runtime not available. Please install dependencies first.")
        print("Run: ./setup_pi.sh")
        return
    
    # Ask user if they want to run performance tests
    print("\n🧪 Would you like to run performance tests? (y/n)")
    print("Note: This will start the detector multiple times for testing")
    
    try:
        user_input = input("Run tests? (y/n): ").lower().strip()
        if user_input in ['y', 'yes']:
            run_performance_test()
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    
    # Generate recommendations
    generate_optimization_report()
    
    print("\n🎉 Optimization complete!")
    print("Use the recommended settings above to improve your FPS.")

if __name__ == "__main__":
    main() 