#!/usr/bin/env python3
"""
Raspberry Pi Optimization Script for Milk Detection
Tunes system settings for optimal performance
"""

import os
import subprocess
import sys
import argparse

class PiOptimizer:
    def __init__(self):
        self.optimizations = {
            'gpu_mem': '128',
            'over_voltage': '2',
            'arm_freq': '1750',
            'gpu_freq': '600',
            'temp_limit': '70',
            'disable_bluetooth': True,
            'disable_wifi': False,
            'disable_leds': True,
            'enable_4k': False
        }
    
    def check_root(self):
        """Check if running as root"""
        if os.geteuid() != 0:
            print("Error: This script must be run as root (use sudo)")
            return False
        return True
    
    def backup_config(self):
        """Backup current config.txt"""
        if os.path.exists('/boot/config.txt'):
            backup_path = '/boot/config.txt.backup'
            try:
                subprocess.run(['cp', '/boot/config.txt', backup_path], check=True)
                print(f"Config backed up to: {backup_path}")
                return True
            except subprocess.CalledProcessError:
                print("Warning: Could not backup config.txt")
                return False
        return True
    
    def update_config_txt(self):
        """Update /boot/config.txt with optimizations"""
        config_path = '/boot/config.txt'
        
        if not os.path.exists(config_path):
            print("Error: /boot/config.txt not found")
            return False
        
        # Read current config
        try:
            with open(config_path, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading config.txt: {e}")
            return False
        
        # Prepare new config
        new_lines = []
        gpu_mem_set = False
        over_voltage_set = False
        arm_freq_set = False
        gpu_freq_set = False
        temp_limit_set = False
        
        # Process existing lines
        for line in lines:
            line = line.strip()
            if line.startswith('gpu_mem='):
                new_lines.append(f'gpu_mem={self.optimizations["gpu_mem"]}\n')
                gpu_mem_set = True
            elif line.startswith('over_voltage='):
                new_lines.append(f'over_voltage={self.optimizations["over_voltage"]}\n')
                over_voltage_set = True
            elif line.startswith('arm_freq='):
                new_lines.append(f'arm_freq={self.optimizations["arm_freq"]}\n')
                arm_freq_set = True
            elif line.startswith('gpu_freq='):
                new_lines.append(f'gpu_freq={self.optimizations["gpu_freq"]}\n')
                gpu_freq_set = True
            elif line.startswith('temp_limit='):
                new_lines.append(f'temp_limit={self.optimizations["temp_limit"]}\n')
            elif line.startswith('#') or line == '':
                new_lines.append(line + '\n')
            else:
                new_lines.append(line + '\n')
        
        # Add missing optimizations
        if not gpu_mem_set:
            new_lines.append(f'gpu_mem={self.optimizations["gpu_mem"]}\n')
        if not over_voltage_set:
            new_lines.append(f'over_voltage={self.optimizations["over_voltage"]}\n')
        if not arm_freq_set:
            new_lines.append(f'arm_freq={self.optimizations["arm_freq"]}\n')
        if not gpu_freq_set:
            new_lines.append(f'gpu_freq={self.optimizations["gpu_freq"]}\n')
        if not temp_limit_set:
            new_lines.append(f'temp_limit={self.optimizations["temp_limit"]}\n')
        
        # Add performance optimizations
        new_lines.extend([
            '# Milk Detection Optimizations\n',
            'dtoverlay=disable-bt\n' if self.optimizations['disable_bluetooth'] else '',
            'dtoverlay=disable-wifi\n' if self.optimizations['disable_wifi'] else '',
            'dtparam=act_led_trigger=none\n' if self.optimizations['disable_leds'] else '',
            'dtparam=act_led_activelow=off\n' if self.optimizations['disable_leds'] else '',
            'dtparam=pwr_led_trigger=none\n' if self.optimizations['disable_leds'] else '',
            'dtparam=pwr_led_activelow=off\n' if self.optimizations['disable_leds'] else '',
            'hdmi_enable_4kp60=1\n' if self.optimizations['enable_4k'] else '',
            'force_turbo=1\n',
            'avoid_warnings=1\n'
        ])
        
        # Write new config
        try:
            with open(config_path, 'w') as f:
                f.writelines(new_lines)
            print("Config.txt updated successfully")
            return True
        except Exception as e:
            print(f"Error writing config.txt: {e}")
            return False
    
    def optimize_systemd(self):
        """Optimize systemd services"""
        services_to_disable = [
            'bluetooth',
            'avahi-daemon',
            'triggerhappy',
            'hciuart'
        ]
        
        if self.optimizations['disable_bluetooth']:
            for service in services_to_disable:
                try:
                    subprocess.run(['systemctl', 'disable', service], check=True)
                    subprocess.run(['systemctl', 'stop', service], check=True)
                    print(f"Disabled and stopped: {service}")
                except subprocess.CalledProcessError:
                    print(f"Warning: Could not disable {service}")
    
    def optimize_swap(self):
        """Optimize swap settings"""
        try:
            # Increase swap size
            swapfile_path = '/etc/dphys-swapfile'
            if os.path.exists(swapfile_path):
                with open(swapfile_path, 'r') as f:
                    content = f.read()
                
                # Update swap size to 1GB
                content = content.replace('CONF_SWAPSIZE=100', 'CONF_SWAPSIZE=1024')
                
                with open(swapfile_path, 'w') as f:
                    f.write(content)
                
                # Restart swap
                subprocess.run(['dphys-swapfile', 'swapoff'], check=True)
                subprocess.run(['dphys-swapfile', 'setup'], check=True)
                subprocess.run(['dphys-swapfile', 'swapon'], check=True)
                
                print("Swap optimized to 1GB")
        except Exception as e:
            print(f"Warning: Could not optimize swap: {e}")
    
    def optimize_network(self):
        """Optimize network settings"""
        try:
            # Optimize TCP settings
            tcp_settings = {
                'net.core.rmem_max': '134217728',
                'net.core.wmem_max': '134217728',
                'net.ipv4.tcp_rmem': '4096 87380 134217728',
                'net.ipv4.tcp_wmem': '4096 65536 134217728',
                'net.ipv4.tcp_congestion_control': 'bbr'
            }
            
            for param, value in tcp_settings.items():
                subprocess.run(['sysctl', '-w', f'{param}={value}'], check=True)
            
            print("Network settings optimized")
        except Exception as e:
            print(f"Warning: Could not optimize network: {e}")
    
    def create_performance_script(self):
        """Create performance monitoring script"""
        script_content = '''#!/bin/bash
# Performance monitoring script
echo "Raspberry Pi Performance Status:"
echo "================================="
echo "CPU Temperature: $(vcgencmd measure_temp)"
echo "CPU Frequency: $(vcgencmd measure_clock arm)"
echo "GPU Frequency: $(vcgencmd measure_clock core)"
echo "Memory: $(free -h | grep Mem | awk '{print $3"/"$2}')"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
'''
        
        script_path = '/usr/local/bin/pi-status'
        try:
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            print(f"Performance script created: {script_path}")
        except Exception as e:
            print(f"Warning: Could not create performance script: {e}")
    
    def print_optimizations(self):
        """Print current optimization settings"""
        print("\nCurrent Optimization Settings:")
        print("==============================")
        for key, value in self.optimizations.items():
            print(f"{key}: {value}")
    
    def apply_optimizations(self):
        """Apply all optimizations"""
        if not self.check_root():
            return False
        
        print("Applying Raspberry Pi optimizations for milk detection...")
        
        # Backup current config
        if not self.backup_config():
            return False
        
        # Update config.txt
        if not self.update_config_txt():
            return False
        
        # Optimize systemd services
        self.optimize_systemd()
        
        # Optimize swap
        self.optimize_swap()
        
        # Optimize network
        self.optimize_network()
        
        # Create performance script
        self.create_performance_script()
        
        print("\nOptimizations applied successfully!")
        print("A reboot is required for changes to take effect.")
        print("\nTo reboot: sudo reboot")
        
        return True
    
    def restore_backup(self):
        """Restore config from backup"""
        backup_path = '/boot/config.txt.backup'
        if os.path.exists(backup_path):
            try:
                subprocess.run(['cp', backup_path, '/boot/config.txt'], check=True)
                print("Config restored from backup")
                return True
            except subprocess.CalledProcessError:
                print("Error: Could not restore config")
                return False
        else:
            print("No backup found")
            return False

def main():
    parser = argparse.ArgumentParser(description="Raspberry Pi Optimizer for Milk Detection")
    parser.add_argument("--apply", action="store_true", help="Apply optimizations")
    parser.add_argument("--restore", action="store_true", help="Restore from backup")
    parser.add_argument("--show", action="store_true", help="Show current settings")
    
    args = parser.parse_args()
    
    optimizer = PiOptimizer()
    
    if args.show:
        optimizer.print_optimizations()
    elif args.restore:
        optimizer.restore_backup()
    elif args.apply:
        optimizer.apply_optimizations()
    else:
        print("Raspberry Pi Optimizer for Milk Detection")
        print("==========================================")
        print("Use --apply to apply optimizations")
        print("Use --restore to restore from backup")
        print("Use --show to show current settings")
        print("\nNote: This script must be run as root (use sudo)")

if __name__ == "__main__":
    main() 