#!/bin/bash
# Raspberry Pi Milk Detection Startup Script
# Optimized for real-time performance

echo "🍓 Starting Raspberry Pi Milk Detection System..."
echo "================================================"

# Check if we're in the right directory
if [ ! -f "raspberry_milk_detector.py" ]; then
    echo "❌ Error: raspberry_milk_detector.py not found in current directory"
    echo "Please run this script from the raspberry folder"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv_pi" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   ./setup_pi.sh"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv_pi/bin/activate

# Check system performance
echo "📊 Checking system performance..."
python3 performance_monitor.py --summary

echo ""
echo "🚀 Starting detection with optimized settings..."
echo ""

# Start detection with speed-optimized settings
python3 raspberry_milk_detector.py \
    --use-picamera2 \
    --resolution 640x480 \
    --target-fps 15 \
    --performance-mode speed \
    --confidence 0.6

echo ""
echo "✅ Detection stopped"
echo "💡 For better performance, try:"
echo "   • Lower resolution: --resolution 320x240"
echo "   • Speed mode: --performance-mode speed"
echo "   • Higher confidence: --confidence 0.7" 