# Raspberry Pi 4 Milk Detection Deployment

This folder contains everything you need to deploy the milk detection system on a Raspberry Pi 4 with real-time camera input.

## 🍓 Features

- **Real-time Detection**: Live camera feed with instant milk packet detection
- **Optimized for Pi**: Uses tflite-runtime and optimized OpenCV for ARM architecture
- **Performance Monitoring**: Track CPU, memory, temperature, and FPS
- **Flexible Camera Support**: Works with both PiCamera2 and USB cameras
- **Auto-start Service**: Optional systemd service for boot-time startup
- **Frame Saving**: Save detected frames with timestamps

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

### Basic Detection

Start the milk detector with default settings:
```bash
cd raspberry
source venv_pi/bin/activate
python raspberry_milk_detector.py
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
python raspberry_milk_detector.py --use-picamera2 --resolution 1280x720 --confidence 0.7
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

## 🎮 Controls

During detection:
- **'q'**: Quit detection
- **'s'**: Save current frame with detections
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

### Low Performance
```bash
# Check CPU temperature
vcgencmd measure_temp

# Monitor performance
python performance_monitor.py

# Reduce resolution
python raspberry_milk_detector.py --resolution 320x240

# Increase confidence threshold
python raspberry_milk_detector.py --confidence 0.7
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

### For Better FPS
1. **Lower Resolution**: Use 640x480 or 320x240
2. **Higher Confidence**: Set confidence threshold to 0.7+
3. **Close Background Apps**: Stop unnecessary services
4. **Use PiCamera2**: Better performance than USB cameras
5. **Optimize Model**: Consider model quantization

### For Better Accuracy
1. **Good Lighting**: Ensure consistent illumination
2. **Camera Position**: Mount camera directly above detection area
3. **Stable Mount**: Minimize camera movement
4. **Clean Lens**: Keep camera lens clean
5. **Optimal Distance**: Position camera at recommended height

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
├── raspberry_milk_detector.py    # Main detection script
├── performance_monitor.py         # Performance monitoring
├── setup_pi.sh                   # Setup script
├── requirements_pi.txt           # Pi-optimized dependencies
├── README_PI.md                  # This file
├── saved_frames/                 # Saved detection frames
└── logs/                         # Performance logs
```

## 🔄 Updates

To update the system:
```bash
cd raspberry
git pull origin main
./setup_pi.sh
```

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Monitor performance with `performance_monitor.py`
3. Check system logs: `sudo journalctl -u milk-detector.service`
4. Verify camera setup: `sudo raspi-config`

## 📈 Expected Performance

On Raspberry Pi 4 (4GB):
- **640x480 resolution**: 15-25 FPS
- **1280x720 resolution**: 8-15 FPS
- **CPU usage**: 60-80%
- **Memory usage**: 200-400 MB
- **Temperature**: 45-65°C (with proper cooling)

## 🎯 Use Cases

- **Production Line Monitoring**: Real-time milk packet counting
- **Quality Control**: Detection of missing or damaged packets
- **Inventory Management**: Automated stock counting
- **Research & Development**: Data collection for model improvement
- **Educational**: Computer vision and ML learning platform 