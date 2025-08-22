#!/bin/bash
# Conveyor Belt Milk Detection Startup Script
# Automatically synchronizes with production line speed

echo "🏭 Starting Conveyor Belt Milk Detection System..."
echo "=================================================="

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
echo "🏭 Starting conveyor belt detection mode..."
echo ""

# Get conveyor belt parameters
echo "📏 Conveyor Belt Configuration:"
read -p "Enter conveyor belt width in meters (default: 0.5): " conveyor_width
conveyor_width=${conveyor_width:-0.5}

echo ""
echo "🚀 Speed Configuration:"
echo "1. Auto-detect speed from object movement (recommended)"
echo "2. Manual speed setting"
read -p "Choose option (1 or 2): " speed_option

if [ "$speed_option" = "2" ]; then
    read -p "Enter conveyor speed in m/s: " conveyor_speed
    speed_arg="--conveyor-speed $conveyor_speed"
else
    speed_arg=""
    echo "Auto-detection enabled - system will learn conveyor speed from object movement"
fi

echo ""
echo "⚙️  Performance Configuration:"
echo "1. Speed mode (best FPS, lower accuracy)"
echo "2. Balanced mode (good balance)"
echo "3. Quality mode (best accuracy, lower FPS)"
read -p "Choose performance mode (1, 2, or 3): " perf_mode

case $perf_mode in
    1) perf_arg="--performance-mode speed --resolution 320x240" ;;
    2) perf_arg="--performance-mode balanced --resolution 640x480" ;;
    3) perf_arg="--performance-mode quality --resolution 640x480" ;;
    *) perf_arg="--performance-mode balanced --resolution 640x480" ;;
esac

echo ""
echo "🎯 Starting detection with conveyor synchronization..."
echo "Conveyor width: ${conveyor_width}m"
echo "Performance mode: $perf_arg"
echo "Speed detection: $([ -z "$speed_arg" ] && echo "Auto" || echo "Manual")"
echo ""

# Start detection with conveyor belt mode
python3 raspberry_milk_detector.py \
    --use-picamera2 \
    --conveyor-mode \
    --conveyor-width $conveyor_width \
    $speed_arg \
    $perf_arg \
    --target-fps 20

echo ""
echo "✅ Conveyor detection stopped"
echo ""
echo "💡 Conveyor Belt Tips:"
echo "• Press 'c' to toggle conveyor mode on/off"
echo "• Press 'v' to manually set conveyor speed"
echo "• Press '1/2/3' to adjust frame processing frequency"
echo "• System automatically adjusts to match conveyor speed"
echo ""
echo "🔧 Calibration:"
echo "• Position camera directly above conveyor center"
echo "• Ensure consistent lighting"
echo "• Adjust conveyor-width parameter if needed"
echo "• Let system run for 1-2 minutes to auto-calibrate speed" 