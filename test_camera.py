#!/usr/bin/env python3
"""
Camera Test Script for Raspberry Pi
Tests both PiCamera2 and OpenCV camera interfaces
"""

import cv2
import time
import argparse
import sys

def test_opencv_camera(camera_index=0, resolution=(640, 480)):
    """Test OpenCV camera interface"""
    print(f"Testing OpenCV camera {camera_index}...")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera {camera_index}")
        return False
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Get actual properties
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Camera properties:")
    print(f"  Requested: {resolution[0]}x{resolution[1]} @ 30fps")
    print(f"  Actual: {actual_width}x{actual_height} @ {actual_fps:.1f}fps")
    
    # Capture a few frames
    frame_count = 0
    start_time = time.time()
    
    try:
        while frame_count < 30:  # Capture 30 frames
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            frame_count += 1
            
            # Display frame
            cv2.imshow('OpenCV Camera Test', frame)
            
            # Check for key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Small delay
            time.sleep(0.033)  # ~30 FPS
        
        # Calculate actual FPS
        elapsed_time = time.time() - start_time
        actual_fps = frame_count / elapsed_time
        
        print(f"Captured {frame_count} frames in {elapsed_time:.2f}s")
        print(f"Actual FPS: {actual_fps:.1f}")
        
        # Save test image
        if frame_count > 0:
            cv2.imwrite('opencv_test.jpg', frame)
            print("Test image saved as: opencv_test.jpg")
        
        return True
        
    except Exception as e:
        print(f"Error during OpenCV test: {e}")
        return False
    finally:
        cap.release()
        cv2.destroyAllWindows()

def test_picamera2(resolution=(640, 480)):
    """Test PiCamera2 interface"""
    print("Testing PiCamera2...")
    
    try:
        from picamera2 import Picamera2
        from picamera2.encoders import JpegEncoder
    except ImportError:
        print("PiCamera2 not available")
        return False
    
    try:
        # Initialize PiCamera2
        picam2 = Picamera2()
        
        # Configure camera with proper color settings to fix color shifting
        config = picam2.create_preview_configuration(
            main={"size": resolution, "format": "RGB888"},
            buffer_count=4,
            controls={
                # Fix color shifting issues - only use widely supported controls
                "AeEnable": True,  # Enable auto-exposure
                "AwbEnable": True,  # Enable auto white balance
                "AeMeteringMode": 0,  # Centre-weighted metering
                "AwbMode": 0,  # Auto white balance
                "AnalogueGain": 1.0,  # Neutral analog gain
                "DigitalGain": 1.0,  # Neutral digital gain
                "ExposureTime": 0,  # Auto exposure time
                "Saturation": 1.0,  # Normal saturation
                "Sharpness": 1.0,  # Normal sharpness
                "Contrast": 1.0,  # Normal contrast
                "Brightness": 0.0,  # Normal brightness
            }
        )
        picam2.configure(config)
        
        # Start camera
        picam2.start()
        
        # Wait for camera to stabilize and apply settings
        time.sleep(2)
        
        print(f"PiCamera2 initialized with {resolution[0]}x{resolution[1]}")
        
        # Capture a few frames
        frame_count = 0
        start_time = time.time()
        
        try:
            while frame_count < 30:  # Capture 30 frames
                # Capture frame
                frame = picam2.capture_array()
                
                # Convert from RGB to BGR for OpenCV
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Display frame
                cv2.imshow('PiCamera2 Test', frame)
                
                frame_count += 1
                
                # Check for key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # Small delay
                time.sleep(0.033)  # ~30 FPS
            
            # Calculate actual FPS
            elapsed_time = time.time() - start_time
            actual_fps = frame_count / elapsed_time
            
            print(f"Captured {frame_count} frames in {elapsed_time:.2f}s")
            print(f"Actual FPS: {actual_fps:.1f}")
            
            # Save test image
            if frame_count > 0:
                cv2.imwrite('picamera2_test.jpg', frame)
                print("Test image saved as: picamera2_test.jpg")
            
            return True
            
        except Exception as e:
            print(f"Error during PiCamera2 capture: {e}")
            return False
        finally:
            cv2.destroyAllWindows()
            picam2.close()
            
    except Exception as e:
        print(f"Error initializing PiCamera2: {e}")
        return False

def test_camera_list():
    """List available camera devices"""
    print("Available camera devices:")
    
    # Check for video devices
    import glob
    video_devices = glob.glob('/dev/video*')
    
    if video_devices:
        for device in video_devices:
            print(f"  {device}")
            
            # Try to open device
            cap = cv2.VideoCapture(device)
            if cap.isOpened():
                # Get device info
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                print(f"    Resolution: {width}x{height}")
                print(f"    FPS: {fps:.1f}")
                
                cap.release()
            else:
                print(f"    Status: Not accessible")
    else:
        print("  No video devices found")
    
    # Check for PiCamera2
    try:
        from picamera2 import Picamera2
        print("  PiCamera2: Available")
    except ImportError:
        print("  PiCamera2: Not available")

def main():
    parser = argparse.ArgumentParser(description="Camera Test for Raspberry Pi")
    parser.add_argument("--opencv", action="store_true", help="Test OpenCV camera")
    parser.add_argument("--picamera2", action="store_true", help="Test PiCamera2")
    parser.add_argument("--list", action="store_true", help="List available cameras")
    parser.add_argument("--camera", type=int, default=0, help="Camera device index")
    parser.add_argument("--resolution", default="640x480", help="Test resolution")
    
    args = parser.parse_args()
    
    # Parse resolution
    try:
        width, height = map(int, args.resolution.split('x'))
        resolution = (width, height)
    except ValueError:
        print("Error: Invalid resolution format. Use WIDTHxHEIGHT (e.g., 640x480)")
        return
    
    print("Raspberry Pi Camera Test")
    print("========================")
    print(f"Resolution: {resolution[0]}x{resolution[1]}")
    print("")
    
    if args.list:
        test_camera_list()
        return
    
    if args.picamera2:
        test_picamera2(resolution)
        return
    
    if args.opencv:
        test_opencv_camera(args.camera, resolution)
        return
    
    # Default: test both
    print("Testing both camera interfaces...")
    print("")
    
    # Test PiCamera2 first (recommended for Pi)
    if test_picamera2(resolution):
        print("\nPiCamera2 test completed successfully!")
    else:
        print("\nPiCamera2 test failed or not available")
    
    print("\n" + "="*50 + "\n")
    
    # Test OpenCV camera
    if test_opencv_camera(args.camera, resolution):
        print("\nOpenCV camera test completed successfully!")
    else:
        print("\nOpenCV camera test failed")
    
    print("\nCamera testing complete!")
    print("Check the generated test images to verify camera functionality.")

if __name__ == "__main__":
    main() 