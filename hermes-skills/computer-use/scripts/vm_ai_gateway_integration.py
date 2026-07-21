#!/usr/bin/env python3
"""
VM AI Gateway Integration for Enhanced Computer Use
Provides real-time contextual awareness by querying the Lilith Gateway
"""

import json
import requests
import time
from datetime import datetime, timedelta

class VMAIGatewayIntegration:
    """Integration with VM AI Gateway for real-time system metrics."""
    
    def __init__(self, gateway_url="http://localhost:8080"):
        self.gateway_url = gateway_url
        self.last_update = None
        self.cached_data = {}
        self.cache_duration = 30  # Cache for 30 seconds
        
    def get_system_status(self):
        """Get current system status from the gateway."""
        # Check if we have fresh cached data
        if (self.last_update and 
            datetime.now() - self.last_update < timedelta(seconds=self.cache_duration)):
            return self.cached_data
            
        try:
            response = requests.get(f"{self.gateway_url}/api/status", timeout=5)
            if response.status_code == 200:
                self.cached_data = response.json()
                self.last_update = datetime.now()
                return self.cached_data
            else:
                print(f"Gateway returned status {response.status_code}")
                return self._get_fallback_data()
        except Exception as e:
            print(f"Failed to connect to gateway: {e}")
            return self._get_fallback_data()
    
    def _get_fallback_data(self):
        """Provide fallback data when gateway is unavailable."""
        return {
            "system_status": "Offline",
            "cpu_load": "0.0 / 0.0 / 0.0",
            "memory_used": "0MB / 0MB",
            "disk_free": "0B",
            "uptime": "Unknown",
            "agents_online": 0,
            "agents_defined": 0,
            "repositories": [],
            "timestamp": datetime.now().isoformat(),
            "gateway_version": "unknown",
            "vms_available": False
        }
    
    def get_resource_pressure(self):
        """Get current resource usage to determine if system is under pressure."""
        status = self.get_system_status()
        
        # Parse CPU load (format: "1.2 / 0.8 / 0.5")
        cpu_load_str = status.get("cpu_load", "0.0 / 0.0 / 0.0")
        try:
            cpu_parts = [float(x.strip()) for x in cpu_load_str.split("/")]
            current_cpu_load = cpu_parts[0] if len(cpu_parts) > 0 else 0.0
        except:
            current_cpu_load = 0.0
            
        # Parse memory usage (format: "22200MB / 63640MB")
        memory_str = status.get("memory_used", "0MB / 0MB")
        try:
            mem_parts = memory_str.replace("MB", "").split("/")
            used_mb = float(mem_parts[0].strip()) if len(mem_parts) > 0 else 0
            total_mb = float(mem_parts[1].strip()) if len(mem_parts) > 1 else 1
            memory_usage_ratio = used_mb / max(total_mb, 1)
        except:
            memory_usage_ratio = 0.0
            
        # Determine pressure levels
        cpu_pressure = min(current_cpu_load / 2.0, 1.0)  # Normalize to 0-1 (assuming 2.0 is high load)
        memory_pressure = memory_usage_ratio
        memory_pressure = min(memory_usage_ratio, 1.0)
        
        return {
            "cpu_pressure": cpu_pressure,
            "memory_pressure": memory_pressure,
            "overall_pressure": max(cpu_pressure, memory_pressure),
            "cpu_load": current_cpu_load,
            "memory_usage_ratio": memory_usage_ratio,
            "system_status": status.get("system_status", "Unknown"),
            "agents_online": status.get("agents_online", 0),
            "timestamp": status.get("timestamp")
        }
    
    def should_reduce_activity(self, threshold=0.7):
        """Determine if we should reduce computer-use activity based on system load."""
        pressure_data = self.get_resource_pressure()
        return pressure_data["overall_pressure"] > threshold
    
    def get_recommended_delay(self):
        """Get recommended delay between operations based on system load."""
        pressure_data = self.get_resource_pressure()
        base_delay = 0.5  # Base 500ms
        
        # Increase delay based on pressure
        pressure_factor = pressure_data["overall_pressure"]
        adaptive_delay = base_delay * (1.0 + pressure_factor * 2.0)  # Up to 1.5x base delay
        
        return min(adaptive_delay, 5.0)  # Cap at 5 seconds

# Example usage and testing
if __name__ == "__main__":
    print("VM AI Gateway Integration Test")
    print("=" * 40)
    
    gateway = VMAIGatewayIntegration()
    
    # Test connection
    print("Testing gateway connection...")
    status = gateway.get_system_status()
    print(f"System Status: {status.get('system_status', 'Unknown')}")
    print(f"CPU Load: {status.get('cpu_load', 'Unknown')}")
    print(f"Memory Used: {status.get('memory_used', 'Unknown')}")
    print(f"Agents Online: {status.get('agents_online', 0)}")
    
    # Test pressure detection
    print("\nTesting resource pressure detection...")
    pressure = gateway.get_resource_pressure()
    print(f"CPU Pressure: {pressure['cpu_pressure']:.2f}")
    print(f"Memory Pressure: {pressure['memory_pressure']:.2f}")
    print(f"Overall Pressure: {pressure['overall_pressure']:.2f}")
    print(f"Should Reduce Activity: {gateway.should_reduce_activity()}")
    print(f"Recommended Delay: {gateway.get_recommended_delay():.2f}s")
    
    # Test caching
    print("\nTesting cache behavior...")
    start = time.time()
    data1 = gateway.get_system_status()
    mid_time = time.time()
    data2 = gateway.get_system_status()
    end = time.time()
    
    print(f"First call: {mid_time - start:.3f}s")
    print(f"Second call (cached): {end - mid_time:.3f}s")
    print(f"Data consistent: {data1.get('timestamp') == data2.get('timestamp')}")