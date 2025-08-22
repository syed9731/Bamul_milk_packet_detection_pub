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
        
        # Convert to RGB if needed
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
        # Preprocess image
        input_tensor = self.preprocess_image(image)
        
        # Set input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)
        
        # Run inference
        self.interpreter.invoke()
        
        # Get output tensor (YOLO format: [1, 5, 8400])
        output = self.interpreter.get_tensor(self.output_details[0]['index'])[0]  # Shape: [5, 8400]
        
        # Parse YOLO output format
        valid_detections = []
        
        for i in range(output.shape[1]):  # Iterate through 8400 possible detections
            confidence = output[4, i]
            
            if confidence >= self.confidence_threshold:
                # Get normalized coordinates
                x_center = output[0, i]
                y_center = output[1, i]
                width = output[2, i]
                height = output[3, i]
                
                # Convert to pixel coordinates
                x1 = int((x_center - width/2) * image.shape[1])
                y1 = int((y_center - height/2) * image.shape[0])
                x2 = int((x_center + width/2) * image.shape[1])
                y2 = int((y_center + height/2) * image.shape[0])
                
                # Ensure coordinates are within image bounds
                x1 = max(0, min(x1, image.shape[1]))
                y1 = max(0, min(y1, image.shape[0]))
                x2 = max(0, min(x2, image.shape[1]))
                y2 = max(0, min(y2, image.shape[0]))
                
                # Add detection (class_id is 0 for single class model)
                valid_detections.append([x1, y1, x2, y2, confidence, 0])
        
        # Apply non-maximum suppression
        if valid_detections:
            valid_detections = self.non_max_suppression(valid_detections)
        
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
    
    def optimize_for_performance(self, target_fps=15):
        """
        Automatically optimize settings for target FPS
        """
        if target_fps <= 10:
            self.frame_skip_interval = 3
            print("Performance mode: Processing every 3rd frame")
        elif target_fps <= 15:
            self.frame_skip_interval = 2
            print("Performance mode: Processing every 2nd frame")
        else:
            self.frame_skip_interval = 1
            print("Performance mode: Processing every frame")
    
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
        Process a single frame and return detection results
        """
        # PERFORMANCE OPTIMIZATION: Frame skipping for better FPS
        self.frame_skip_counter += 1
        if self.frame_skip_counter % self.frame_skip_interval != 0:
            # Skip this frame, return original with previous detections
            if hasattr(self, 'last_detections'):
                result_frame = self.draw_detections(frame.copy(), self.last_detections)
                # Add info overlay
                info_text = f"Detections: {len(self.last_detections)} | FPS: {self.fps:.1f} | Skipped"
                cv2.putText(result_frame, info_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                count_text = f"Milk Packets: {len(self.last_detections)}"
                cv2.putText(result_frame, count_text, (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                return result_frame, self.last_detections
        
        # Run detection
        detections = self.detect(frame)
        
        # Store detections for frame skipping
        self.last_detections = detections
        
        # Draw detections
        result_frame = self.draw_detections(frame.copy(), detections)
        
        # Add info overlay
        info_text = f"Detections: {len(detections)} | FPS: {self.fps:.1f}"
        cv2.putText(result_frame, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add count text
        count_text = f"Milk Packets: {len(detections)}"
        cv2.putText(result_frame, count_text, (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return result_frame, detections
    
    def start_camera_detection(self, camera_index=0, resolution=(640, 480), target_fps=15):
        """
        Start real-time camera detection
        
        Args:
            camera_index: Camera device index (usually 0 for Pi Camera)
            resolution: Camera resolution (width, height)
            target_fps: Target FPS for performance optimization
        """
        print(f"Starting camera detection with resolution {resolution}")
        print("Press 'q' to quit, 's' to save current frame, '1/2/3' to set frame skip")
        
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
        
        # PERFORMANCE OPTIMIZATION: Reduce buffer size
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
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
                
                # Print detection info every 30 frames
                if self.frame_count % 30 == 0:
                    print(f"FPS: {self.fps:.1f}, Detections: {len(detections)}, Frame Skip: {self.frame_skip_interval}")
                
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            self.running = False
            cap.release()
            cv2.destroyAllWindows()
            print("Camera detection stopped")
    
    def start_picamera2_detection(self, resolution=(640, 480), target_fps=15):
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
        
        # PERFORMANCE OPTIMIZATION: Auto-optimize for target FPS
        self.optimize_for_performance(target_fps)
        
        # Initialize PiCamera2
        picam2 = Picamera2()
        
        # Configure camera with performance optimizations
        config = picam2.create_preview_configuration(
            main={"size": resolution, "format": "RGB888"},
            buffer_count=2,  # Reduced buffer for lower latency
            controls={"FrameDurationLimits": (int(1000000/target_fps), int(1000000/target_fps))}
        )
        picam2.configure(config)
        
        # Start camera
        picam2.start()
        
        # Create output directory for saved frames
        output_dir = Path("saved_frames")
        output_dir.mkdir(exist_ok=True)
        
        self.running = True
        
        try:
            while self.running:
                # Capture frame
                frame = picam2.capture_array()
                
                # Convert from RGB to BGR for OpenCV
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
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
                
                # Print detection info every 30 frames
                if self.frame_count % 30 == 0:
                    print(f"FPS: {self.fps:.1f}, Detections: {len(detections)}, Frame Skip: {self.frame_skip_interval}")
                
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
    parser.add_argument("--target-fps", type=int, default=15,
                       help="Target FPS for performance optimization (default: 15)")
    parser.add_argument("--performance-mode", choices=["quality", "balanced", "speed"], default="balanced",
                       help="Performance mode: quality (best accuracy), balanced (default), speed (best FPS)")
    
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
        detector.optimize_for_performance(10)
        print("Performance mode: SPEED (target: 10+ FPS)")
    elif args.performance_mode == "quality":
        detector.optimize_for_performance(30)
        print("Performance mode: QUALITY (target: 30 FPS)")
    else:  # balanced
        detector.optimize_for_performance(args.target_fps)
        print("Performance mode: BALANCED")
    
    print("Raspberry Pi Milk Detector Started!")
    print(f"Model: {args.model}")
    print(f"Resolution: {resolution}")
    print(f"Target FPS: {args.target_fps}")
    print(f"Confidence threshold: {args.confidence}")
    print(f"NMS threshold: {args.nms}")
    print(f"Frame skip interval: {detector.frame_skip_interval}")
    
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