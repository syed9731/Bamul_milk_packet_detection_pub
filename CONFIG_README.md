# Configuration System for Raspberry Pi Milk Detection

This configuration system provides centralized control over all parameters for the milk detection system, making it easy to adjust settings without modifying the main code.

## Quick Start

```python
from config import config

# Adjust confidence threshold
config.CONFIDENCE_THRESHOLD = 0.7

# Enable ROI and set boundaries
config.ENABLE_ROI = True
config.ROI_X1 = 0.2  # 20% from left
config.ROI_Y1 = 0.2  # 20% from top
config.ROI_X2 = 0.8  # 80% from left
config.ROY_Y2 = 0.8  # 80% from top

# Print current configuration
config.print_config()
```

## Key Configuration Categories

### 1. Detection Thresholds
- **`CONFIDENCE_THRESHOLD`** (0.0 - 1.0): Minimum confidence for detection
  - Higher values = fewer, more confident detections
  - Lower values = more detections, may include false positives
- **`NMS_THRESHOLD`** (0.0 - 1.0): Non-maximum suppression threshold
  - Higher values = more overlapping detections allowed
  - Lower values = stricter overlap filtering
- **`IOU_THRESHOLD`** (0.0 - 1.0): Intersection over Union threshold

### 2. ROI (Region of Interest)
- **`ENABLE_ROI`**: Enable/disable ROI filtering
- **`ROI_X1, ROI_Y1`**: Top-left boundary (0.0 - 1.0, relative to image)
- **`ROI_X2, ROI_Y2`**: Bottom-right boundary (0.0 - 1.0, relative to image)

**Example ROI configurations:**
```python
# Center area (25% margin on all sides)
config.ROI_X1 = 0.25
config.ROI_Y1 = 0.25
config.ROI_X2 = 0.75
config.ROI_Y2 = 0.75

# Left half of image
config.ROI_X1 = 0.0
config.ROI_Y1 = 0.0
config.ROI_X2 = 0.5
config.ROI_Y2 = 1.0

# Top third of image
config.ROI_X1 = 0.0
config.ROI_Y1 = 0.0
config.ROI_X2 = 1.0
config.ROI_Y2 = 0.33
```

### 3. Camera Settings
- **`CAMERA_RESOLUTION`**: Tuple of (width, height) in pixels
- **`CAMERA_FPS`**: Frames per second
- **`USE_PICAMERA2`**: Use PiCamera2 (True) or OpenCV camera (False)

**Common resolutions:**
```python
# Performance optimized
config.CAMERA_RESOLUTION = (320, 240)    # QVGA
config.CAMERA_RESOLUTION = (640, 480)    # VGA

# Quality optimized
config.CAMERA_RESOLUTION = (1280, 720)   # HD
config.CAMERA_RESOLUTION = (1920, 1080)  # Full HD
```

### 4. Performance Settings
- **`NUM_THREADS`**: Number of threads for TFLite interpreter
  - Pi 4: 4 threads recommended
  - Pi Zero: 1-2 threads recommended
- **`FRAME_SKIP`**: Skip frames for performance (0 = process all)
- **`MAX_DETECTIONS`**: Maximum detections to process per frame

### 5. Visualization
- **`BOX_COLOR`**: BGR color for bounding boxes (default: green)
- **`LABEL_COLOR`**: BGR color for text labels (default: black)
- **`LINE_THICKNESS`**: Thickness of bounding box lines
- **`FONT_SCALE`**: Size of text labels

## Predefined Configuration Profiles

### High Performance Mode
```python
config.CAMERA_RESOLUTION = (320, 240)
config.CAMERA_FPS = 15
config.NUM_THREADS = 2
config.FRAME_SKIP = 1
config.ENABLE_FPS_DISPLAY = True
```

### High Quality Mode
```python
config.CAMERA_RESOLUTION = (1280, 720)
config.CAMERA_FPS = 30
config.QUALITY = 100
config.SAVE_DETECTIONS = True
config.ENABLE_POSTPROCESSING = True
```

### Strict Detection Mode
```python
config.CONFIDENCE_THRESHOLD = 0.8
config.NMS_THRESHOLD = 0.3
config.ENABLE_ROI = True
config.ROI_X1 = 0.2
config.ROI_Y1 = 0.2
config.ROI_X2 = 0.8
config.ROI_Y2 = 0.8
```

### Loose Detection Mode
```python
config.CONFIDENCE_THRESHOLD = 0.3
config.NMS_THRESHOLD = 0.6
config.ENABLE_ROI = False
config.MAX_DETECTIONS = 20
```

## Advanced Usage

### Custom Configuration Classes
```python
class NightModeConfig:
    def __init__(self):
        self.CONFIDENCE_THRESHOLD = 0.6
        self.CAMERA_RESOLUTION = (640, 480)
        self.CAMERA_FPS = 15
        self.ENABLE_ROI = True
        self.ROI_X1 = 0.1
        self.ROI_Y1 = 0.1
        self.ROI_X2 = 0.9
        self.ROI_Y2 = 0.9

# Use custom config
night_config = NightModeConfig()
```

### Dynamic Configuration Updates
```python
def adjust_for_lighting(light_level):
    """Dynamically adjust confidence based on lighting"""
    if light_level < 0.3:  # Low light
        config.CONFIDENCE_THRESHOLD = 0.4
        config.ENABLE_ROI = True
    elif light_level > 0.7:  # Bright light
        config.CONFIDENCE_THRESHOLD = 0.6
        config.ENABLE_ROI = False
    else:  # Normal light
        config.CONFIDENCE_THRESHOLD = 0.5
        config.ENABLE_ROI = True
```

### Configuration Validation
```python
try:
    config.CONFIDENCE_THRESHOLD = 1.5  # Invalid value
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Integration with Main Code

To use the configuration in your main detection code:

```python
from config import config

class MilkDetector:
    def __init__(self):
        self.confidence_threshold = config.CONFIDENCE_THRESHOLD
        self.nms_threshold = config.NMS_THRESHOLD
        
    def detect(self, image):
        # Use config values
        if config.ENABLE_ROI:
            roi_coords = config.get_roi_coordinates(image.shape[1], image.shape[0])
            # Apply ROI filtering
        
        # Apply confidence threshold
        if detection[4] >= config.CONFIDENCE_THRESHOLD:
            # Process detection
```

## Configuration File Structure

```
raspberry/
├── config.py              # Main configuration file
├── config_example.py      # Usage examples
├── CONFIG_README.md       # This file
├── raspberry_milk_detector.py
└── ...
```

## Best Practices

1. **Start with defaults**: Begin with default values and adjust gradually
2. **Test thoroughly**: Test configuration changes with various lighting conditions
3. **Document changes**: Keep notes of what works best for your setup
4. **Performance balance**: Balance detection accuracy with processing speed
5. **ROI optimization**: Use ROI to focus on areas where milk packets typically appear

## Troubleshooting

### Common Issues

1. **Too many false positives**: Increase `CONFIDENCE_THRESHOLD`
2. **Missing detections**: Decrease `CONFIDENCE_THRESHOLD` or adjust ROI
3. **Low FPS**: Reduce resolution, increase `FRAME_SKIP`, or reduce `NUM_THREADS`
4. **High memory usage**: Reduce `CAMERA_RESOLUTION` or disable `SAVE_DETECTIONS`

### Performance Tuning

```python
# For Pi Zero
config.CAMERA_RESOLUTION = (320, 240)
config.NUM_THREADS = 1
config.FRAME_SKIP = 2

# For Pi 4
config.CAMERA_RESOLUTION = (640, 480)
config.NUM_THREADS = 4
config.FRAME_SKIP = 0
```

## Support

For issues or questions about the configuration system, check:
1. This README file
2. The example script (`config_example.py`)
3. The main configuration file (`config.py`) for parameter descriptions 