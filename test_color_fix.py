#!/usr/bin/env python3
"""
Test script to verify color space fix for PiCamera
Tests both OpenCV and PiCamera2 interfaces to ensure correct colors
"""

import cv2
import numpy as np
import time
import sys

def test_color_spaces():
    """Test different color space conversions to understand the issue"""
    print("Testing color space conversions...")
    
    # Create a test image with known colors
    test_image = np.zeros((100, 300, 3), dtype=np.uint8)
    
    # Red (255, 0, 0) in RGB
    test_image[:, :100] = [255, 0, 0]  # Red
    # Green (0, 255, 0) in RGB  
    test_image[:, 100:200] = [0, 255, 0]  # Green
    # Blue (0, 0, 255) in RGB
    test_image[:, 200:300] = [0, 0, 255]  # Blue
    
    print("Original RGB image created:")
    print("  Left: Red (255,0,0)")
    print("  Middle: Green (0,255,0)") 
    print("  Right: Blue (0,0,255)")
    
    # Convert to BGR (OpenCV format)
    bgr_image = cv2.cvtColor(test_image, cv2.COLOR_RGB2BGR)
    
    print("\nConverted to BGR (OpenCV format):")
    print("  Left: Blue (255,0,0) in BGR = Red in RGB")
    print("  Middle: Green (0,255,0) in BGR = Green in RGB")
    print("  Right: Red (0,0,255) in BGR = Blue in RGB")
    
    # Save both images
    cv2.imwrite('test_rgb.jpg', test_image)
    cv2.imwrite('test_bgr.jpg', bgr_image)
    
    print("\nTest images saved:")
    print("  test_rgb.jpg - Original RGB image")
    print("  test_bgr.jpg - BGR converted image")
    
    return test_image, bgr_image

def test_camera_colors():
    """Test actual camera colors"""
    print("\nTesting camera colors...")
    
    # Try OpenCV camera first
    print("Testing OpenCV camera...")
    cap = cv2.VideoCapture(0)
    
    if cap.isOpened():
        print("OpenCV camera opened successfully")
        
        # Set properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Capture a few frames
        for i in range(5):
            ret, frame = cap.read()
            if ret:
                print(f"Frame {i+1} captured, shape: {frame.shape}")
                print(f"  Sample pixel values (BGR): {frame[240, 320]}")
                
                # Save frame
                cv2.imwrite(f'opencv_frame_{i+1}.jpg', frame)
                
                # Show frame briefly
                cv2.imshow('OpenCV Camera Test', frame)
                cv2.waitKey(500)
        
        cap.release()
        cv2.destroyAllWindows()
        
        print("OpenCV test completed")
    else:
        print("OpenCV camera not available")
    
    # Try PiCamera2
    print("\nTesting PiCamera2...")
    try:
        from picamera2 import Picamera2
        
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        picam2.configure(config)
        picam2.start()
        
        # Wait for camera to stabilize
        time.sleep(2)
        
        print("PiCamera2 opened successfully")
        
        # Capture a few frames
        for i in range(5):
            frame = picam2.capture_array()
            print(f"Frame {i+1} captured, shape: {frame.shape}")
            print(f"  Sample pixel values (RGB): {frame[240, 320]}")
            
            # Convert to BGR for OpenCV display
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Save frame
            cv2.imwrite(f'picamera2_frame_{i+1}.jpg', frame_bgr)
            
            # Show frame briefly
            cv2.imshow('PiCamera2 Test', frame_bgr)
            cv2.waitKey(500)
        
        picam2.close()
        cv2.destroyAllWindows()
        
        print("PiCamera2 test completed")
        
    except ImportError:
        print("PiCamera2 not available")
    except Exception as e:
        print(f"PiCamera2 error: {e}")

def main():
    print("Color Space Test for PiCamera")
    print("=" * 40)
    
    # Test color space conversions
    test_color_spaces()
    
    # Test actual camera colors
    test_camera_colors()
    
    print("\nTest completed!")
    print("Check the saved images to verify colors are correct.")
    print("If colors are still inverted, the issue may be in camera configuration.")

if __name__ == "__main__":
    main() 