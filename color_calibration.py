#!/usr/bin/env python3
"""
PiCamera2 Color Calibration Script
Fixes color shifting issues where yellow objects appear blue
"""

import cv2
import numpy as np
import time
import json
from pathlib import Path

class PiCamera2ColorCalibrator:
    def __init__(self):
        self.picam2 = None
        self.current_settings = {}
        self.calibration_file = Path("picamera2_color_calibration.json")
        
    def initialize_camera(self, resolution=(640, 480)):
        """Initialize PiCamera2 with basic configuration"""
        try:
            from picamera2 import Picamera2
            print("Initializing PiCamera2...")
            
            self.picam2 = Picamera2()
            
            # Basic configuration
            config = self.picam2.create_preview_configuration(
                main={"size": resolution, "format": "RGB888"},
                buffer_count=4
            )
            self.picam2.configure(config)
            self.picam2.start()
            
            # Wait for camera to stabilize
            time.sleep(2)
            print("Camera initialized successfully!")
            return True
            
        except ImportError:
            print("Error: PiCamera2 not available")
            return False
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def load_calibration(self):
        """Load saved calibration settings"""
        if self.calibration_file.exists():
            try:
                with open(self.calibration_file, 'r') as f:
                    self.current_settings = json.load(f)
                print("Loaded saved calibration settings")
                return True
            except Exception as e:
                print(f"Error loading calibration: {e}")
        return False
    
    def save_calibration(self):
        """Save current calibration settings"""
        try:
            with open(self.calibration_file, 'w') as f:
                json.dump(self.current_settings, f, indent=2)
            print(f"Calibration saved to {self.calibration_file}")
            return True
        except Exception as e:
            print(f"Error saving calibration: {e}")
            return False
    
    def apply_color_settings(self, settings):
        """Apply color correction settings to camera"""
        if not self.picam2:
            print("Camera not initialized")
            return False
        
        try:
            # Apply the settings
            for key, value in settings.items():
                try:
                    self.picam2.set_controls({key: value})
                    print(f"Applied {key}: {value}")
                except Exception as e:
                    print(f"Could not apply {key}: {e}")
            
            # Wait for settings to take effect
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"Error applying settings: {e}")
            return False
    
    def get_default_color_settings(self):
        """Get default color correction settings"""
        return {
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
    
    def get_advanced_color_settings(self):
        """Get advanced color correction settings"""
        return {
            "AeEnable": True,
            "AwbEnable": True,
            "AeMeteringMode": 0,
            "AwbMode": 0,
            "ColourGains": (1.0, 1.0),
            "AnalogueGain": 1.0,
            "DigitalGain": 1.0,
            "ExposureTime": 0,
            "Saturation": 1.0,
            "Sharpness": 1.0,
            "Contrast": 1.0,
            "Brightness": 0.0,
            # Advanced color correction
            "ColourCorrectionMatrix": [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
            "ScalerCrop": (0, 0, 640, 480),  # Full sensor area
            "SensorBlackLevels": (0, 0, 0, 0),  # No black level adjustment
        }
    
    def interactive_calibration(self):
        """Interactive calibration mode"""
        print("\n=== PiCamera2 Color Calibration ===")
        print("Place a white/yellow object in front of the camera")
        print("Adjust settings until colors look correct")
        print("Press 'q' to quit, 's' to save, 'r' to reset")
        print("Use number keys 1-9 to adjust different parameters")
        
        # Load saved settings or use defaults
        if not self.load_calibration():
            self.current_settings = self.get_default_color_settings()
        
        # Apply initial settings
        self.apply_color_settings(self.current_settings)
        
        # Start calibration loop
        while True:
            # Capture frame
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Add calibration info overlay
            info_frame = frame.copy()
            cv2.putText(info_frame, "Color Calibration Mode", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display current settings
            y_offset = 60
            for i, (key, value) in enumerate(self.current_settings.items()):
                if i < 8:  # Show first 8 settings
                    cv2.putText(info_frame, f"{key}: {value}", (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    y_offset += 20
            
            cv2.imshow('PiCamera2 Color Calibration', info_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.save_calibration()
                print("Calibration saved!")
            elif key == ord('r'):
                self.current_settings = self.get_default_color_settings()
                self.apply_color_settings(self.current_settings)
                print("Reset to default settings")
            elif key == ord('1'):
                # Adjust red color gain
                current = self.current_settings.get("ColourGains", (1.0, 1.0))
                new_red = min(2.0, current[0] + 0.1)
                self.current_settings["ColourGains"] = (new_red, current[1])
                self.apply_color_settings({"ColourGains": (new_red, current[1])})
                print(f"Red gain: {new_red:.2f}")
            elif key == ord('2'):
                # Adjust blue color gain
                current = self.current_settings.get("ColourGains", (1.0, 1.0))
                new_blue = min(2.0, current[1] + 0.1)
                self.current_settings["ColourGains"] = (current[0], new_blue)
                self.apply_color_settings({"ColourGains": (current[0], new_blue)})
                print(f"Blue gain: {new_blue:.2f}")
            elif key == ord('3'):
                # Adjust saturation
                current = self.current_settings.get("Saturation", 1.0)
                new_sat = min(2.0, current + 0.1)
                self.current_settings["Saturation"] = new_sat
                self.apply_color_settings({"Saturation": new_sat})
                print(f"Saturation: {new_sat:.2f}")
            elif key == ord('4'):
                # Adjust contrast
                current = self.current_settings.get("Contrast", 1.0)
                new_contrast = min(2.0, current + 0.1)
                self.current_settings["Contrast"] = new_contrast
                self.apply_color_settings({"Contrast": new_contrast})
                print(f"Contrast: {new_contrast:.2f}")
            elif key == ord('5'):
                # Adjust brightness
                current = self.current_settings.get("Brightness", 0.0)
                new_brightness = min(1.0, current + 0.1)
                self.current_settings["Brightness"] = new_brightness
                self.apply_color_settings({"Brightness": new_brightness})
                print(f"Brightness: {new_brightness:.2f}")
            elif key == ord('6'):
                # Decrease red gain
                current = self.current_settings.get("ColourGains", (1.0, 1.0))
                new_red = max(0.1, current[0] - 0.1)
                self.current_settings["ColourGains"] = (new_red, current[1])
                self.apply_color_settings({"ColourGains": (new_red, current[1])})
                print(f"Red gain: {new_red:.2f}")
            elif key == ord('7'):
                # Decrease blue gain
                current = self.current_settings.get("ColourGains", (1.0, 1.0))
                new_blue = max(0.1, current[1] - 0.1)
                self.current_settings["ColourGains"] = (new_red, new_blue)
                self.apply_color_settings({"ColourGains": (current[0], new_blue)})
                print(f"Blue gain: {new_blue:.2f}")
            elif key == ord('8'):
                # Decrease saturation
                current = self.current_settings.get("Saturation", 1.0)
                new_sat = max(0.1, current - 0.1)
                self.current_settings["Saturation"] = new_sat
                self.apply_color_settings({"Saturation": new_sat})
                print(f"Saturation: {new_sat:.2f}")
            elif key == ord('9'):
                # Decrease contrast
                current = self.current_settings.get("Contrast", 1.0)
                new_contrast = max(0.1, current - 0.1)
                self.current_settings["Contrast"] = new_contrast
                self.apply_color_settings({"Contrast": new_contrast})
                print(f"Contrast: {new_contrast:.2f}")
        
        cv2.destroyAllWindows()
        if self.picam2:
            self.picam2.close()
    
    def test_color_correction(self):
        """Test the current color correction settings"""
        print("\n=== Testing Color Correction ===")
        print("Capturing test image with current settings...")
        
        if not self.picam2:
            print("Camera not initialized")
            return
        
        # Capture test frame
        frame = self.picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Save test image
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"color_test_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Test image saved: {filename}")
        
        # Display frame
        cv2.imshow('Color Test Result', frame)
        print("Press any key to continue...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    """Main function"""
    print("PiCamera2 Color Calibration Tool")
    print("This tool helps fix color shifting issues in PiCamera2")
    
    calibrator = PiCamera2ColorCalibrator()
    
    if not calibrator.initialize_camera():
        print("Failed to initialize camera. Exiting.")
        return
    
    while True:
        print("\nOptions:")
        print("1. Interactive Calibration")
        print("2. Test Current Settings")
        print("3. Load Saved Calibration")
        print("4. Save Current Calibration")
        print("5. Reset to Defaults")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            calibrator.interactive_calibration()
        elif choice == '2':
            calibrator.test_color_correction()
        elif choice == '3':
            if calibrator.load_calibration():
                calibrator.apply_color_settings(calibrator.current_settings)
        elif choice == '4':
            calibrator.save_calibration()
        elif choice == '5':
            calibrator.current_settings = calibrator.get_default_color_settings()
            calibrator.apply_color_settings(calibrator.current_settings)
            print("Reset to default settings")
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")
    
    if calibrator.picam2:
        calibrator.picam2.close()
    print("Calibration tool closed.")

if __name__ == "__main__":
    main() 