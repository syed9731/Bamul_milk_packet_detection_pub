#!/usr/bin/env python3
"""
Simple test script to verify PiCamera2 color correction
"""

import cv2
import time
import numpy as np

def test_picamera2_color():
    """Test PiCamera2 with color correction"""
    try:
        from picamera2 import Picamera2
        print("Testing PiCamera2 with color correction...")
        
        # Initialize PiCamera2
        picam2 = Picamera2()
        
        # Configure with color correction settings
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            buffer_count=4,
            controls={
                # Fix color shifting issues
                "AeEnable": True,           # Auto-exposure
                "AwbEnable": True,          # Auto white balance
                "AeMeteringMode": 0,        # Centre-weighted metering
                "AwbMode": 0,               # Auto white balance
                "ColourGains": (1.0, 1.0), # Neutral color gains (R, B)
                "AnalogueGain": 1.0,        # Neutral analog gain
                "DigitalGain": 1.0,         # Neutral digital gain
                "ExposureTime": 0,          # Auto exposure time
                "Saturation": 1.0,          # Normal saturation
                "Sharpness": 1.0,           # Normal sharpness
                "Contrast": 1.0,            # Normal contrast
                "Brightness": 0.0,          # Normal brightness
            }
        )
        picam2.configure(config)
        picam2.start()
        
        # Wait for camera to stabilize
        time.sleep(2)
        
        print("Camera started. Press 'q' to quit, 's' to save image")
        
        frame_count = 0
        while frame_count < 100:  # Capture 100 frames
            # Capture frame
            frame = picam2.capture_array()
            
            # Convert from RGB to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Add frame counter
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow('PiCamera2 Color Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"color_test_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Image saved: {filename}")
            
            frame_count += 1
            time.sleep(0.033)  # ~30 FPS
        
        cv2.destroyAllWindows()
        picam2.close()
        print("Test completed")
        
    except ImportError:
        print("PiCamera2 not available")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_picamera2_color() 