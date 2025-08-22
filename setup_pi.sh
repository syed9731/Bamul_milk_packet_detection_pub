#!/bin/bash

# Raspberry Pi 4 Setup Script for Milk Detection
# This script sets up the environment for running milk detection on Pi

echo "Setting up Raspberry Pi 4 for Milk Packets Detection..."

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-opencv \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libjasper-dev \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    gfortran \
    libhdf5-103 \
    python3-dev \
    libopencv-dev

# Enable camera interface
echo "Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# # Enable I2C interface (if needed for sensors)
# echo "Enabling I2C interface..."
# sudo raspi-config nonint do_i2c 0

# # Enable SPI interface (if needed for sensors)
# echo "Enabling SPI interface..."
# sudo raspi-config nonint do_spi 0

# Create Python virtual environment
echo "Creating Python virtual environment..."
# Try to use Python 3.11 if available, fallback to python3
if command -v python3.11 &> /dev/null; then
    echo "Using Python 3.11 for virtual environment..."
    python3.11 -m venv venv_pi
else
    echo "Python 3.11 not found, using default python3..."
    python3 -m venv venv_pi
fi
source venv_pi/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements_pi.txt

# Install tflite-runtime specifically for Pi
echo "Installing TensorFlow Lite Runtime for Pi..."
echo "Detecting architecture and Python version..."

# Detect architecture
ARCH=$(uname -m)
PYTHON_VERSION=$(python3.11 --version 2>/dev/null | grep -o '3\.11' || echo "3.10")

echo "Architecture: $ARCH, Python: $PYTHON_VERSION"

# Try different TFLite runtime versions for compatibility
if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    echo "64-bit ARM detected, trying 64-bit packages..."
    python3.11 -m pip install tflite-runtime || \
    python3.11 -m pip install https://github.com/google-coral/pycoral/releases/download/v2.0.0/tflite_runtime-2.5.0.post1-cp311-cp311-linux_aarch64.whl || \
    python3.11 -m pip install https://github.com/google-coral/pycoral/releases/download/v2.0.0/tflite_runtime-2.5.0.post1-cp310-cp310-linux_aarch64.whl || \
    echo "Warning: Could not install 64-bit tflite-runtime"
elif [ "$ARCH" = "armv7l" ] || [ "$ARCH" = "armv6l" ]; then
    echo "32-bit ARM detected, trying 32-bit packages..."
    python3.11 -m pip install tflite-runtime || \
    python3.11 -m pip install https://github.com/google-coral/pycoral/releases/download/v2.0.0/tflite_runtime-2.5.0.post1-cp311-cp311-linux_armv7l.whl || \
    python3.11 -m pip install https://github.com/google-coral/pycoral/releases/download/v2.0.0/tflite_runtime-2.5.0.post1-cp310-cp310-linux_armv7l.whl || \
    echo "Warning: Could not install 32-bit tflite-runtime"
else
    echo "Unknown architecture: $ARCH, trying generic packages..."
    python3.11 -m pip install tflite-runtime || \
    echo "Warning: Could not install tflite-runtime"
fi

# Fallback to regular pip if python3.11 -m pip fails
if ! python3.11 -c "import tflite_runtime" 2>/dev/null; then
    echo "Trying fallback installation methods..."
    pip install tflite-runtime || \
    pip install https://github.com/google-coral/pycoral/releases/download/v2.0.0/tflite_runtime-2.5.0.post1-cp39-cp39-linux_armv7l.whl || \
    pip install https://github.com/google-coral/pycoral/releases/download/v2.0.0/tflite_runtime-2.5.0.post1-cp310-cp310-linux_armv7l.whl || \
    echo "Warning: Could not install tflite-runtime, will use tensorflow fallback"
fi

# Install tensorflow as fallback if tflite-runtime fails
echo "Installing TensorFlow as fallback..."
pip install tensorflow

# Create necessary directories
echo "Creating directories..."
mkdir -p saved_frames
mkdir -p logs

# Set permissions
echo "Setting permissions..."
chmod +x raspberry_milk_detector.py
chmod +x requirements_pi.txt

# Create systemd service file for auto-start (optional)
echo "Creating systemd service file..."
sudo tee /etc/systemd/system/milk-detector.service > /dev/null <<EOF
[Unit]
Description=Milk Detection Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv_pi/bin
ExecStart=$(pwd)/venv_pi/bin/python $(pwd)/raspberry_milk_detector.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable service (optional - uncomment if you want auto-start)
# sudo systemctl enable milk-detector.service

echo "Setup complete!"
echo ""
echo "To start detection:"
echo "1. Activate virtual environment: source venv_pi/bin/activate"
echo "2. Run detector: python raspberry_milk_detector.py"
echo ""
echo "Optional commands:"
echo "- Start with PiCamera2: python raspberry_milk_detector.py --use-picamera2"
echo "- Change resolution: python raspberry_milk_detector.py --resolution 1280x720"
echo "- Adjust confidence: python raspberry_milk_detector.py --confidence 0.6"
echo ""
echo "To enable auto-start on boot:"
echo "sudo systemctl enable milk-detector.service"
echo "sudo systemctl start milk-detector.service" 