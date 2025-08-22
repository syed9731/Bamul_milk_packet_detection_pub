#!/usr/bin/env python3
"""
Example script showing how to use the configuration file
to control milk detection parameters
"""

from config import config

def main():
    """Demonstrate configuration usage"""
    
    # Print current configuration
    print("Current Configuration:")
    config.print_config()
    
    # Example 1: Adjust confidence threshold for more strict detection
    print("\n=== Example 1: Strict Detection ===")
    config.CONFIDENCE_THRESHOLD = 0.8  # Only detect with 80%+ confidence
    config.NMS_THRESHOLD = 0.3         # More aggressive NMS
    print(f"Adjusted confidence threshold to: {config.CONFIDENCE_THRESHOLD}")
    print(f"Adjusted NMS threshold to: {config.NMS_THRESHOLD}")
    
    # Example 2: Set ROI to focus on center area
    print("\n=== Example 2: Center ROI ===")
    config.ENABLE_ROI = True
    config.ROI_X1 = 0.25  # 25% from left
    config.ROI_Y1 = 0.25  # 25% from top
    config.ROI_X2 = 0.75  # 75% from left
    config.ROI_Y2 = 0.75  # 75% from top
    print(f"ROI set to center area: ({config.ROI_X1:.2f}, {config.ROI_Y1:.2f}) to ({config.ROI_X2:.2f}, {config.ROI_Y2:.2f})")
    
    # Example 3: Performance optimization
    print("\n=== Example 3: Performance Optimization ===")
    config.CAMERA_RESOLUTION = (320, 240)  # Lower resolution for speed
    config.CAMERA_FPS = 15                  # Lower FPS for stability
    config.NUM_THREADS = 2                  # Fewer threads for Pi Zero
    config.FRAME_SKIP = 1                   # Process every other frame
    print(f"Optimized for performance: {config.CAMERA_RESOLUTION} @ {config.CAMERA_FPS}fps")
    
    # Example 4: High quality detection
    print("\n=== Example 4: High Quality Detection ===")
    config.CAMERA_RESOLUTION = (1280, 720)  # HD resolution
    config.CAMERA_FPS = 30                  # Full FPS
    config.QUALITY = 100                    # Maximum JPEG quality
    config.SAVE_DETECTIONS = True           # Save all detections
    print(f"High quality mode: {config.CAMERA_RESOLUTION} @ {config.CAMERA_FPS}fps")
    
    # Example 5: Custom visualization
    print("\n=== Example 5: Custom Visualization ===")
    config.BOX_COLOR = (255, 0, 0)         # Red boxes
    config.LABEL_COLOR = (255, 255, 255)    # White labels
    config.LINE_THICKNESS = 3               # Thicker lines
    config.FONT_SCALE = 0.7                 # Larger font
    print("Custom visualization applied")
    
    # Example 6: Alert configuration
    print("\n=== Example 6: Alert Settings ===")
    config.ENABLE_ALERTS = True
    config.ALERT_THRESHOLD = 3              # Alert when 3+ detections
    config.ALERT_COOLDOWN = 10.0            # 10 second cooldown
    print(f"Alerts enabled: {config.ALERT_THRESHOLD}+ detections, {config.ALERT_COOLDOWN}s cooldown")
    
    # Example 7: ROI validation
    print("\n=== Example 7: ROI Validation ===")
    image_width, image_height = 640, 480
    roi_coords = config.get_roi_coordinates(image_width, image_height)
    print(f"ROI coordinates for {image_width}x{image_height}: {roi_coords}")
    
    # Test ROI filtering
    test_detection = [100, 100, 200, 200, 0.9, 0]  # x1, y1, x2, y2, conf, class
    in_roi = config.is_in_roi(test_detection, image_width, image_height)
    print(f"Test detection {test_detection[:4]} is {'IN' if in_roi else 'OUTSIDE'} ROI")
    
    # Example 8: Configuration export
    print("\n=== Example 8: Configuration Export ===")
    config_dict = config.to_dict()
    print("Configuration as dictionary:")
    for key, value in config_dict.items():
        print(f"  {key}: {value}")
    
    # Example 9: Reset to defaults
    print("\n=== Example 9: Reset to Defaults ===")
    config.__init__()  # Reset to default values
    print("Configuration reset to defaults")
    
    # Example 10: Custom configuration
    print("\n=== Example 10: Custom Configuration ===")
    # You can create multiple config instances for different scenarios
    class CustomConfig:
        def __init__(self):
            self.CONFIDENCE_THRESHOLD = 0.6
            self.ENABLE_ROI = False
            self.CAMERA_RESOLUTION = (800, 600)
    
    custom = CustomConfig()
    print(f"Custom config: confidence={custom.CONFIDENCE_THRESHOLD}, ROI={custom.ENABLE_ROI}")

if __name__ == "__main__":
    main() 