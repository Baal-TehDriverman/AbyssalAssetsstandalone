#!/usr/bin/env python3
"""
Windows Port Console Synchronization for Computer Use
Enables bidirectional communication between Linux (this machine) and Windows VM
via HTTP on port 8081.

Modes:
  --server: Start HTTP server to listen for commands from Windows VM
  --client: Send a command to the Windows VM (requires WINDOWS_VM_IP env var)

Actions supported (examples):
  - screenshot: Take a screenshot and return it as base64
  - click: Click at coordinates (x, y)
  - type: Type a string
  - key: Press a key or key combination (e.g., "ctrl+c")

Configuration:
  Set WINDOWS_VM_IP environment variable to the IP address of the Windows VM.
  Defaults to 192.168.122.1 (common virbr0 gateway) if not set.
"""

import os
import sys
import json
import http.server
import socketserver
import threading
import urllib.request
import urllib.error
from urllib.parse import urlparse
import base64
import time
import subprocess
import tempfile
from typing import Dict, Any, Optional, Tuple

# Add the scripts directory to the path to import our enhanced computer use
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import the EnhancedComputerUse class or instance from either module
ComputerClass = None
computer_instance = None

try:
    from enhanced_computer_use import EnhancedComputerUse
    ComputerClass = EnhancedComputerUse
except ImportError:
    pass

if ComputerClass is None:
    try:
        from working_enhanced_cu import EnhancedComputerUse
        ComputerClass = EnhancedComputerUse
    except ImportError:
        pass

if ComputerClass is None:
    # Try to get an instance directly
    try:
        from enhanced_computer_use import enhanced_cu
        computer_instance = enhanced_cu
    except ImportError:
        try:
            from working_enhanced_cu import enhanced_cu
            computer_instance = enhanced_cu
        except ImportError:
            pass

# Default Windows VM IP (common for libvirt virbr0)
DEFAULT_WINDOWS_VM_IP = "192.168.122.1"
# Port for Windows VM to listen on (and for us to send to)
WINDOWS_PORT = 8081
# Port for us to listen on (for Windows to send to us)
LINUX_PORT = 8081

class ComputerControl:
    """Wrapper for computer control operations."""
    
    def __init__(self):
        if ComputerClass is not None:
            self.computer = ComputerClass()
        elif computer_instance is not None:
            self.computer = computer_instance
        else:
            self.computer = None
    
    def screenshot(self, params: dict = None) -> dict:
        """Take a screenshot and return as base64."""
        if not self.computer:
            return {"error": "Computer control not available"}
        try:
            # We'll use the enhanced computer use to capture the screen
            # and then try to get the image data. However, the enhanced_computer_use
            # might not return the image pixels directly.
            # Let's try to use the computer_use tool to capture and see if we can get an image.
            # Alternatively, we can use a system command to take a screenshot.
            # For now, we'll return a placeholder and note that we need to implement image capture.
            # But let's try to get the image from the computer_use tool if possible.
            
            # First, try to capture using the enhanced computer use
            result = self.computer.safe_capture(mode='vision')  # Try vision mode to get image
            if result.get('error'):
                return {"error": result['error']}
            
            # Check if the result contains image data
            # This is a placeholder - we need to see what the actual result contains
            # For now, we'll assume it doesn't and fall back to a system method
            pass
            
        except Exception as e:
            pass  # Fall back to system method
        
        # Fallback: use a system command to take a screenshot
        try:
            # Try to use scrot if available
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Try scrot
            result = subprocess.run(['scrot', tmp_path], capture_output=True, timeout=5)
            if result.returncode != 0:
                # Try gnome-screenshot
                result = subprocess.run(['gnome-screenshot', '-f', tmp_path], capture_output=True, timeout=5)
                if result.returncode != 0:
                    # Try import (from ImageMagick)
                    result = subprocess.run(['import', '-window', 'root', tmp_path], capture_output=True, timeout=5)
                    if result.returncode != 0:
                        os.unlink(tmp_path)
                        return {"error": "No screenshot tool available (scrot, gnome-screenshot, or ImageMagick)"}
            
            # Read the image and encode as base64
            with open(tmp_path, 'rb') as f:
                image_data = f.read()
            os.unlink(tmp_path)
            
            base64_image = base64.b64encode(image_data).decode('utf-8')
            return {
                "status": "success",
                "image": base64_image,
                "format": "png"
            }
        except Exception as e:
            return {"error": f"Failed to take screenshot: {str(e)}"}
    
    def click(self, params: dict) -> dict:
        """Click at coordinates."""
        if not self.computer:
            return {"error": "Computer control not available"}
        try:
            x = params.get('x', 0)
            y = params.get('y', 0)
            button = params.get('button', 'left')
            # Use the enhanced computer use to click
            # We don't have a direct click method, but we can use the computer_use tool via the enhanced class?
            # Since we don't have a direct method, we'll use the computer_use tool via hermes_tools.
            from hermes_tools import computer_use
            result = computer_use(
                action='click',
                x=x,
                y=y,
                button=button
            )
            if result.get('error'):
                return {"error": result['error']}
            return {"status": "success", "message": f"Clicked at ({x}, {y}) with {button} button"}
        except Exception as e:
            return {"error": str(e)}
    
    def type_text(self, params: dict) -> dict:
        """Type text."""
        if not self.computer:
            return {"error": "Computer control not available"}
        try:
            text = params.get('text', '')
            # We don't have a direct type method in enhanced_computer_use
            # Use the computer_use tool
            from hermes_tools import computer_use
            result = computer_use(
                action='type',
                text=text
            )
            if result.get('error'):
                return {"error": result['error']}
            return {"status": "success", "message": f"Typed: {text}"}
        except Exception as e:
            return {"error": str(e)}
    
    def press_key(self, params: dict) -> dict:
        """Press a key or key combination."""
        if not self.computer:
            return {"error": "Computer control not available"}
        try:
            key = params.get('key', '')
            # We don't have a direct key method
            # Use the computer_use tool
            from hermes_tools import computer_use
            result = computer_use(
                action='key',
                key=key
            )
            if result.get('error'):
                return {"error": result['error']}
            return {"status": "success", "message": f"Pressed key: {key}"}
        except Exception as e:
            return {"error": str(e)}
    
    def execute_action(self, action: str, params: dict = None) -> dict:
        """Execute an action by name."""
        if params is None:
            params = {}
        
        if action == "screenshot":
            return self.screenshot(params)
        elif action == "click":
            return self.click(params)
        elif action == "type":
            return self.type_text(params)
        elif action == "key":
            return self.press_key(params)
        else:
            return {"error": f"Unknown action: {action}"}

# Global computer control instance
computer_control = ComputerControl()

class RequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for receiving commands from Windows VM."""
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/command':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "No content"}')
                return
            
            try:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                action = data.get('action')
                params = data.get('params', {})
                
                # Execute the action
                result = computer_control.execute_action(action, params)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid JSON"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'{{"error": "{str(e)}"}}'.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')
    
    def do_GET(self):
        """Handle GET requests (for health check)."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')
    
    def log_message(self, format, *args):
        """Override to use print instead of logging."""
        print(f"{self.address_string()} - {format % args}")

def start_server(port: int = LINUX_PORT):
    """Start the HTTP server to listen for commands from Windows VM."""
    handler = RequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving on port {port}")
        print("Waiting for commands from Windows VM...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.shutdown()

def send_command_to_windows(action: str, params: dict = None, 
                           windows_ip: str = None, port: int = WINDOWS_PORT) -> dict:
    """Send a command to the Windows VM."""
    if params is None:
        params = {}
    
    if windows_ip is None:
        windows_ip = os.environ.get('WINDOWS_VM_IP', DEFAULT_WINDOWS_VM_IP)
        if windows_ip == DEFAULT_WINDOWS_VM_IP:
            print(f"Warning: WINDOWS_VM_IP not set, using default: {windows_ip}", file=sys.stderr)
    
    url = f"http://{windows_ip}:{port}/command"
    data = json.dumps({"action": action, "params": params}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.read() else 'Unknown error'
        return {"error": f"HTTP error {e.code}: {error_body}"}
    except urllib.error.URLError as e:
        return {"error": f"URL error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    """Main function to handle command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Windows Port Console Synchronization for Computer Use')
    parser.add_argument('--server', action='store_true', help='Run in server mode (listen for commands from Windows)')
    parser.add_argument('--client', action='store_true', help='Run in client mode (send command to Windows)')
    parser.add_argument('--action', type=str, help='Action to send (for client mode)')
    parser.add_argument('--params', type=str, help='JSON string of parameters (for client mode)')
    parser.add_argument('--windows-ip', type=str, help='Windows VM IP address (overrides WINDOWS_VM_IP env var)')
    parser.add_argument('--port', type=int, default=WINDOWS_PORT, help=f'Port to use (default: {WINDOWS_PORT})')
    
    args = parser.parse_args()
    
    if args.server:
        # Server mode
        start_server(args.port)
    elif args.client:
        # Client mode
        if not args.action:
            print("Error: --action is required for client mode", file=sys.stderr)
            sys.exit(1)
        
        params = {}
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in --params: {e}", file=sys.stderr)
                sys.exit(1)
        
        windows_ip = args.windows_ip if args.windows_ip else None
        result = send_command_to_windows(args.action, params, windows_ip, args.port)
        print(json.dumps(result, indent=2))
    else:
        # Default: show help
        parser.print_help()

if __name__ == '__main__':
    main()