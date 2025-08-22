#!/usr/bin/env python3
"""
Performance Monitor for Raspberry Pi Milk Detection
Monitors CPU, memory, temperature, and FPS during detection
"""

import psutil
import time
import threading
import csv
from pathlib import Path
import argparse
import signal
import sys

class PerformanceMonitor:
    def __init__(self, log_file="performance_log.csv", monitor_interval=1.0):
        """
        Initialize performance monitor
        
        Args:
            log_file: CSV file to save performance data
            monitor_interval: Monitoring interval in seconds
        """
        self.log_file = Path(log_file)
        self.monitor_interval = monitor_interval
        self.running = False
        self.monitoring_thread = None
        
        # Performance metrics
        self.cpu_percent = 0
        self.memory_percent = 0
        self.memory_used = 0
        self.temperature = 0
        self.fps = 0
        self.detection_count = 0
        
        # Create log file with headers
        self.setup_log_file()
        
    def setup_log_file(self):
        """Create CSV log file with headers"""
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'timestamp', 'cpu_percent', 'memory_percent', 
                    'memory_used_mb', 'temperature_c', 'fps', 
                    'detection_count'
                ])
    
    def get_temperature(self):
        """Get Raspberry Pi CPU temperature"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
            return temp
        except:
            return 0.0
    
    def update_metrics(self):
        """Update performance metrics"""
        self.cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        self.memory_percent = memory.percent
        self.memory_used = memory.used / (1024 * 1024)  # MB
        self.temperature = self.get_temperature()
    
    def log_metrics(self):
        """Log current metrics to CSV file"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.log_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                timestamp, self.cpu_percent, self.memory_percent,
                round(self.memory_used, 2), round(self.temperature, 2),
                round(self.fps, 2), self.detection_count
            ])
    
    def print_metrics(self):
        """Print current metrics to console"""
        print(f"\rCPU: {self.cpu_percent:5.1f}% | "
              f"Memory: {self.memory_percent:5.1f}% ({self.memory_used:6.1f}MB) | "
              f"Temp: {self.temperature:5.1f}°C | "
              f"FPS: {self.fps:5.1f} | "
              f"Detections: {self.detection_count:3d}", end='', flush=True)
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self.update_metrics()
                self.log_metrics()
                self.print_metrics()
                time.sleep(self.monitor_interval)
            except Exception as e:
                print(f"\nError in monitoring: {e}")
                break
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitoring_thread = threading.Thread(target=self.monitor_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        print("Performance monitoring started...")
        print("Press Ctrl+C to stop monitoring")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        
        print("\nPerformance monitoring stopped")
        print(f"Log file saved to: {self.log_file}")
    
    def set_fps(self, fps):
        """Update FPS value (called from detection script)"""
        self.fps = fps
    
    def set_detection_count(self, count):
        """Update detection count (called from detection script)"""
        self.detection_count = count
    
    def get_summary(self):
        """Get performance summary"""
        if not self.log_file.exists():
            return "No performance data available"
        
        try:
            with open(self.log_file, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
            
            if not rows:
                return "No performance data available"
            
            # Calculate averages
            cpu_values = [float(row['cpu_percent']) for row in rows]
            memory_values = [float(row['memory_percent']) for row in rows]
            temp_values = [float(row['temperature_c']) for row in rows]
            fps_values = [float(row['fps']) for row in rows if float(row['fps']) > 0]
            
            summary = f"""
Performance Summary:
==================
Total samples: {len(rows)}
Monitoring duration: {len(rows) * self.monitor_interval:.1f} seconds

CPU Usage:
  Average: {sum(cpu_values)/len(cpu_values):.1f}%
  Max: {max(cpu_values):.1f}%
  Min: {min(cpu_values):.1f}%

Memory Usage:
  Average: {sum(memory_values)/len(memory_values):.1f}%
  Max: {max(memory_values):.1f}%
  Min: {min(memory_values):.1f}%

Temperature:
  Average: {sum(temp_values)/len(temp_values):.1f}°C
  Max: {max(temp_values):.1f}°C
  Min: {min(temp_values):.1f}°C

FPS (when > 0):
  Average: {sum(fps_values)/len(fps_values):.1f} FPS
  Max: {max(fps_values):.1f} FPS
  Min: {min(fps_values):.1f} FPS

Log file: {self.log_file}
"""
            return summary
            
        except Exception as e:
            return f"Error reading performance data: {e}"

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down gracefully...")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Raspberry Pi Performance Monitor")
    parser.add_argument("--log-file", default="performance_log.csv",
                       help="CSV file to save performance data")
    parser.add_argument("--interval", type=float, default=1.0,
                       help="Monitoring interval in seconds (default: 1.0)")
    parser.add_argument("--summary", action="store_true",
                       help="Show performance summary and exit")
    
    args = parser.parse_args()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create monitor
    monitor = PerformanceMonitor(args.log_file, args.interval)
    
    if args.summary:
        print(monitor.get_summary())
        return
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
        # Keep main thread alive
        while monitor.running:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        monitor.stop_monitoring()
        print(monitor.get_summary())

if __name__ == "__main__":
    main() 