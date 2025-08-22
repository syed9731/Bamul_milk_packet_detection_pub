#!/usr/bin/env python3
"""
Raspberry Pi 4 Milk Packet Detector with Real-time Camera Input
Optimized for ARM architecture and real-time processing
"""

import os
import cv2
import numpy as np
import time
import threading
from pathlib import Path
import argparse
import signal
import sys

# Try to import tflite-runtime first (Pi optimized), fall back to tensorflow
try:
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True
    print("Using tflite-runtime (optimized for Pi)")
except ImportError:
    try:
        import tensorflow as tf
        tflite = tf.lite
        TFLITE_AVAILABLE = True
        print("Using tensorflow (fallback)")
    except ImportError:
        print("Error: Neither tflite-runtime nor tensorflow is available")
        sys.exit(1)

class RaspberryMilkDetector:
    def __init__(self, model_path, confidence_threshold=0.5, nms_threshold=0.4):
        """
        Initialize the Raspberry Pi milk packet detector
        
        Args:
            model_path: Path to the TFLite model
            confidence_threshold: Minimum confidence for detection
            nms_threshold: Non-maximum suppression threshold
        """
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.running = False
        self.frame_count = 0
        self.fps = 0
        self.last_time = time.time()
        
        # Camera interface tracking
        self.using_picamera2 = False
        
        # CONVEYOR BELT SYNCHRONIZATION
        self.conveyor_speed = 0.0  # meters per second
        self.target_fps = 60  # Changed from 15 to 60 FPS
        self.adaptive_processing = True
        self.speed_detection_enabled = True
        self.production_line_mode = False
        
        # Speed detection parameters
        self.speed_detection_frames = []
        self.speed_detection_timestamps = []
        self.last_detection_positions = []
        self.conveyor_width = 0.5  # meters (adjustable)
        self.pixel_to_meter_ratio = 1.0  # pixels per meter
        
        # Load TFLite model
        self.interpreter = tflite.Interpreter(model_path=model_path)
        
        # PERFORMANCE OPTIMIZATION: Configure interpreter for Pi 4
        try:
            # Set number of threads for better performance on Pi 4
            self.interpreter.set_num_threads(4)
            print("Set TFLite interpreter to use 4 threads")
        except:
            print("Could not set thread count (using default)")
        
        # PERFORMANCE OPTIMIZATION: Enable GPU delegation if available
        try:
            # Try to enable GPU acceleration
            from tflite_runtime.interpreter import load_delegate
            gpu_delegate = load_delegate('libedgetpu.so.1.0')
            self.interpreter = tflite.Interpreter(
                model_path=model_path,
                experimental_delegates=[gpu_delegate]
            )
            print("GPU acceleration enabled")
        except:
            print("GPU acceleration not available, using CPU")
        
        self.interpreter.allocate_tensors()
        
        # Get model details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Get input shape
        self.input_shape = self.input_details[0]['shape']
        self.input_height = self.input_shape[1]
        self.input_width = self.input_shape[2]
        
        print(f"Model loaded successfully!")
        print(f"Input shape: {self.input_shape}")
        print(f"Input size: {self.input_width}x{self.input_height}")
        
        # PERFORMANCE OPTIMIZATION: Add frame skip counter
        self.frame_skip_counter = 0
        self.frame_skip_interval = 1  # Process every frame by default
        
    def preprocess_image(self, image):
        """
        Preprocess image for model input (optimized for Pi)
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            Preprocessed image
        """
        # Resize image to model input size
        resized = cv2.resize(image, (self.input_width, self.input_height))
        
        # Convert color space based on camera interface
        # OpenCV camera outputs BGR, PiCamera2 outputs RGB
        if self.using_picamera2:
            # PiCamera2 already outputs RGB, no conversion needed
            pass
        else:
            # OpenCV camera outputs BGR, convert to RGB
            if len(resized.shape) == 3 and resized.shape[2] == 3:
                resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0, 1]
        normalized = resized.astype(np.float32) / 255.0
        
        # Add batch dimension
        input_tensor = np.expand_dims(normalized, axis=0)
        
        return input_tensor
    
    def detect(self, image):
        """
        Run detection on the image (optimized for real-time)
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            List of detections with format [x1, y1, x2, y2, confidence, class_id]
        """
        # PERFORMANCE OPTIMIZATION: Skip detection if frame skip is active
        if hasattr(self, 'frame_skip_interval') and self.frame_skip_interval > 1:
            if self.frame_count % self.frame_skip_interval != 0:
                if hasattr(self, 'last_detections'):
                    return self.last_detections
        
        # Preprocess image
        input_tensor = self.preprocess_image(image)
        
        # Set input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)
        
        # Run inference
        self.interpreter.invoke()
        
        # Get output tensor (YOLO format: [1, 5, 8400])
        output = self.interpreter.get_tensor(self.output_details[0]['index'])[0]  # Shape: [5, 8400]
        
        # PERFORMANCE OPTIMIZATION: Faster detection parsing
        valid_detections = []
        
        # Use numpy operations for faster processing
        confidences = output[4, :]
        valid_indices = np.where(confidences >= self.confidence_threshold)[0]
        
        if len(valid_indices) > 0:
            # Get coordinates for valid detections only
            x_centers = output[0, valid_indices]
            y_centers = output[1, valid_indices]
            widths = output[2, valid_indices]
            heights = output[3, valid_indices]
            valid_confidences = confidences[valid_indices]
            
            # Convert to pixel coordinates (vectorized)
            x1 = np.clip((x_centers - widths/2) * image.shape[1], 0, image.shape[1])
            y1 = np.clip((y_centers - heights/2) * image.shape[0], 0, image.shape[0])
            x2 = np.clip((x_centers + widths/2) * image.shape[1], 0, image.shape[1])
            y2 = np.clip((y_centers + heights/2) * image.shape[0], 0, image.shape[0])
            
            # Convert to integers and create detection list
            for i in range(len(valid_indices)):
                valid_detections.append([
                    int(x1[i]), int(y1[i]), int(x2[i]), int(y2[i]), 
                    float(valid_confidences[i]), 0
                ])
        
        # PERFORMANCE OPTIMIZATION: Limit maximum detections
        if len(valid_detections) > 10:
            # Sort by confidence and keep top 10
            valid_detections = sorted(valid_detections, key=lambda x: x[4], reverse=True)[:10]
        
        # Apply non-maximum suppression only if needed
        if len(valid_detections) > 1:
            valid_detections = self.non_max_suppression(valid_detections)
        
        # Store for frame skipping
        self.last_detections = valid_detections
        
        return valid_detections
    
    def non_max_suppression(self, detections):
        """
        Apply non-maximum suppression to remove overlapping detections
        """
        if not detections:
            return []
        
        # Sort by confidence
        detections = sorted(detections, key=lambda x: x[4], reverse=True)
        
        filtered_detections = []
        
        while detections:
            # Take the detection with highest confidence
            current = detections.pop(0)
            filtered_detections.append(current)
            
            # Remove overlapping detections
            remaining = []
            for detection in detections:
                iou = self.calculate_iou(current, detection)
                if iou < self.nms_threshold:
                    remaining.append(detection)
            
            detections = remaining
        
        return filtered_detections
    
    def calculate_iou(self, box1, box2):
        """
        Calculate Intersection over Union between two bounding boxes
        """
        x1_1, y1_1, x2_1, y2_1 = box1[:4]
        x1_2, y1_2, x2_2, y2_2 = box2[:4]
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y2_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def draw_detections(self, image, detections):
        """
        Draw detection boxes and labels on the image (optimized for Pi)
        """
        # Draw bounding boxes and labels
        for i, detection in enumerate(detections):
            x1, y1, x2, y2, confidence, class_id = detection
            
            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"Milk {i+1}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            
            # Position label above the box
            label_x = max(0, x1)
            label_y = max(0, y1 - 10)
            
            # Draw label background
            cv2.rectangle(image, (label_x, label_y - label_size[1] - 10), 
                         (label_x + label_size[0], label_y), (0, 255, 0), -1)
            
            # Draw label text
            cv2.putText(image, label, (label_x, label_y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return image
    
    def set_frame_skip(self, interval):
        """
        Set frame skip interval for performance optimization
        interval=1: process every frame (best quality, lower FPS)
        interval=2: process every 2nd frame (2x faster)
        interval=3: process every 3rd frame (3x faster)
        """
        self.frame_skip_interval = max(1, interval)
        print(f"Frame skip interval set to {self.frame_skip_interval}")
    
    def enable_low_latency_mode(self):
        """
        Enable low-latency mode for production line applications
        Reduces detection delay and improves accuracy
        """
        print("🚀 Low-latency mode enabled for production line")
        
        # Optimize for minimal delay
        self.frame_skip_interval = 1  # Process every frame
        self.target_fps = 60  # Changed from 30 to 60 FPS
        
        # Reduce confidence threshold for faster detection
        if self.confidence_threshold > 0.4:
            self.confidence_threshold = 0.4
            print(f"Adjusted confidence threshold to {self.confidence_threshold} for low latency")
        
        # Optimize NMS for speed
        if self.nms_threshold > 0.3:
            self.nms_threshold = 0.3
            print(f"Adjusted NMS threshold to {self.nms_threshold} for low latency")
        
        # Enable adaptive processing
        self.adaptive_processing = True
        
        print("Low-latency optimizations applied:")
        print("  • Process every frame")
        print("  • Target 60 FPS")  # Updated from 30 to 60
        print("  • Reduced confidence threshold")
        print("  • Optimized NMS")
    
    def set_conveyor_speed(self, speed_mps):
        """
        Set conveyor belt speed in meters per second
        
        Args:
            speed_mps: Speed in meters per second
        """
        self.conveyor_speed = speed_mps
        print(f"Conveyor speed set to {speed_mps:.2f} m/s")
        
        # Auto-adjust frame skip based on conveyor speed
        if speed_mps > 0:
            # Calculate required FPS to match conveyor speed
            # Assuming we need to detect objects every 0.1 meters
            required_fps = speed_mps / 0.1
            self.target_fps = min(30, max(5, required_fps))
            
            if required_fps > 20:
                self.frame_skip_interval = 3
                print(f"High speed detected: Processing every 3rd frame")
            elif required_fps > 15:
                self.frame_skip_interval = 2
                print(f"Medium speed detected: Processing every 2nd frame")
            else:
                self.frame_skip_interval = 1
                print(f"Low speed detected: Processing every frame")
    
    def detect_conveyor_speed(self, detections, frame_width, frame_height):
        """
        Automatically detect conveyor belt speed from object movement
        
        Args:
            detections: List of detections from current frame
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels
        """
        if not self.speed_detection_enabled or not detections:
            return
        
        current_time = time.time()
        
        # Store detection positions and timestamps
        for detection in detections:
            x1, y1, x2, y2, confidence, class_id = detection
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            self.speed_detection_frames.append({
                'timestamp': current_time,
                'center_x': center_x,
                'center_y': center_y,
                'confidence': confidence
            })
        
        # Keep only recent detections (last 5 seconds)
        cutoff_time = current_time - 5.0
        self.speed_detection_frames = [
            f for f in self.speed_detection_frames 
            if f['timestamp'] > cutoff_time
        ]
        
        # Calculate speed if we have enough data
        if len(self.speed_detection_frames) >= 3:
            # Find objects moving horizontally (conveyor direction)
            horizontal_movements = []
            
            for i in range(1, len(self.speed_detection_frames)):
                prev_frame = self.speed_detection_frames[i-1]
                curr_frame = self.speed_detection_frames[i]
                
                time_diff = curr_frame['timestamp'] - prev_frame['timestamp']
                x_diff = curr_frame['center_x'] - prev_frame['center_x']
                y_diff = curr_frame['center_y'] - prev_frame['center_y']
                
                # Only consider horizontal movement (conveyor direction)
                if abs(x_diff) > abs(y_diff) and time_diff > 0:
                    # Convert pixels to meters and calculate speed
                    distance_m = abs(x_diff) / self.pixel_to_meter_ratio
                    speed_mps = distance_m / time_diff
                    
                    if 0.01 < speed_mps < 10.0:  # Reasonable speed range
                        horizontal_movements.append(speed_mps)
            
            if horizontal_movements:
                # Calculate average speed
                avg_speed = sum(horizontal_movements) / len(horizontal_movements)
                self.conveyor_speed = avg_speed
                
                # Auto-adjust processing based on detected speed
                if self.adaptive_processing:
                    self.auto_adjust_processing()
    
    def auto_adjust_processing(self):
        """
        Automatically adjust processing parameters based on conveyor speed
        """
        if self.conveyor_speed <= 0:
            return
        
        # Calculate required detection frequency
        # We want to detect objects every 0.1 meters on the conveyor
        required_detection_freq = self.conveyor_speed / 0.1
        
        # Adjust frame skip interval
        if required_detection_freq > 25:
            new_interval = 3
        elif required_detection_freq > 15:
            new_interval = 2
        else:
            new_interval = 1
        
        if new_interval != self.frame_skip_interval:
            self.frame_skip_interval = new_interval
            print(f"Auto-adjusted: Processing every {new_interval} frame(s) for {self.conveyor_speed:.2f} m/s conveyor")
        
        # Adjust confidence threshold based on speed
        if self.conveyor_speed > 2.0:  # High speed
            if self.confidence_threshold < 0.7:
                self.confidence_threshold = 0.7
                print(f"Auto-adjusted confidence threshold to {self.confidence_threshold} for high speed")
        elif self.conveyor_speed > 1.0:  # Medium speed
            if self.confidence_threshold < 0.6:
                self.confidence_threshold = 0.6
                print(f"Auto-adjusted confidence threshold to {self.confidence_threshold} for medium speed")
    
    def enable_production_line_mode(self, conveyor_width_m=0.5, target_detection_gap_m=0.1):
        """
        Enable production line mode for conveyor belt synchronization
        
        Args:
            conveyor_width_m: Width of conveyor belt in meters
            target_detection_gap_m: Target gap between detections in meters
        """
        self.production_line_mode = True
        self.conveyor_width = conveyor_width_m
        self.adaptive_processing = True
        self.speed_detection_enabled = True
        
        # Calculate pixel-to-meter ratio based on camera setup
        # This should be calibrated for your specific camera position
        self.pixel_to_meter_ratio = 1000.0  # pixels per meter (adjustable)
        
        print(f"Production line mode enabled:")
        print(f"  Conveyor width: {conveyor_width_m} m")
        print(f"  Target detection gap: {target_detection_gap_m} m")
        print(f"  Pixel-to-meter ratio: {self.pixel_to_meter_ratio:.1f} px/m")
    
    def optimize_for_performance(self, target_fps=60):  # Changed default from 15 to 60
        """
        Automatically optimize settings for target FPS
        """
        if target_fps >= 50:  # High FPS mode (50+ FPS)
            self.frame_skip_interval = 1
            print("Performance mode: HIGH FPS - Processing every frame for 50+ FPS")
        elif target_fps >= 30:  # Medium FPS mode (30-49 FPS)
            self.frame_skip_interval = 1
            print("Performance mode: MEDIUM FPS - Processing every frame for 30+ FPS")
        elif target_fps >= 15:  # Balanced mode (15-29 FPS)
            self.frame_skip_interval = 2
            print("Performance mode: BALANCED - Processing every 2nd frame")
        else:  # Low FPS mode (<15 FPS)
            self.frame_skip_interval = 3
            print("Performance mode: LOW FPS - Processing every 3rd frame")
    
    def calculate_fps(self):
        """Calculate and update FPS"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_time)
            self.frame_count = 0
            self.last_time = current_time
    
    def process_frame(self, frame):
        """
        Process a single frame and return detection results (optimized for low lag)
        """
        # PERFORMANCE OPTIMIZATION: Smart frame skipping for minimal lag
        self.frame_skip_counter += 1
        
        # Skip frame processing if not needed
        if self.frame_skip_interval > 1:
            if self.frame_count % self.frame_skip_interval != 0:
                # Return cached result with minimal processing
                if hasattr(self, 'last_detections') and hasattr(self, 'last_result_frame'):
                    # Just update FPS counter and return cached frame
                    self.calculate_fps()
                    return self.last_result_frame, self.last_detections
        
        # Run detection (only when needed)
        detections = self.detect(frame)
        
        # CONVEYOR BELT SYNCHRONIZATION: Detect speed from object movement
        if self.production_line_mode and self.speed_detection_enabled:
            self.detect_conveyor_speed(detections, frame.shape[1], frame.shape[0])
        
        # Store detections for frame skipping
        self.last_detections = detections
        
        # PERFORMANCE OPTIMIZATION: Only draw detections when displaying
        if self.frame_count % 2 == 0:  # Update display every 2nd frame
            result_frame = self.draw_detections(frame.copy(), detections)
            self.last_result_frame = result_frame
        else:
            # Use cached frame for non-display frames
            if hasattr(self, 'last_result_frame'):
                result_frame = self.last_result_frame
            else:
                result_frame = frame.copy()
        
        # Add minimal info overlay (only essential text)
        if self.frame_count % 2 == 0:  # Update text every 2nd frame
            # Basic info
            cv2.putText(result_frame, f"Det: {len(detections)} | FPS: {self.fps:.1f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Conveyor info (only if enabled)
            if self.production_line_mode and self.conveyor_speed > 0:
                cv2.putText(result_frame, f"Speed: {self.conveyor_speed:.1f} m/s", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        return result_frame, detections
    
    def calculate_detection_coverage(self, detections, frame_width, frame_height):
        """
        Calculate detection coverage percentage across the frame
        """
        if not detections:
            return 0.0
        
        # Calculate total area covered by detections
        total_coverage = 0
        for detection in detections:
            x1, y1, x2, y2, confidence, class_id = detection
            area = (x2 - x1) * (y2 - y1)
            total_coverage += area
        
        # Calculate percentage of frame covered
        frame_area = frame_width * frame_height
        coverage_percent = (total_coverage / frame_area) * 100
        
        return min(100.0, coverage_percent)
    
    def start_camera_detection(self, camera_index=0, resolution=(640, 480), target_fps=60):  # Changed from 15 to 60
        """
        Start real-time camera detection
        
        Args:
            camera_index: Camera device index (usually 0 for Pi Camera)
            resolution: Camera resolution (width, height)
            target_fps: Target FPS for performance optimization
        """
        print(f"Starting camera detection with resolution {resolution}")
        print("Press 'q' to quit, 's' to save current frame, '1/2/3' to set frame skip")
        print("Press 'c' to toggle conveyor mode, 'v' to set conveyor speed, 'l' for low-latency mode")
        
        # PERFORMANCE OPTIMIZATION: Auto-optimize for target FPS
        self.optimize_for_performance(target_fps)
        
        # Initialize camera
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"Error: Could not open camera {camera_index}")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        cap.set(cv2.CAP_PROP_FPS, target_fps)
        
        # PERFORMANCE OPTIMIZATION: Reduce buffer size for high FPS
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Set flag for OpenCV camera (outputs BGR)
        self.using_picamera2 = False
        
        # Create output directory for saved frames
        output_dir = Path("saved_frames")
        output_dir.mkdir(exist_ok=True)
        
        self.running = True
        
        try:
            while self.running:
                # Capture frame
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Process frame
                result_frame, detections = self.process_frame(frame)
                
                # Calculate FPS
                self.calculate_fps()
                
                # PERFORMANCE OPTIMIZATION: Reduce display frequency
                if self.frame_count % 2 == 0:  # Update display every 2nd frame
                    cv2.imshow('Milk Detection - Raspberry Pi', result_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save current frame
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = output_dir / f"milk_detection_{timestamp}.jpg"
                    cv2.imwrite(str(filename), result_frame)
                    print(f"Frame saved: {filename}")
                elif key == ord('1'):
                    self.set_frame_skip(1)
                elif key == ord('2'):
                    self.set_frame_skip(2)
                elif key == ord('3'):
                    self.set_frame_skip(3)
                elif key == ord('c'):
                    # Toggle conveyor mode
                    if not self.production_line_mode:
                        self.enable_production_line_mode()
                        print("Conveyor mode enabled")
                    else:
                        self.production_line_mode = False
                        self.speed_detection_enabled = False
                        print("Conveyor mode disabled")
                elif key == ord('v'):
                    # Set conveyor speed manually
                    try:
                        speed_input = input("Enter conveyor speed (m/s): ")
                        speed = float(speed_input)
                        self.set_conveyor_speed(speed)
                    except (ValueError, EOFError):
                        print("Invalid speed value")
                elif key == ord('l'):
                    # Toggle low-latency mode
                    if hasattr(self, 'low_latency_enabled') and self.low_latency_enabled:
                        # Disable low-latency mode
                        self.low_latency_enabled = False
                        self.frame_skip_interval = 2
                        self.target_fps = 15
                        print("Low-latency mode disabled")
                    else:
                        # Enable low-latency mode
                        self.enable_low_latency_mode()
                        self.low_latency_enabled = True
                
                # Print detection info every 30 frames
                if self.frame_count % 30 == 0:
                    status = f"FPS: {self.fps:.1f}, Detections: {len(detections)}, Frame Skip: {self.frame_skip_interval}"
                    if self.production_line_mode:
                        status += f", Conveyor: {self.conveyor_speed:.2f} m/s"
                    print(status)
                
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            self.running = False
            cap.release()
            cv2.destroyAllWindows()
            print("Camera detection stopped")
    
    def start_picamera2_detection(self, resolution=(640, 480), target_fps=60):  # Changed from 15 to 60
        """
        Start real-time detection using PiCamera2 (recommended for Pi)
        
        Args:
            resolution: Camera resolution (width, height)
            target_fps: Target FPS for performance optimization
        """
        try:
            from picamera2 import Picamera2
            from picamera2.encoders import JpegEncoder
            from picamera2.sensor_format import SensorFormat
        except ImportError:
            print("PiCamera2 not available, falling back to OpenCV camera")
            self.start_camera_detection(0, resolution, target_fps)
            return
        
        print(f"Starting PiCamera2 detection with resolution {resolution}")
        print("Press 'q' to quit, 's' to save current frame, '1/2/3' to set frame skip")
        print("Press 'c' to toggle conveyor mode, 'v' to set conveyor speed, 'l' for low-latency mode")
        
        # PERFORMANCE OPTIMIZATION: Auto-optimize for target FPS
        self.optimize_for_performance(target_fps)
        
        # Initialize PiCamera2
        picam2 = Picamera2()
        
        # Configure camera with minimal, widely-supported settings
        config = picam2.create_preview_configuration(
            main={"size": resolution, "format": "RGB888"},
            buffer_count=1  # Reduced buffer for lower latency at high FPS
            # Remove custom controls to avoid compatibility issues
        )
        picam2.configure(config)
        
        # Start camera
        picam2.start()
        
        # Wait for camera to stabilize and apply settings
        time.sleep(2)
        
        # Create output directory for saved frames
        output_dir = Path("saved_frames")
        output_dir.mkdir(exist_ok=True)
        
        self.running = True
        self.using_picamera2 = True # Set flag for PiCamera2
        
        try:
            while self.running:
                # Capture frame
                frame = picam2.capture_array()
                
                # Process frame
                result_frame, detections = self.process_frame(frame)
                
                # Calculate FPS
                self.calculate_fps()
                
                # PERFORMANCE OPTIMIZATION: Reduce display frequency
                if self.frame_count % 2 == 0:  # Update display every 2nd frame
                    cv2.imshow('Milk Detection - PiCamera2', result_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save current frame
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = output_dir / f"milk_detection_{timestamp}.jpg"
                    cv2.imwrite(str(filename), result_frame)
                    print(f"Frame saved: {filename}")
                elif key == ord('1'):
                    self.set_frame_skip(1)
                elif key == ord('2'):
                    self.set_frame_skip(2)
                elif key == ord('3'):
                    self.set_frame_skip(3)
                elif key == ord('c'):
                    # Toggle conveyor mode
                    if not self.production_line_mode:
                        self.enable_production_line_mode()
                        print("Conveyor mode enabled")
                    else:
                        self.production_line_mode = False
                        self.speed_detection_enabled = False
                        print("Conveyor mode disabled")
                elif key == ord('v'):
                    # Set conveyor speed manually
                    try:
                        speed_input = input("Enter conveyor speed (m/s): ")
                        speed = float(speed_input)
                        self.set_conveyor_speed(speed)
                    except (ValueError, EOFError):
                        print("Invalid speed value")
                elif key == ord('l'):
                    # Toggle low-latency mode
                    if hasattr(self, 'low_latency_enabled') and self.low_latency_enabled:
                        # Disable low-latency mode
                        self.low_latency_enabled = False
                        self.frame_skip_interval = 2
                        self.target_fps = 15
                        print("Low-latency mode disabled")
                    else:
                        # Enable low-latency mode
                        self.enable_low_latency_mode()
                        self.low_latency_enabled = True
                
                # Print detection info every 30 frames
                if self.frame_count % 30 == 0:
                    status = f"FPS: {self.fps:.1f}, Detections: {len(detections)}, Frame Skip: {self.frame_skip_interval}"
                    if self.production_line_mode:
                        status += f", Conveyor: {self.conveyor_speed:.2f} m/s"
                    print(status)
                
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            self.running = False
            picam2.close()
            cv2.destroyAllWindows()
            print("PiCamera2 detection stopped")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down gracefully...")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Raspberry Pi Milk Packet Detector")
    parser.add_argument("--model", default="model/best_float32.tflite", 
                       help="Path to TFLite model")
    parser.add_argument("--confidence", type=float, default=0.5,
                       help="Confidence threshold (default: 0.5)")
    parser.add_argument("--nms", type=float, default=0.4,
                       help="NMS threshold (default: 0.4)")
    parser.add_argument("--resolution", default="640x480",
                       help="Camera resolution (default: 640x480)")
    parser.add_argument("--camera", type=int, default=0,
                       help="Camera device index (default: 0)")
    parser.add_argument("--use-picamera2", action="store_true",
                       help="Use PiCamera2 instead of OpenCV camera")
    parser.add_argument("--target-fps", type=int, default=60,  # Changed from 15 to 60
                       help="Target FPS for performance optimization (default: 60)")
    parser.add_argument("--performance-mode", choices=["quality", "balanced", "speed"], default="balanced",
                       help="Performance mode: quality (best accuracy), balanced (default), speed (best FPS)")
    parser.add_argument("--conveyor-mode", action="store_true",
                       help="Enable conveyor belt synchronization mode")
    parser.add_argument("--conveyor-speed", type=float, default=0.0,
                       help="Set conveyor belt speed in m/s (0 = auto-detect)")
    parser.add_argument("--conveyor-width", type=float, default=0.5,
                       help="Conveyor belt width in meters (default: 0.5)")
    parser.add_argument("--low-latency", action="store_true",
                       help="Enable low-latency mode for production line (minimal delay)")
    
    args = parser.parse_args()
    
    # Parse resolution
    try:
        width, height = map(int, args.resolution.split('x'))
        resolution = (width, height)
    except ValueError:
        print("Error: Invalid resolution format. Use WIDTHxHEIGHT (e.g., 640x480)")
        return
    
    # Check if model exists
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        return
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize detector
    detector = RaspberryMilkDetector(args.model, args.confidence, args.nms)
    
    # PERFORMANCE OPTIMIZATION: Apply performance mode settings
    if args.performance_mode == "speed":
        detector.optimize_for_performance(60)  # Changed from 10 to 60
        print("Performance mode: SPEED (target: 60 FPS)")
    elif args.performance_mode == "quality":
        detector.optimize_for_performance(60)  # Changed from 30 to 60
        print("Performance mode: QUALITY (target: 60 FPS)")
    else:  # balanced
        detector.optimize_for_performance(args.target_fps)
        print("Performance mode: BALANCED")
    
    # CONVEYOR BELT SYNCHRONIZATION: Enable if requested
    if args.conveyor_mode:
        detector.enable_production_line_mode(args.conveyor_width)
        print(f"Conveyor mode enabled with width: {args.conveyor_width}m")
        
        if args.conveyor_speed > 0:
            detector.set_conveyor_speed(args.conveyor_speed)
            print(f"Conveyor speed set to: {args.conveyor_speed} m/s")
        else:
            print("Conveyor speed: Auto-detection enabled")
    
    # LOW-LATENCY MODE: Enable if requested
    if args.low_latency:
        detector.enable_low_latency_mode()
        print("Low-latency mode enabled for production line")
    
    print("Raspberry Pi Milk Detector Started!")
    print(f"Model: {args.model}")
    print(f"Resolution: {resolution}")
    print(f"Target FPS: {args.target_fps}")
    print(f"Confidence threshold: {args.confidence}")
    print(f"NMS threshold: {args.nms}")
    print(f"Frame skip interval: {detector.frame_skip_interval}")
    
    if args.conveyor_mode:
        print(f"Conveyor mode: ENABLED")
        print(f"Conveyor width: {args.conveyor_width}m")
        print(f"Speed detection: {'Manual' if args.conveyor_speed > 0 else 'Auto'}")
    
    try:
        if args.use_picamera2:
            detector.start_picamera2_detection(resolution, args.target_fps)
        else:
            detector.start_camera_detection(args.camera, resolution, args.target_fps)
    except Exception as e:
        print(f"Error during detection: {e}")
        print("Falling back to OpenCV camera...")
        detector.start_camera_detection(args.camera, resolution, args.target_fps)

if __name__ == "__main__":
    main() 