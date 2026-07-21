#!/usr/bin/env python3
"""
Demo: Using computer-use to navigate GitHub and kairos-dream to generate ideas.
"""

import subprocess
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from adaptive_skill_loader import AdaptiveSkillLoader
    from enhanced_computer_use import enhanced_cu
    COMPUTER_USE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}", file=sys.stderr)
    COMPUTER_USE_AVAILABLE = False

def main():
    if not COMPUTER_USE_AVAILABLE:
        print("Computer use not available. Exiting.")
        return 1

    print("=== GitHub and Kairos-Dream Demo ===")

    # Step 1: Load necessary skills for vision and delegation
    print("\n1. Loading vision and delegation skills...")
    loader = AdaptiveSkillLoader()
    loader.load_skill_category("vision")
    loader.load_skill_category("delegation")
    print("   Skills loaded.")

    # Step 2: Ensure Firefox is running
    print("\n2. Ensuring Firefox is running...")
    try:
        # Check if Firefox is running
        subprocess.check_output(["pgrep", "firefox"], stderr=subprocess.DEVNULL)
        print("   Firefox is already running.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   Starting Firefox...")
        # Start Firefox in the background
        subprocess.Popen(["firefox"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Wait for Firefox to start and create a window
        time.sleep(5)
        print("   Firefox started.")

    # Step 3: Focus the address bar and navigate to GitHub
    print("\n3. Navigating to GitHub...")
    # Focus the address bar (Ctrl+L works in most browsers)
    print("   Focusing address bar (Ctrl+L)...")
    result = enhanced_cu.safe_key("ctrl+l")
    if result.get("error"):
        print(f"   Error focusing address bar: {result['error']}")
        # Try to continue anyway
    time.sleep(0.5)

    url = "https://github.com/tehlappy"
    print(f"   Typing URL: {url}")
    result = enhanced_cu.safe_type(url)
    if result.get("error"):
        print(f"   Error typing URL: {result['error']}")
        return 1
    time.sleep(0.5)

    print("   Pressing Enter...")
    result = enhanced_cu.safe_key("enter")
    if result.get("error"):
        print(f"   Error pressing Enter: {result['error']}")
        return 1
    # Wait for page to load
    print("   Waiting for page to load (10 seconds)...")
    time.sleep(10)

    # Step 4: Take a screenshot to verify
    print("\n4. Taking screenshot to verify...")
    result = enhanced_cu.safe_capture()
    if result.get("error"):
        print(f"   Error capturing screen: {result['error']}")
    else:
        print(f"   Screenshot successful. Detected {len(result.get('elements', []))} UI elements.")

    # Step 5: Run kairos-dream to generate ideas
    print("\n5. Running kairos-dream for idea generation...")
    try:
        dream_result = subprocess.run(
            ["hermes", "skills", "run", "kairos-dream"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if dream_result.returncode == 0:
            print("   Kairos-dream output:")
            print("   " + "\n   ".join(dream_result.stdout.strip().split('\n')))
        else:
            print(f"   Kairos-dream error (exit code {dream_result.returncode}):")
            print("   " + dream_result.stderr.strip())
    except subprocess.TimeoutExpired:
        print("   Kairos-dream timed out after 30 seconds.")
    except Exception as e:
        print(f"   Exception running kairos-dream: {e}")

    print("\n=== Demo completed ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())