#!/usr/bin/env python3
"""
High-Performance 60 FPS Configuration for Raspberry Pi Milk Detector
Optimized for maximum frame rate and minimal latency
"""

# 60 FPS OPTIMIZATION SETTINGS
HIGH_FPS_CONFIG = {
    # Performance Settings
    'target_fps': 60,
    'frame_skip_interval': 1,  # Process every frame for maximum accuracy
    'performance_mode': 'speed',
    
    # Camera Settings
    'resolution': (640, 480),  # Lower resolution for higher FPS
    'buffer_size': 1,  # Minimal buffer for lowest latency
    'use_picamera2': True,  # PiCamera2 is generally faster than OpenCV
    
    # Detection Settings
    'confidence_threshold': 0.4,  # Lower threshold for faster detection
    'nms_threshold': 0.3,  # Faster NMS processing
    'max_detections': 5,  # Limit detections for speed
    
    # Processing Optimizations
    'enable_gpu_delegation': True,  # Use GPU if available
    'num_threads': 4,  # Use all 4 cores of Pi 4
    'adaptive_processing': True,
    
    # Display Settings
    'display_update_interval': 1,  # Update display every frame
    'show_fps': True,
    'show_detection_count': True,
    
    # Conveyor Settings (if using production line)
    'conveyor_mode': False,
    'low_latency_mode': True,
}

# ADVANCED 60 FPS OPTIMIZATIONS
ADVANCED_OPTIMIZATIONS = {
    # Memory Management
    'preallocate_tensors': True,
    'use_fixed_memory': True,
    
    # Frame Processing
    'skip_processing_on_no_change': True,
    'use_frame_difference': True,
    
    # Model Optimization
    'quantization': 'int8',  # Use int8 quantization if available
    'enable_xnnpack': True,  # Enable XNNPACK for ARM optimization
}

# CAMERA-SPECIFIC 60 FPS SETTINGS
CAMERA_OPTIMIZATIONS = {
    'picamera2': {
        'buffer_count': 1,
        'queue': False,  # Disable queuing for lower latency
        'controls': {
            'FrameDurationLimits': (16667, 16667),  # 60 FPS = 16.667ms per frame
            'NoiseReductionMode': 0,  # Disable noise reduction for speed
            'Sharpness': 0,  # Disable sharpening for speed
        }
    },
    'opencv': {
        'buffer_size': 1,
        'fourcc': 'MJPG',  # Use MJPG codec for better performance
        'backend': 'CAP_V4L2',  # Use V4L2 backend
    }
}

# PERFORMANCE PROFILES
PERFORMANCE_PROFILES = {
    'ultra_fast': {
        'description': 'Maximum speed, lower accuracy',
        'frame_skip': 1,
        'confidence_threshold': 0.3,
        'nms_threshold': 0.2,
        'max_detections': 3,
        'resolution': (480, 360),
    },
    'balanced_60fps': {
        'description': 'Balanced speed and accuracy for 60 FPS',
        'frame_skip': 1,
        'confidence_threshold': 0.4,
        'nms_threshold': 0.3,
        'max_detections': 5,
        'resolution': (640, 480),
    },
    'quality_60fps': {
        'description': 'High quality while maintaining 60 FPS',
        'frame_skip': 1,
        'confidence_threshold': 0.5,
        'nms_threshold': 0.4,
        'max_detections': 8,
        'resolution': (800, 600),
    }
}

def get_60fps_config(profile='balanced_60fps'):
    """
    Get configuration for 60 FPS operation
    
    Args:
        profile: Performance profile to use
        
    Returns:
        Dictionary with optimized settings
    """
    config = HIGH_FPS_CONFIG.copy()
    
    if profile in PERFORMANCE_PROFILES:
        profile_config = PERFORMANCE_PROFILES[profile]
        config.update(profile_config)
    
    return config

def print_60fps_optimizations():
    """Print all 60 FPS optimization settings"""
    print("🚀 60 FPS OPTIMIZATION SETTINGS")
    print("=" * 50)
    
    config = get_60fps_config()
    for key, value in config.items():
        print(f"{key}: {value}")
    
    print("\n📊 PERFORMANCE PROFILES")
    print("-" * 30)
    for profile, settings in PERFORMANCE_PROFILES.items():
        print(f"{profile}: {settings['description']}")
        for key, value in settings.items():
            if key != 'description':
                print(f"  {key}: {value}")
        print()

if __name__ == "__main__":
    print_60fps_optimizations() 