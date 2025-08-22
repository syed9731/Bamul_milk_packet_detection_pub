#!/usr/bin/env python3
"""
Performance Monitor for Raspberry Pi Milk Detection
Monitors CPU, memory, temperature, and FPS in real-time
"""

import psutil
import time
import subprocess
import os
import signal
import sys
from datetime import datetime

class PerformanceMonitor:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.running = False
        self.start_time = time.time()
        self.fps_samples = []
        
    def get_cpu_temp(self):
        """Get CPU temperature"""
        try:
            temp = subprocess.check_output(['vcgencmd', 'measure_temp']).decode()
            return float(temp.replace('temp=', '').replace("'C", ''))
        except:
            return None
    
    def get_cpu_freq(self):
        """Get CPU frequency"""
        try:
            freq = subprocess.check_output(['vcgencmd', 'measure_clock', 'arm']).decode()
            return int(freq.split('=')[1]) / 1000000  # Convert to MHz
        except:
            return None
    
    def get_gpu_freq(self):
        """Get GPU frequency"""
        try:
            freq = subprocess.check_output(['vcgencmd', 'measure_clock', 'core']).decode()
            return int(freq.split('=')[1]) / 1000000  # Convert to MHz
        except:
            return None
    
    def get_memory_info(self):
        """Get memory information"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total / (1024**3),  # GB
            'used': memory.used / (1024**3),    # GB
            'percent': memory.percent
        }
    
    def get_cpu_info(self):
        """Get CPU information"""
        return {
            'percent': psutil.cpu_percent(interval=0.1),
            'count': psutil.cpu_count(),
            'freq': psutil.cpu_freq().current / 1000 if psutil.cpu_freq() else None  # GHz
        }
    
    def get_disk_info(self):
        """Get disk information"""
        disk = psutil.disk_usage('/')
        return {
            'total': disk.total / (1024**3),  # GB
            'used': disk.used / (1024**3),    # GB
            'percent': (disk.used / disk.total) * 100
        }
    
    def print_header(self):
        """Print monitoring header"""
        os.system('clear')
        print("🍓 Raspberry Pi Performance Monitor")
        print("=" * 50)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Interval: {self.interval}s | Press Ctrl+C to stop")
        print("-" * 50)
    
    def print_stats(self):
        """Print current statistics"""
        # Get system info
        cpu_info = self.get_cpu_info()
        memory_info = self.get_memory_info()
        disk_info = self.get_disk_info()
        cpu_temp = self.get_cpu_temp()
        cpu_freq = self.get_cpu_freq()
        gpu_freq = self.get_gpu_freq()
        
        # Calculate uptime
        uptime = time.time() - self.start_time
        
        # Print statistics
        print(f"\n⏱️  Uptime: {uptime:.0f}s")
        
        print(f"\n🖥️  CPU:")
        print(f"   Usage: {cpu_info['percent']:5.1f}%")
        print(f"   Cores: {cpu_info['count']}")
        if cpu_freq:
            print(f"   Freq:  {cpu_freq:5.0f} MHz")
        if cpu_temp:
            print(f"   Temp:  {cpu_temp:5.1f}°C")
        
        print(f"\n💾 Memory:")
        print(f"   Used:  {memory_info['used']:5.1f} GB / {memory_info['total']:5.1f} GB")
        print(f"   Usage: {memory_info['percent']:5.1f}%")
        
        print(f"\n💿 Disk:")
        print(f"   Used:  {disk_info['used']:5.1f} GB / {disk_info['total']:5.1f} GB")
        print(f"   Usage: {disk_info['percent']:5.1f}%")
        
        if gpu_freq:
            print(f"\n🎮 GPU:")
            print(f"   Freq:  {gpu_freq:5.0f} MHz")
        
        # Performance warnings
        warnings = []
        if cpu_temp and cpu_temp > 70:
            warnings.append(f"⚠️  CPU temperature high: {cpu_temp:.1f}°C")
        if memory_info['percent'] > 90:
            warnings.append(f"⚠️  Memory usage high: {memory_info['percent']:.1f}%")
        if cpu_info['percent'] > 90:
            warnings.append(f"⚠️  CPU usage high: {cpu_info['percent']:.1f}%")
        
        if warnings:
            print(f"\n🚨 Warnings:")
            for warning in warnings:
                print(f"   {warning}")
        
        # Performance tips
        print(f"\n💡 Tips:")
        if cpu_temp and cpu_temp > 60:
            print("   • Consider improving cooling")
        if memory_info['percent'] > 80:
            print("   • Close unnecessary applications")
        if cpu_info['percent'] > 80:
            print("   • Reduce detection resolution or FPS")
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.running = True
        self.print_header()
        
        try:
            while self.running:
                self.print_stats()
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user")
            self.running = False
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.running = False

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down performance monitor...")
    sys.exit(0)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Raspberry Pi Performance Monitor")
    parser.add_argument("--interval", type=float, default=2.0,
                       help="Update interval in seconds (default: 2.0)")
    parser.add_argument("--summary", action="store_true",
                       help="Show one-time summary instead of continuous monitoring")
    
    args = parser.parse_args()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create monitor
    monitor = PerformanceMonitor(args.interval)
    
    if args.summary:
        # Show one-time summary
        monitor.print_header()
        monitor.print_stats()
        print("\n📊 Summary complete")
    else:
        # Start continuous monitoring
        monitor.start_monitoring()

if __name__ == "__main__":
    main() 