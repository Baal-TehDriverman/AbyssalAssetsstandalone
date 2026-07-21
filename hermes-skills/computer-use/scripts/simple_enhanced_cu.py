#!/usr/bin/env python3
"""
Simple Enhanced Computer Use Wrapper
Provides improved reliability for computer_use tool calls
"""

import time
import json

def safe_capture(app=None, mode="som", max_retries=3):
    """Safely capture screen with retry logic"""
    from hermes_tools import computer_use
    
    for attempt in range(max_retries):
        try:
            result = computer_use(
                action="capture",
                mode=mode,
                app=app
            )
            
            # Check if we got usable data
            if result and isinstance(result, dict) and not result.get("error"):
                return result
                
        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    "error": str(e),
                    "attempts": attempt + 1,
                    "success": False
                }
            
            # Wait before retry
            time.sleep(0.5 * (attempt + 1))
    
    return {"error": "Max retries exceeded", "success": False}

def safe_click(element=None, coordinate=None, capture_after=False, max_retries=3):
    """Safely click with fallback to coordinates"""
    from hermes_tools import computer_use
    
    # Try element-based click first
    if element is not None:
        for attempt in range(max_retries):
            try:
                result = computer_use(
                    action="click",
                    element=element,
                    capture_after=capture_after
                )
                
                if result and not result.get("error"):
                    return result
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    break  # Fall through to coordinate fallback
                time.sleep(0.5 * (attempt + 1))
    
    # Fallback to coordinate-based clicking
    if coordinate is not None:
        for attempt in range(max_retries):
            try:
                result = computer_use(
                    action="click",
                    coordinate=coordinate,
                    capture_after=capture_after
                )
                
                if result and not result.get("error"):
                    return result
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    return {
                        "error": str(e),
                        "attempts": attempt + 1,
                        "fallback_used": "coordinates",
                        "success": False
                    }
                time.sleep(0.5 * (attempt + 1))
    
    return {"error": "Both element and coordinate clicks failed", "success": False}

def safe_type(text, clear_first=True, max_retries=3):
    """Safely type text with verification"""
    from hermes_tools import computer_use
    
    for attempt in range(max_retries):
        try:
            result = computer_use(
                action="type",
                text=text
            )
            
            if result and not result.get("error"):
                # Simple verification - just check no error occurred
                return result
                
        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    "error": str(e),
                    "attempts": attempt + 1,
                    "success": False
                }
            time.sleep(0.5 * (attempt + 1))
    
    return {"error": "Max retries exceeded for typing", "success": False}

def safe_key(keys, max_retries=3):
    """Safely send key presses"""
    from hermes_tools import computer_use
    
    for attempt in range(max_retries):
        try:
            result = computer_use(
                action="key",
                keys=keys
            )
            
            if result and not result.get("error"):
                return result
                
        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    "error": str(e),
                    "attempts": attempt + 1,
                    "success": False
                }
            time.sleep(0.5 * (attempt + 1))
    
    return {"error": "Max retries exceeded for key press", "success": False}

# Example usage
if __name__ == "__main__":
    print("Simple Enhanced Computer Use Wrapper")
    print("=" * 40)
    
    # Test capture
    print("Testing screen capture...")
    result = safe_capture()
    if result.get("error"):
        print(f"Capture failed: {result['error']}")
    else:
        print(f"Capture successful! Found {len(result.get('elements', []))} elements")
    
    # Show available functions
    print("\nAvailable functions:")
    print("- safe_capture()")
    print("- safe_click()")
    print("- safe_type()")
    print("- safe_key()")