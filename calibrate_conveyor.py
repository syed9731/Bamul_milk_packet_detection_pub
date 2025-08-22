#!/usr/bin/env python3
"""
Conveyor Belt Calibration Script for Milk Detection
Helps calibrate camera position and conveyor parameters
"""

import cv2
import numpy as np
import time
import math
from pathlib import Path

class ConveyorCalibrator:
    def __init__(self):
        self.calibration_points = []
        self.reference_objects = []
        self.camera_height = 1.0  # meters (adjustable)
        self.conveyor_width = 0.5  # meters (adjustable)
        
    def calibrate_camera_position(self, camera_index=0):
        """
        Interactive camera position calibration
        """
        print("📷 Camera Position Calibration")
        print("=" * 40)
        print("1. Position camera directly above conveyor center")
        print("2. Ensure camera is perpendicular to conveyor surface")
        print("3. Mark reference points on conveyor")
        print("4. Measure distances for calibration")
        
        # Get camera parameters
        print("\n📏 Camera Setup Parameters:")
        try:
            self.camera_height = float(input("Enter camera height above conveyor (meters): ") or "1.0")
            self.conveyor_width = float(input("Enter conveyor belt width (meters): ") or "0.5")
        except ValueError:
            print("Using default values")
        
        print(f"\nCamera height: {self.camera_height}m")
        print(f"Conveyor width: {self.conveyor_width}m")
        
        # Start camera for visual calibration
        print("\n🎥 Starting camera for visual calibration...")
        print("Press 'm' to mark reference points, 'q' to quit")
        
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print("❌ Could not open camera")
            return False
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Draw calibration overlay
                self.draw_calibration_overlay(frame)
                
                # Draw reference points
                for i, point in enumerate(self.calibration_points):
                    cv2.circle(frame, point, 5, (0, 255, 0), -1)
                    cv2.putText(frame, f"P{i+1}", (point[0]+10, point[1]-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Draw conveyor boundaries
                if len(self.calibration_points) >= 2:
                    cv2.line(frame, self.calibration_points[0], self.calibration_points[1], 
                             (255, 0, 0), 2)
                    cv2.putText(frame, f"Width: {self.conveyor_width}m", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                cv2.imshow('Conveyor Calibration', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('m'):
                    # Mark reference point
                    if len(self.calibration_points) < 4:
                        print(f"Click to mark reference point {len(self.calibration_points)+1}")
                        point = cv2.selectROI('Select Point', frame, False)
                        if point[2] > 0 and point[3] > 0:
                            center = (point[0] + point[2]//2, point[1] + point[3]//2)
                            self.calibration_points.append(center)
                            print(f"Point {len(self.calibration_points)} marked at {center}")
                    else:
                        print("Maximum 4 reference points allowed")
                elif key == ord('c'):
                    # Clear calibration points
                    self.calibration_points.clear()
                    print("Calibration points cleared")
                
        finally:
            cap.release()
            cv2.destroyAllWindows()
        
        return len(self.calibration_points) >= 2
    
    def draw_calibration_overlay(self, frame):
        """
        Draw calibration grid and guidelines
        """
        height, width = frame.shape[:2]
        
        # Draw center line
        center_x = width // 2
        cv2.line(frame, (center_x, 0), (center_x, height), (128, 128, 128), 1)
        
        # Draw horizontal guidelines
        for i in range(1, 4):
            y = (height * i) // 4
            cv2.line(frame, (0, y), (width, y), (128, 128, 128), 1)
        
        # Draw vertical guidelines
        for i in range(1, 4):
            x = (width * i) // 4
            cv2.line(frame, (x, 0), (x, height), (128, 128, 128), 1)
        
        # Draw center crosshair
        center_y = height // 2
        cv2.circle(frame, (center_x, center_y), 20, (0, 255, 255), 2)
        cv2.line(frame, (center_x-25, center_y), (center_x+25, center_y), (0, 255, 255), 2)
        cv2.line(frame, (center_x, center_y-25), (center_x, center_y+25), (0, 255, 255), 2)
    
    def calculate_pixel_ratio(self):
        """
        Calculate pixels per meter ratio
        """
        if len(self.calibration_points) < 2:
            return None
        
        # Calculate distance between first two points in pixels
        p1 = self.calibration_points[0]
        p2 = self.calibration_points[1]
        pixel_distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        # Calculate pixels per meter
        pixels_per_meter = pixel_distance / self.conveyor_width
        
        return pixels_per_meter
    
    def generate_calibration_report(self):
        """
        Generate calibration report with recommended settings
        """
        if not self.calibration_points:
            print("❌ No calibration points available")
            return
        
        print("\n📊 Calibration Report")
        print("=" * 30)
        
        # Calculate pixel ratio
        pixel_ratio = self.calculate_pixel_ratio()
        if pixel_ratio:
            print(f"Pixel-to-meter ratio: {pixel_ratio:.1f} px/m")
            
            # Calculate recommended settings
            recommended_fps = min(30, max(10, int(pixel_ratio * 2)))
            print(f"Recommended target FPS: {recommended_fps}")
            
            # Calculate detection coverage
            frame_width = 640  # Assuming 640x480 resolution
            detection_coverage = (self.conveyor_width * pixel_ratio) / frame_width * 100
            print(f"Detection coverage: {detection_coverage:.1f}% of frame width")
            
            if detection_coverage < 50:
                print("⚠️  Warning: Low detection coverage. Consider:")
                print("   • Moving camera closer to conveyor")
                print("   • Using higher resolution camera")
                print("   • Adjusting camera angle")
            
            # Generate startup command
            print(f"\n🚀 Recommended startup command:")
            print(f"python3 raspberry_milk_detector.py \\")
            print(f"    --use-picamera2 \\")
            print(f"    --conveyor-mode \\")
            print(f"    --conveyor-width {self.conveyor_width} \\")
            print(f"    --performance-mode balanced \\")
            print(f"    --target-fps {recommended_fps}")
            
            # Save calibration data
            self.save_calibration_data(pixel_ratio, recommended_fps)
        
        print(f"\n✅ Calibration complete!")
        print("Use the recommended settings above for optimal performance")
    
    def save_calibration_data(self, pixel_ratio, recommended_fps):
        """
        Save calibration data to file
        """
        calibration_data = {
            'pixel_to_meter_ratio': pixel_ratio,
            'conveyor_width': self.conveyor_width,
            'camera_height': self.camera_height,
            'recommended_fps': recommended_fps,
            'calibration_points': self.calibration_points,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Create calibration directory
        cal_dir = Path("calibration")
        cal_dir.mkdir(exist_ok=True)
        
        # Save to file
        import json
        cal_file = cal_dir / "conveyor_calibration.json"
        with open(cal_file, 'w') as f:
            json.dump(calibration_data, f, indent=2)
        
        print(f"📁 Calibration data saved to: {cal_file}")
    
    def load_calibration_data(self):
        """
        Load previous calibration data
        """
        cal_file = Path("calibration/conveyor_calibration.json")
        if cal_file.exists():
            try:
                import json
                with open(cal_file, 'r') as f:
                    data = json.load(f)
                
                self.calibration_points = data.get('calibration_points', [])
                self.conveyor_width = data.get('conveyor_width', 0.5)
                self.camera_height = data.get('camera_height', 1.0)
                
                print(f"📁 Loaded calibration data from: {cal_file}")
                return data
            except Exception as e:
                print(f"❌ Error loading calibration data: {e}")
        
        return None

def main():
    print("🏭 Conveyor Belt Calibration Tool")
    print("=" * 40)
    
    calibrator = ConveyorCalibrator()
    
    # Try to load previous calibration
    previous_cal = calibrator.load_calibration_data()
    
    if previous_cal:
        print(f"Previous calibration found:")
        print(f"  Conveyor width: {previous_cal['conveyor_width']}m")
        print(f"  Pixel ratio: {previous_cal['pixel_to_meter_ratio']:.1f} px/m")
        print(f"  Recommended FPS: {previous_cal['recommended_fps']}")
        
        use_previous = input("\nUse previous calibration? (y/n): ").lower().strip()
        if use_previous == 'y':
            calibrator.generate_calibration_report()
            return
    
    print("\nStarting new calibration...")
    
    # Run calibration
    if calibrator.calibrate_camera_position():
        calibrator.generate_calibration_report()
    else:
        print("❌ Calibration failed or was cancelled")

if __name__ == "__main__":
    main() 