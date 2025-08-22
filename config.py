#!/usr/bin/env python3
"""
Configuration file for Raspberry Pi Milk Detection System
Centralized control over all system parameters
"""

import os
from pathlib import Path

class DetectionConfig:
    """Configuration class for milk detection parameters"""
    
    def __init__(self):
        # Model Configuration
        self.MODEL_PATH = "model/best_float32.tflite"
        self.MODEL_INPUT_SIZE = (640, 640)  # (width, height)
        
        # Detection Thresholds
        self.CONFIDENCE_THRESHOLD = 0.5      # Minimum confidence for detection (0.0 - 1.0)
        self.NMS_THRESHOLD = 0.4             # Non-maximum suppression threshold (0.0 - 1.0)
        self.IOU_THRESHOLD = 0.5             # Intersection over Union threshold
        
        # ROI (Region of Interest) Configuration
        self.ENABLE_ROI = True               # Enable/disable ROI filtering
        self.ROI_X1 = 0.1                    # ROI left boundary (0.0 - 1.0, relative to image width)
        self.ROI_Y1 = 0.1                    # ROI top boundary (0.0 - 1.0, relative to image height)
        self.ROI_X2 = 0.9                    # ROI right boundary (0.0 - 1.0, relative to image width)
        self.ROI_Y2 = 0.9                    # ROI bottom boundary (0.0 - 1.0, relative to image height)
        
        # Camera Configuration
        self.CAMERA_INDEX = 0                 # Camera device index
        self.CAMERA_RESOLUTION = (640, 480)  # (width, height)
        self.CAMERA_FPS = 30                  # Frames per second
        self.USE_PICAMERA2 = True             # Use PiCamera2 instead of OpenCV camera
        
        # Processing Configuration
        self.ENABLE_PREPROCESSING = True      # Enable image preprocessing
        self.ENABLE_POSTPROCESSING = True     # Enable detection post-processing
        self.MAX_DETECTIONS = 10              # Maximum number of detections to process
        self.MIN_DETECTION_SIZE = 20          # Minimum detection size in pixels
        
        # Performance Configuration
        self.NUM_THREADS = 4                  # Number of threads for TFLite interpreter
        self.ENABLE_FPS_DISPLAY = True        # Show FPS on output
        self.ENABLE_DETECTION_COUNT = True    # Show detection count on output
        self.FRAME_SKIP = 0                   # Skip frames for performance (0 = process all)
        
        # Output Configuration
        self.SAVE_DETECTIONS = True           # Save detected frames
        self.OUTPUT_DIR = "saved_frames"      # Directory to save output
        self.IMAGE_FORMAT = "jpg"             # Output image format
        self.QUALITY = 95                     # JPEG quality (1-100)
        
        # Visualization Configuration
        self.DRAW_BOUNDING_BOXES = True       # Draw detection boxes
        self.DRAW_LABELS = True               # Draw confidence labels
        self.BOX_COLOR = (0, 255, 0)         # BGR color for boxes
        self.LABEL_COLOR = (0, 0, 0)         # BGR color for labels
        self.LINE_THICKNESS = 2               # Thickness of bounding box lines
        self.FONT_SCALE = 0.5                # Font scale for labels
        
        # Alert Configuration
        self.ENABLE_ALERTS = True             # Enable detection alerts
        self.ALERT_THRESHOLD = 1              # Minimum detections to trigger alert
        self.ALERT_COOLDOWN = 5.0            # Seconds between alerts
        
        # Logging Configuration
        self.ENABLE_LOGGING = True            # Enable logging
        self.LOG_LEVEL = "INFO"               # Log level (DEBUG, INFO, WARNING, ERROR)
        self.LOG_FILE = "milk_detection.log"  # Log file path
        
        # System Optimization
        self.ENABLE_GPU_MEMORY = True         # Enable GPU memory allocation
        self.GPU_MEMORY = 128                 # GPU memory in MB
        self.OVERCLOCK_ENABLED = False        # Enable overclocking
        self.TEMP_LIMIT = 70                  # Temperature limit in Celsius
        
        # Network Configuration (if using remote monitoring)
        self.ENABLE_NETWORK = False           # Enable network features
        self.HOST = "0.0.0.0"                # Host for network server
        self.PORT = 8080                      # Port for network server
        
        # Validation
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration parameters"""
        # Validate thresholds
        if not 0.0 <= self.CONFIDENCE_THRESHOLD <= 1.0:
            raise ValueError("CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
        
        if not 0.0 <= self.NMS_THRESHOLD <= 1.0:
            raise ValueError("NMS_THRESHOLD must be between 0.0 and 1.0")
        
        if not 0.0 <= self.IOU_THRESHOLD <= 1.0:
            raise ValueError("IOU_THRESHOLD must be between 0.0 and 1.0")
        
        # Validate ROI
        if self.ENABLE_ROI:
            if not (0.0 <= self.ROI_X1 < self.ROI_X2 <= 1.0):
                raise ValueError("ROI X coordinates must be 0.0 <= X1 < X2 <= 1.0")
            if not (0.0 <= self.ROI_Y1 < self.ROI_Y2 <= 1.0):
                raise ValueError("ROI Y coordinates must be 0.0 <= Y1 < Y2 <= 1.0")
        
        # Validate camera settings
        if self.CAMERA_FPS <= 0:
            raise ValueError("CAMERA_FPS must be positive")
        
        if self.NUM_THREADS <= 0:
            raise ValueError("NUM_THREADS must be positive")
        
        # Validate output settings
        if not 1 <= self.QUALITY <= 100:
            raise ValueError("QUALITY must be between 1 and 100")
    
    def get_roi_coordinates(self, image_width, image_height):
        """Get ROI coordinates in pixels"""
        if not self.ENABLE_ROI:
            return (0, 0, image_width, image_height)
        
        x1 = int(self.ROI_X1 * image_width)
        y1 = int(self.ROI_Y1 * image_height)
        x2 = int(self.ROI_X2 * image_width)
        y2 = int(self.ROI_Y2 * image_height)
        
        return (x1, y1, x2, y2)
    
    def is_in_roi(self, detection, image_width, image_height):
        """Check if detection is within ROI"""
        if not self.ENABLE_ROI:
            return True
        
        x1, y1, x2, y2, _, _ = detection
        roi_x1, roi_y1, roi_x2, roi_y2 = self.get_roi_coordinates(image_width, image_height)
        
        # Check if detection center is within ROI
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        return (roi_x1 <= center_x <= roi_x2 and roi_y1 <= center_y <= roi_y2)
    
    def get_model_path(self):
        """Get absolute path to model file"""
        script_dir = Path(__file__).parent
        model_path = script_dir / self.MODEL_PATH
        return str(model_path)
    
    def get_output_dir(self):
        """Get absolute path to output directory"""
        script_dir = Path(__file__).parent
        output_dir = script_dir / self.OUTPUT_DIR
        output_dir.mkdir(exist_ok=True)
        return str(output_dir)
    
    def to_dict(self):
        """Convert configuration to dictionary"""
        return {
            'model_path': self.MODEL_PATH,
            'confidence_threshold': self.CONFIDENCE_THRESHOLD,
            'nms_threshold': self.NMS_THRESHOLD,
            'iou_threshold': self.IOU_THRESHOLD,
            'enable_roi': self.ENABLE_ROI,
            'roi_coordinates': (self.ROI_X1, self.ROI_Y1, self.ROI_X2, self.ROI_Y2),
            'camera_resolution': self.CAMERA_RESOLUTION,
            'camera_fps': self.CAMERA_FPS,
            'use_picamera2': self.USE_PICAMERA2,
            'num_threads': self.NUM_THREADS,
            'max_detections': self.MAX_DETECTIONS,
            'min_detection_size': self.MIN_DETECTION_SIZE,
            'save_detections': self.SAVE_DETECTIONS,
            'enable_alerts': self.ENABLE_ALERTS,
            'alert_threshold': self.ALERT_THRESHOLD
        }
    
    def print_config(self):
        """Print current configuration"""
        print("=== Milk Detection Configuration ===")
        print(f"Model Path: {self.MODEL_PATH}")
        print(f"Confidence Threshold: {self.CONFIDENCE_THRESHOLD}")
        print(f"NMS Threshold: {self.NMS_THRESHOLD}")
        print(f"IOU Threshold: {self.IOU_THRESHOLD}")
        print(f"ROI Enabled: {self.ENABLE_ROI}")
        if self.ENABLE_ROI:
            print(f"ROI: ({self.ROI_X1:.2f}, {self.ROI_Y1:.2f}) to ({self.ROI_X2:.2f}, {self.ROI_Y2:.2f})")
        print(f"Camera Resolution: {self.CAMERA_RESOLUTION}")
        print(f"Camera FPS: {self.CAMERA_FPS}")
        print(f"Use PiCamera2: {self.USE_PICAMERA2}")
        print(f"Number of Threads: {self.NUM_THREADS}")
        print(f"Max Detections: {self.MAX_DETECTIONS}")
        print(f"Save Detections: {self.SAVE_DETECTIONS}")
        print(f"Enable Alerts: {self.ENABLE_ALERTS}")
        print("==================================")

# Create global configuration instance
config = DetectionConfig()

# Example usage:
# from config import config
# print(config.CONFIDENCE_THRESHOLD)
# config.CONFIDENCE_THRESHOLD = 0.7
# config.print_config() 