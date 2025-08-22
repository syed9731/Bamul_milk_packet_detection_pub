# PiCamera2 Color Shifting Fix

## Problem Description
PiCamera2 often experiences color shifting issues where:
- **Yellow objects appear blue**
- **Red objects appear green**
- **Overall colors are incorrect or washed out**

This is a common issue caused by improper color space configuration, white balance settings, and missing color correction parameters.

## Root Causes
1. **Missing color space configuration** - PiCamera2 needs explicit RGB888 format
2. **Incorrect white balance** - Auto white balance may not be properly configured
3. **Missing color correction matrix** - Camera needs proper color correction
4. **Incorrect color gains** - Red and blue color gains may be unbalanced
5. **Missing exposure controls** - Auto-exposure settings affect color reproduction

## Solutions Implemented

### 1. Fixed Main Detection Script (`raspberry_milk_detector.py`)
The main script now includes proper color correction settings:
- Explicit RGB888 format
- Auto-exposure and auto white balance enabled
- Neutral color gains (1.0, 1.0)
- Proper color correction matrix
- Balanced saturation, contrast, and brightness

### 2. Fixed Test Camera Script (`test_camera.py`)
Updated test script with the same color correction settings for consistency.

### 3. Color Calibration Tool (`color_calibration.py`)
Interactive tool to fine-tune color settings:
- Real-time color adjustment
- Save/load calibration settings
- Interactive controls for red/blue gains
- Saturation, contrast, and brightness adjustment

### 4. Simple Test Script (`test_color_fix.py`)
Quick test to verify color correction is working.

## How to Use

### Quick Fix
Run the main detection script with the updated configuration:
```bash
python raspberry_milk_detector.py --use-picamera2
```

### Test Color Correction
Test if the color fix is working:
```bash
python test_color_fix.py
```

### Interactive Calibration
For fine-tuning colors:
```bash
python color_calibration.py
```

## Color Calibration Tool Usage

### Interactive Mode
1. **Start calibration**: Option 1
2. **Place a white/yellow object** in front of the camera
3. **Adjust settings** using number keys:
   - `1`/`6`: Increase/decrease red gain
   - `2`/`7`: Increase/decrease blue gain
   - `3`/`8`: Increase/decrease saturation
   - `4`/`9`: Increase/decrease contrast
   - `5`: Increase brightness
4. **Save settings**: Press `s`
5. **Reset to defaults**: Press `r`
6. **Quit**: Press `q`

### Key Settings Explained

#### ColourGains (Red, Blue)
- **Default**: (1.0, 1.0) - Neutral
- **Increase red**: (1.5, 1.0) - More red, less blue
- **Increase blue**: (1.0, 1.5) - More blue, less red
- **For yellow objects appearing blue**: Increase red gain, decrease blue gain

#### White Balance
- **AwbEnable**: True - Auto white balance
- **AwbMode**: 0 - Auto mode
- **AeEnable**: True - Auto exposure

#### Color Correction Matrix
- **Identity matrix**: [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
- This ensures no artificial color transformation

## Advanced Configuration

### Manual Color Gains
If you know the exact values needed:
```python
controls = {
    "ColourGains": (1.2, 0.8),  # More red, less blue
    "Saturation": 1.1,           # Slightly more saturated
    "Contrast": 1.05,            # Slightly more contrast
}
```

### Custom Color Correction Matrix
For advanced users, you can create a custom color correction matrix:
```python
# Example: Enhance red channel, reduce blue channel
"ColourCorrectionMatrix": [1.1, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.9]
```

## Troubleshooting

### Colors Still Wrong
1. **Check lighting**: Ensure consistent lighting conditions
2. **Reset to defaults**: Use calibration tool option 5
3. **Manual adjustment**: Use interactive calibration mode
4. **Check camera hardware**: Ensure camera module is properly connected

### Camera Not Working
1. **Check PiCamera2 installation**: `pip list | grep picamera2`
2. **Check camera interface**: `vcgencmd get_camera`
3. **Check camera module**: Ensure it's enabled in raspi-config

### Performance Issues
1. **Reduce resolution**: Use 640x480 instead of higher resolutions
2. **Reduce FPS**: Lower target FPS in detection script
3. **Check temperature**: Ensure Pi is not overheating

## Technical Details

### Color Space
- **Input**: PiCamera2 captures in RGB888 format
- **Processing**: Convert to BGR for OpenCV compatibility
- **Output**: BGR format for display and saving

### Buffer Configuration
- **Buffer count**: 2-4 for optimal performance
- **Format**: RGB888 for best color accuracy
- **Size**: Configurable resolution

### Control Parameters
All color-related controls are documented in the PiCamera2 documentation:
- `ColourGains`: Red and blue channel gains
- `ColourCorrectionMatrix`: 3x3 color transformation matrix
- `AwbMode`: White balance algorithm selection
- `AeMeteringMode`: Exposure metering mode

## Files Modified
1. `raspberry_milk_detector.py` - Main detection script with color fix
2. `test_camera.py` - Test script with color fix
3. `color_calibration.py` - Interactive color calibration tool
4. `test_color_fix.py` - Simple color test script
5. `COLOR_FIX_README.md` - This documentation

## Testing
After applying fixes:
1. **Run test script**: Verify colors are correct
2. **Test with known objects**: Use objects with known colors
3. **Save test images**: Compare before/after images
4. **Check in different lighting**: Test under various conditions

## Support
If issues persist:
1. Check PiCamera2 version: `pip show picamera2`
2. Update PiCamera2: `pip install --upgrade picamera2`
3. Check camera firmware: `vcgencmd get_camera`
4. Review system logs: `dmesg | grep camera` 