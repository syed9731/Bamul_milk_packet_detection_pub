# Raspberry Pi 4 Milk Detection Deployment

This folder contains everything you need to deploy the milk detection system on a Raspberry Pi 4 with real-time camera input.

## 🍓 Features

- **Real-time Detection**: Live camera feed with instant milk packet detection
- **Optimized for Pi**: Uses tflite-runtime and optimized OpenCV for ARM architecture
- **Performance Monitoring**: Track CPU, memory, temperature, and FPS
- **Flexible Camera Support**: Works with both PiCamera2 and USB cameras
- **Auto-start Service**: Optional systemd service for boot-time startup
- **Frame Saving**: Save detected frames with timestamps
- **🚀 NEW: Performance Optimization**: Frame skipping, thread optimization, and performance modes

## 📋 Requirements

- Raspberry Pi 4 (2GB RAM minimum, 4GB+ recommended)
- Raspberry Pi Camera Module v2 or USB camera
- MicroSD card with Raspberry Pi OS (Bullseye or newer)
- Internet connection for initial setup

## 🚀 Quick Setup

### 1. Transfer Files to Pi

Copy the entire `raspberry` folder to your Raspberry Pi:
```bash
scp -r raspberry/ pi@your_pi_ip:/home/pi/
```

### 2. Run Setup Script

SSH into your Pi and run the setup script:
```bash
cd raspberry
chmod +x setup_pi.sh
./setup_pi.sh
```

The setup script will:
- Update system packages
- Install required dependencies
- Enable camera interface
- Create Python virtual environment
- Install optimized Python packages
- Create necessary directories
- Set up optional auto-start service

### 3. Test Camera

Ensure your camera is working:
```bash
# Test PiCamera2
libcamera-still -o test.jpg

# Or test USB camera
fswebcam test.jpg
```

## 📸 Usage

### 🚀 Quick Start (Optimized for Performance)

Use the optimized startup script for best performance:
```bash
./start_detection.sh
```

This automatically uses:
- PiCamera2 (best performance)
- 640x480 resolution
- 15 FPS target
- Speed performance mode
- Frame skipping optimization

### 🏭 Conveyor Belt Mode (Production Line Synchronization)

**NEW!** If your detection isn't matching conveyor belt speed, use the specialized conveyor mode:

```bash
# Quick conveyor belt setup
./start_conveyor_detection.sh

# Or manual conveyor mode
python raspberry_milk_detector.py --conveyor-mode --conveyor-width 0.5
```

**Conveyor Belt Features:**
- **Auto-speed detection** from object movement
- **Adaptive frame processing** to match production line speed
- **Real-time synchronization** with conveyor belt
- **Automatic calibration** for optimal performance
- **Production line mode** for industrial applications

**Calibration Tool:**
```bash
python calibrate_conveyor.py
```

This helps you:
- Position camera correctly above conveyor
- Set proper conveyor dimensions
- Calculate optimal detection parameters
- Generate recommended startup commands

### Basic Detection

Start the milk detector with default settings:
```bash
cd raspberry
source venv_pi/bin/activate
python raspberry_milk_detector.py
```

### 🎯 Performance-Optimized Options

#### Speed Mode (Best FPS)
```bash
# For maximum speed (10+ FPS)
python raspberry_milk_detector.py --performance-mode speed --resolution 320x240 --target-fps 15
```

#### Balanced Mode (Default)
```bash
# For balanced performance (10-15 FPS)
python raspberry_milk_detector.py --performance-mode balanced --resolution 640x480 --target-fps 15
```

#### Quality Mode (Best Accuracy)
```bash
# For best quality (5-10 FPS)
python raspberry_milk_detector.py --performance-mode quality --resolution 1280x720 --target-fps 10
```

### Advanced Options

```bash
# Use PiCamera2 (recommended for Pi)
python raspberry_milk_detector.py --use-picamera2

# Change resolution
python raspberry_milk_detector.py --resolution 1280x720

# Adjust confidence threshold
python raspberry_milk_detector.py --confidence 0.6

# Use specific camera device
python raspberry_milk_detector.py --camera 1

# Combine options
python raspberry_milk_detector.py --use-picamera2 --resolution 640x480 --performance-mode speed
```

### Performance Monitoring

Monitor system performance during detection:
```bash
# In another terminal
python performance_monitor.py

# Or monitor with custom interval
python performance_monitor.py --interval 2.0

# View performance summary
python performance_monitor.py --summary
```

### 🧪 Performance Optimization

Run the performance optimizer to find best settings:
```bash
python optimize_pi.py
```

This will:
- Check your Pi's hardware
- Test different configurations
- Recommend optimal settings
- Run performance tests

## 🎮 Controls

During detection:
- **'q'**: Quit detection
- **'s'**: Save current frame with detections
- **'1'**: Process every frame (best quality, lower FPS)
- **'2'**: Process every 2nd frame (2x faster)
- **'3'**: Process every 3rd frame (3x faster)
- **Ctrl+C**: Graceful shutdown

## ⚙️ Configuration

### Model Path
Update the model path in `raspberry_milk_detector.py` if your model is in a different location:
```python
parser.add_argument("--model", default="../model/best_float32.tflite", 
                   help="Path to TFLite model")
```

### Camera Settings
Adjust camera properties in the code:
```python
# Set camera properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
cap.set(cv2.CAP_PROP_FPS, 30)  # Adjust FPS as needed
```

### Performance Tuning
Modify these parameters for better performance:
```python
# Thread count for Pi 4
self.interpreter.set_num_threads(4)

# Confidence and NMS thresholds
confidence_threshold=0.5  # Lower = more detections
nms_threshold=0.4         # Lower = less overlap removal

# Frame skip interval
frame_skip_interval=2     # Process every 2nd frame
```

## 🔧 Troubleshooting

### Camera Not Working
```bash
# Check camera interface
sudo raspi-config nonint do_camera

# Test camera
libcamera-still -o test.jpg

# Check camera permissions
ls -la /dev/video*
```

### Low Performance (0.8 FPS Issue)
If you're getting only 0.8 FPS instead of real-time:

1. **Use Performance Mode**:
   ```bash
   python raspberry_milk_detector.py --performance-mode speed
   ```

2. **Lower Resolution**:
   ```bash
   python raspberry_milk_detector.py --resolution 320x240
   ```

3. **Enable Frame Skipping**:
   - Press '2' during detection to process every 2nd frame
   - Press '3' to process every 3rd frame

4. **Check System Resources**:
   ```bash
   python performance_monitor.py
   ```

5. **Close Background Apps**:
   ```bash
   sudo systemctl stop bluetooth
   sudo systemctl stop avahi-daemon
   ```

6. **Use PiCamera2**:
   ```bash
   python raspberry_milk_detector.py --use-picamera2
   ```

### 🏭 Conveyor Belt Synchronization Issues
If your detection isn't matching conveyor belt speed:

1. **Enable Conveyor Mode**:
   ```bash
   python raspberry_milk_detector.py --conveyor-mode --conveyor-width 0.5
   ```

2. **Use Auto-Speed Detection**:
   - Let the system run for 1-2 minutes to learn conveyor speed
   - System automatically adjusts frame processing to match speed

3. **Manual Speed Setting**:
   ```bash
   python raspberry_milk_detector.py --conveyor-mode --conveyor-speed 1.5
   ```

4. **Calibrate Camera Position**:
   ```bash
   python calibrate_conveyor.py
   ```

5. **Check Detection Coverage**:
   - Ensure camera covers full conveyor width
   - Position camera directly above conveyor center
   - Adjust camera height for optimal coverage

6. **Runtime Controls**:
   - Press 'c' to toggle conveyor mode on/off
   - Press 'v' to manually set conveyor speed
   - Press '1/2/3' to adjust frame processing frequency

7. **Production Line Optimization**:
   ```bash
   # For high-speed production lines
   python raspberry_milk_detector.py --conveyor-mode --performance-mode speed --target-fps 25
   
   # For medium-speed lines
   python raspberry_milk_detector.py --conveyor-mode --performance-mode balanced --target-fps 20
   
   # For low-speed lines
   python raspberry_milk_detector.py --conveyor-mode --performance-mode quality --target-fps 15
   ```

### Memory Issues