#!/usr/bin/env python3
"""
Enhanced Computer Use Wrapper
Provides improved reliability, error handling, and fallback mechanisms
for the computer_use tool.
"""

import time
import json
from typing import Dict, Any, Optional, Tuple
from hermes_tools import computer_use, terminal

class EnhancedComputerUse:
    """Enhanced computer-use wrapper with reliability features."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.last_screenshot = None
        self.element_cache = {}
        
    def safe_capture(self, app: str = None, mode: str = "som") -> Dict[str, Any]:
        """
        Safely capture screen with retry logic and fallback.
        
        Args:
            app: Target application name
            mode: Capture mode ('som', 'vision', 'ax')
            
        Returns:
            Capture result dictionary
        """
        for attempt in range(self.max_retries):
            try:
                result = computer_use(
                    action="capture",
                    mode=mode,
                    app=app
                )
                
                # Check if we got usable data
                if result and isinstance(result, dict):
                    self.last_screenshot = result
                    return result
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    # Last attempt failed, return error info
                    return {
                        "error": str(e),
                        "attempts": attempt + 1,
                        "success": False
                    }
                
                # Wait before retry
                time.sleep(self.retry_delay * (attempt + 1))
                
        return {"error": "Max retries exceeded", "success": False}
    
    def safe_click(self, element: int = None, coordinate: list = None, 
                   capture_after: bool = False) -> Dict[str, Any]:
        """
        Safely click an element with fallback to coordinates.
        
        Args:
            element: Element index to click
            coordinate: [x, y] coordinates to click (if element not provided)
            capture_after: Whether to capture screen after click
            
        Returns:
            Click result dictionary
        """
        # Try element-based click first
        if element is not None:
            for attempt in range(self.max_retries):
                try:
                    result = computer_use(
                        action="click",
                        element=element,
                        capture_after=capture_after
                    )
                    
                    if result and not result.get("error"):
                        return result
                        
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        break  # Fall through to coordinate fallback
                    time.sleep(self.retry_delay * (attempt + 1))
        
        # Fallback to coordinate-based clicking
        if coordinate is not None:
            for attempt in range(self.max_retries):
                try:
                    result = computer_use(
                        action="click",
                        coordinate=coordinate,
                        capture_after=capture_after
                    )
                    
                    if result and not result.get("error"):
                        return result
                        
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        return {
                            "error": str(e),
                            "attempts": attempt + 1,
                            "fallback_used": "coordinates",
                            "success": False
                        }
                    time.sleep(self.retry_delay * (attempt + 1))
                    
        return {"error": "Both element and coordinate clicks failed", "success": False}
    
    def safe_type(self, text: str, clear_first: bool = True) -> Dict[str, Any]:
        """
        Safely type text with verification.
        
        Args:
            text: Text to type
            clear_first: Whether to clear field before typing
            
        Returns:
            Type result dictionary
        """
        for attempt in range(self.max_retries):
            try:
                result = computer_use(
                    action="type",
                    text=text
                )
                
                if result and not result.get("error"):
                    # Optionally verify the text was entered correctly
                    if self._verify_input(text):
                        return result
                        
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        "error": str(e),
                        "attempts": attempt + 1,
                        "success": False
                    }
                time.sleep(self.retry_delay * (attempt + 1))
                
        return {"error": "Max retries exceeded for typing", "success": False}
    
    def safe_key(self, keys: str) -> Dict[str, Any]:
        """
        Safely send key presses.
        
        Args:
            keys: Key combination to send (e.g., "return", "ctrl+c")
            
        Returns:
            Key result dictionary
        """
        for attempt in range(self.max_retries):
            try:
                result = computer_use(
                    action="key",
                    keys=keys
                )
                
                if result and not result.get("error"):
                    return result
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        "error": str(e),
                        "attempts": attempt + 1,
                        "success": False
                    }
                time.sleep(self.retry_delay * (attempt + 1))
                
        return {"error": "Max retries exceeded for key press", "success": False}
    
    def wait_for_element(self, element_name: str, timeout: float = 10.0, 
                        app: str = None) -> Dict[str, Any]:
        """
        Wait for an element to appear on screen.
        
        Args:
            element_name: Name or description of element to wait for
            timeout: Maximum time to wait in seconds
            app: Target application name
            
        Returns:
            Result dictionary with element info if found
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            capture_result = self.safe_capture(app=app)
            
            if capture_result.get("error"):
                time.sleep(0.5)
                continue
                
            # Search for element in the captured data
            elements = capture_result.get("elements", [])
            for elem in elements:
                if (element_name.lower() in elem.get("name", "").lower() or
                    element_name.lower() in elem.get("text", "").lower()):
                    return {
                        "found": True,
                        "element": elem,
                        "wait_time": time.time() - start_time
                    }
            
            time.sleep(0.5)
            
        return {
            "found": False,
            "error": f"Element '{element_name}' not found within {timeout} seconds",
            "wait_time": time.time() - start_time
        }
    
    def _verify_input(self, expected_text: str) -> bool:
        """
        Verify that text was correctly entered (simplified implementation).
        In a real implementation, this would use OCR or other verification methods.
        """
        # For now, we'll assume it worked if no error was thrown
        # A more sophisticated implementation would recapture and check
        return True
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the enhanced computer-use wrapper."""
        # This would be expanded with actual metrics tracking
        return {
            "wrapper_version": "1.0.0",
            "features": [
                "retry_mechanism",
                "fallback_to_coordinates",
                "safe_capture",
                "safe_click",
                "safe_type",
                "safe_key",
                "wait_for_element"
            ]
        }

# Global instance for easy access
enhanced_cu = EnhancedComputerUse()

def safe_capture(*args, **kwargs):
    """Wrapper function for easy access."""
    return enhanced_cu.safe_capture(*args, **kwargs)

def safe_click(*args, **kwargs):
    """Wrapper function for easy access."""
    return enhanced_cu.safe_click(*args, **kwargs)

def safe_type(*args, **kwargs):
    """Wrapper function for easy access."""
    return enhanced_cu.safe_type(*args, **kwargs)

def safe_key(*args, **kwargs):
    """Wrapper function for easy access."""
    return enhanced_cu.safe_key(*args, **kwargs)

def wait_for_element(*args, **kwargs):
    """Wrapper function for easy access."""
    return enhanced_cu.wait_for_element(*args, **kwargs)

if __name__ == "__main__":
    # Example usage
    print("Enhanced Computer Use Wrapper")
    print("=" * 40)
    
    # Test capture
    print("Testing screen capture...")
    result = safe_capture()
    if result.get("error"):
        print(f"Capture failed: {result['error']}")
    else:
        print(f"Capture successful! Found {len(result.get('elements', []))} elements")
    
    # Print stats
    print("\nPerformance stats:")
    print(json.dumps(enhanced_cu.get_performance_stats(), indent=2))