#!/bin/bash
# 60 FPS High-Performance Milk Detection Startup Script
# Optimized for maximum frame rate on Raspberry Pi 4

echo "🚀 Starting 60 FPS High-Performance Milk Detection"
echo "=================================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is optimized for Raspberry Pi 4"
fi

# Performance optimizations for 60 FPS
echo "🔧 Applying 60 FPS optimizations..."

# Set CPU governor to performance for maximum speed
if command -v cpufreq-set &> /dev/null; then
    echo "Setting CPU governor to performance mode..."
    sudo cpufreq-set -g performance
fi

# Increase GPU memory split if needed
if [ -f /boot/config.txt ]; then
    echo "Checking GPU memory configuration..."
    if ! grep -q "gpu_mem=128" /boot/config.txt; then
        echo "⚠️  Consider adding 'gpu_mem=128' to /boot/config.txt for better GPU performance"
    fi
fi

# Check available memory
echo "Checking system resources..."
free -h
echo "CPU cores: $(nproc)"

# Start detection with 60 FPS optimizations
echo "🎯 Starting detection with 60 FPS target..."
python3 raspberry_milk_detector.py \
    --target-fps 60 \
    --performance-mode speed \
    --use-picamera2 \
    --resolution 640x480 \
    --confidence 0.4 \
    --nms 0.3 \
    --low-latency

echo "✅ 60 FPS detection started!"
echo ""
echo "📊 Performance Tips:"
echo "• Use PiCamera2 for best performance"
echo "• Lower resolution = higher FPS"
echo "• Press '1' to process every frame"
echo "• Press 'l' to enable low-latency mode"
echo "• Press 'q' to quit"
echo ""
echo "🔍 Monitor performance with:"
echo "  watch -n 1 'ps aux | grep python'" 