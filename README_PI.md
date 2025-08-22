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

### Memory Issues
```bash
# Check memory usage
free -h

# Close unnecessary applications
sudo systemctl stop bluetooth
sudo systemctl stop avahi-daemon

# Increase swap if needed
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Model Loading Issues
```bash
# Check model file
ls -la ../model/

# Verify TFLite runtime
python -c "import tflite_runtime; print('OK')"

# Reinstall TFLite runtime
pip uninstall tflite-runtime
pip install https://github.com/google-coral/pycoral/releases/download/v2.0.0/tflite_runtime-2.5.0.post1-cp39-cp39-linux_armv7l.whl
```

## 📊 Performance Tips

### For Better FPS (Real-time Performance)
1. **Use Speed Mode**: `--performance-mode speed`
2. **Lower Resolution**: Use 320x240 or 640x480
3. **Frame Skipping**: Press '2' or '3' during detection
4. **Higher Confidence**: Set confidence threshold to 0.6+
5. **Use PiCamera2**: Better performance than USB cameras
6. **Close Background Apps**: Stop unnecessary services
7. **Reduce Display Updates**: Display updates every 2nd frame

### For Better Accuracy
1. **Good Lighting**: Ensure consistent illumination
2. **Camera Position**: Mount camera directly above detection area
3. **Stable Mount**: Minimize camera movement
4. **Clean Lens**: Keep camera lens clean
5. **Optimal Distance**: Position camera at recommended height

### Performance Modes Explained
- **Speed Mode**: Processes every 3rd frame, optimized for 10+ FPS
- **Balanced Mode**: Processes every 2nd frame, optimized for 10-15 FPS  
- **Quality Mode**: Processes every frame, optimized for 5-10 FPS

## 🚀 Auto-start Service

Enable the milk detector to start automatically on boot:
```bash
# Enable service
sudo systemctl enable milk-detector.service

# Start service
sudo systemctl start milk-detector.service

# Check status
sudo systemctl status milk-detector.service

# View logs
sudo journalctl -u milk-detector.service -f
```

## 📁 File Structure

```
raspberry/
├── raspberry_milk_detector.py    # Main detection script (OPTIMIZED)
├── performance_monitor.py         # Performance monitoring
├── optimize_pi.py                # Performance optimizer
├── start_detection.sh            # Optimized startup script
├── setup_pi.sh                   # Setup script
├── requirements_pi.txt           # Pi-optimized dependencies
├── README_PI.md                  # This file
├── saved_frames/                 # Saved detection frames
└── logs/                         # Performance logs
```

## 🎯 Quick Performance Commands

### Get Real-time Performance (15+ FPS)
```bash
./start_detection.sh
```

### Maximum Speed (20+ FPS)
```bash
python raspberry_milk_detector.py --performance-mode speed --resolution 320x240 --target-fps 20
```

### Monitor Performance
```bash
python performance_monitor.py
```

### Optimize Settings
```bash
python optimize_pi.py
```

## 🆘 Still Getting Low FPS?

If you're still experiencing low performance:

1. **Run the optimizer**: `python optimize_pi.py`
2. **Check system resources**: `python performance_monitor.py --summary`
3. **Use speed mode**: `--performance-mode speed`
4. **Lower resolution**: `--resolution 320x240`
5. **Enable frame skipping**: Press '2' or '3' during detection
6. **Check temperature**: Ensure Pi is not throttling due to heat
7. **Close background apps**: Stop unnecessary services
8. **Use PiCamera2**: Better than USB cameras

The optimizations should get you from 0.8 FPS to 15+ FPS for real-time performance! 