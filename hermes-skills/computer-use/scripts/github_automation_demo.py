#!/usr/bin/env python3
"""
GitHub Automation Demonstration
Shows how to integrate kairos-dream, computer-use, and adaptive skill loading
to automate GitHub interactions (in a safe, read-only manner).
"""

import os
import sys
import time
import json
import subprocess
from threading import Thread
from queue import Queue, Empty

# Add the scripts directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from adaptive_skill_loader import AdaptiveSkillLoader
    from enhanced_computer_use import enhanced_cu
    COMPUTER_USE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}", file=sys.stderr)
    COMPUTER_USE_AVAILABLE = False

def run_kairos_dream():
    """Run the kairos-dream skill and return any output."""
    try:
        result = subprocess.run(
            ["hermes", "skills", "run", "kairos-dream"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Kairos-dream failed: {result.stderr}"
    except Exception as e:
        return f"Error running kairos-dream: {str(e)}"

def demonstrate_github_browsing():
    """Demonstrate using computer-use to browse GitHub (read-only)."""
    if not COMPUTER_USE_AVAILABLE:
        print("Computer use not available, skipping demonstration.")
        return
    
    print("Starting GitHub browsing demonstration...")
    
    # Step 1: Launch browser (assuming Firefox is available)
    print("Launching Firefox...")
    result = enhanced_cu.safe_capture()  # Just to see what's on screen
    if result.get("error"):
        print(f"Initial capture error: {result['error']}")
    
    # Try to open Firefox
    try:
        # Use the computer_use tool to launch Firefox
        from hermes_tools import terminal
        term_result = terminal("firefox --new-window https://github.com &")
        print(f"Firefox launch result: {term_result}")
        time.sleep(3)  # Give it time to start
    except Exception as e:
        print(f"Could not launch Firefox via terminal: {e}")
        # Fallback: try to use computer_use to click on the Firefox icon if visible
        # This is more complex and depends on the current desktop state
    
    # Step 2: Take a screenshot and analyze with vision
    print("Taking screenshot and analyzing with vision processing...")
    capture_result = enhanced_cu.safe_capture(mode='vision')
    if capture_result.get("error"):
        print(f"Capture error: {capture_result['error']}")
    else:
        print(f"Capture successful. Found {len(capture_result.get('elements', []))} elements.")
        # In a real implementation, we would use the vision processing to analyze the page
        # For now, we just note that we have the elements
    
    # Step 3: Demonstrate navigating to a specific repository (read-only)
    print("Navigating to a public repository (read-only)...")
    # We would use computer-use to click on the search bar, type a repo name, etc.
    # But to keep it simple and safe, we'll just note the steps.
    
    print("Demonstration complete. No actual changes were made to GitHub.")

def main():
    """Main demonstration function."""
    print("GitHub Automation Demonstration with Adaptive Skill Loading")
    print("=" * 50)
    
    # Step 1: Load relevant skills using adaptive loader
    print("\n1. Loading relevant skills via adaptive loader...")
    loader = AdaptiveSkillLoader()
    # Load vision for screen analysis, github for repo interaction concepts, and delegation for AI agent use
    loader.load_skill_category("vision")
    loader.load_skill_category("github")
    loader.load_skill_category("delegation")
    
    # Show current status
    status = loader.get_status()
    print(f"Loaded {status['loaded_count']} skills: {', '.join(status['loaded_skills'][:5])}{'...' if len(status['loaded_skills']) > 5 else ''}")
    
    # Step 2: Run kairos-dream to get creative input
    print("\n2. Running kairos-dream for creative insight...")
    dream_result = run_kairos_dream()
    print(f"Kairos-dream result: {dream_result[:200]}{'...' if len(dream_result) > 200 else ''}")
    
    # Step 3: Demonstrate GitHub interaction (read-only)
    print("\n3. Demonstrating GitHub interaction (read-only, no credentials used)...")
    demonstrate_github_browsing()
    
    print("\nDemonstration finished.")

if __name__ == '__main__':
    main()