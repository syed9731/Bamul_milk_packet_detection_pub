#!/bin/bash

# Startup script for Raspberry Pi Milk Detection
# This script activates the virtual environment and starts detection

echo "Starting Raspberry Pi Milk Detection..."

# Check if we're in the right directory
if [ ! -f "raspberry_milk_detector.py" ]; then
    echo "Error: Please run this script from the raspberry directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv_pi" ]; then
    echo "Error: Virtual environment not found. Please run setup_pi.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv_pi/bin/activate

# Check if model exists
if [ ! -f "../model/best_float32.tflite" ]; then
    echo "Warning: Model file not found at ../model/best_float32.tflite"
    echo "Please ensure the model file is in the correct location"
fi

# Start detection with default settings
echo "Starting milk detection..."
echo "Press 'q' to quit, 's' to save frame"
echo ""

python raspberry_milk_detector.py "$@" 