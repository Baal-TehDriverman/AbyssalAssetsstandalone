#!/usr/bin/env python3
"""
Demo: Integrated Computer Use with Hermes Ecosystem
Demonstrates the use of enhanced computer use, adaptive skill loading, VM AI gateway, and bidirectional memory.
"""

import os
import sys
import time
import json

# Add the scripts directory to the path
scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# Try to import hermes_tools from the Hermes environment
try:
    import hermes_tools
    # The computer_use tool is available in hermes_tools in the Hermes environment
    from hermes_tools import computer_use, terminal
    HERMES_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import hermes_tools: {e}")
    print("This demo requires running within the Hermes environment.")
    HERMES_TOOLS_AVAILABLE = False

# Import our custom modules
try:
    from enhanced_computer_use import EnhancedComputerUse
    from adaptive_skill_loader import AdaptiveSkillLoader
    from vm_ai_gateway_integration import VMAIGatewayIntegration
    from bidirectional_memory_hooks import ComputerUseMemoryHooks, hook_computer_use_action
    CUSTOM_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import custom modules: {e}")
    CUSTOM_MODULES_AVAILABLE = False

def demo_enhanced_computer_use():
    """Demonstrate enhanced computer use features."""
    if not HERMES_TOOLS_AVAILABLE:
        print("Skipping enhanced computer use demo (hermes_tools not available)")
        return None
    
    print("\n=== Enhanced Computer Use Demo ===")
    ecu = EnhancedComputerUse()
    
    # Take a screenshot with retry logic
    print("Taking screenshot...")
    result = ecu.safe_capture()
    if result.get('error'):
        print(f"  Error: {result['error']}")
        return None
    else:
        element_count = len(result.get('elements', []))
        print(f"  Success! Captured {element_count} UI elements")
        # Show a few elements if any
        if element_count > 0:
            print("  First few elements:")
            for i, elem in enumerate(result['elements'][:3]):
                print(f"    {i}: {elem.get('label', 'No label')} ({elem.get('role', 'Unknown role')})")
        return result

def demo_adaptive_skill_loader():
    """Demonstrate adaptive skill loading."""
    if not CUSTOM_MODULES_AVAILABLE:
        print("Skipping adaptive skill loader demo (custom modules not available)")
        return None
    
    print("\n=== Adaptive Skill Loader Demo ===")
    loader = AdaptiveSkillLoader()
    
    # Show current status
    status = loader.get_status()
    print(f"  Loaded {status['loaded_count']} skills")
    print(f"  Base skills: {', '.join(status['base_skills'])}")
    
    # Load vision category if not already loaded
    print("  Loading vision skills...")
    loader.load_skill_category("vision")
    
    # Show updated status
    status = loader.get_status()
    print(f"  Now loaded {status['loaded_count']} skills")
    return status

def demo_vm_ai_gateway():
    """Demonstrate VM AI Gateway integration."""
    if not CUSTOM_MODULES_AVAILABLE:
        print("Skipping VM AI gateway demo (custom modules not available)")
        return None
    
    print("\n=== VM AI Gateway Demo ===")
    gateway = VMAIGatewayIntegration()
    
    # Get system resources
    print("  Getting system resources...")
    resources = gateway.get_system_resources()
    print(f"    CPU: {resources.cpu_percent:.1f}%")
    print(f"    Memory: {resources.memory_mb:.0f} MB")
    print(f"    Disk: {resources.disk_usage_percent:.1f}%")
    
    # Check if vision processing is safe
    vision_safe = gateway.is_vision_safe(resources)
    print(f"  Vision processing safe: {vision_safe}")
    
    # Get health status
    health = gateway.get_health_status()
    print(f"  Gateway status: {health.get('status', 'unknown')}")
    return resources

def demo_bidirectional_memory():
    """Demonstrate bidirectional memory hooks."""
    if not CUSTOM_MODULES_AVAILABLE:
        print("Skipping bidirectional memory demo (custom modules not available)")
        return None
    
    print("\n=== Bidirectional Memory Demo ===")
    hooks = ComputerUseMemoryHooks()
    
    # Simulate recording an action
    print("  Recording a sample action...")
    action_id = hooks.record_action(
        action_type="click",
        params={"x": 100, "y": 200, "button": "left"},
        result={"success": True, "timestamp": time.time()},
        context={"app": "demo", "purpose": "testing"}
    )
    print(f"  Recorded action with ID: {action_id}")
    
    # Retrieve recent actions
    recent = hooks.get_recent_actions(limit=5)
    print(f"  Retrieved {len(recent)} recent actions")
    return action_id

def main():
    """Run all demos."""
    print("Starting Integrated Computer Use Demo")
    print("=" * 50)
    
    # Run demos
    cu_result = demo_enhanced_computer_use()
    skill_status = demo_adaptive_skill_loader()
    vm_resources = demo_vm_ai_gateway()
    action_id = demo_bidirectional_memory()
    
    print("\n" + "=" * 50)
    print("Demo completed successfully!")
    
    # Summary
    print("\nSummary:")
    if cu_result:
        print(f"  - Computer Use: Captured {len(cu_result.get('elements', []))} UI elements")
    if skill_status:
        print(f"  - Skill Loader: {skill_status['loaded_count']} skills loaded")
    if vm_resources:
        print(f"  - VM Gateway: CPU {vm_resources.cpu_percent:.1f}%, Memory {vm_resources.mb:.0f}MB")
    if action_id:
        print(f"  - Memory Hooks: Recorded action ID {action_id}")

if __name__ == "__main__":
    # Check if we're in the Hermes environment
    if not HERMES_TOOLS_AVAILABLE:
        print("ERROR: This demo must be run within the Hermes environment.")
        print("Please run it using the Hermes-provided Python or in a Hermes shell.")
        sys.exit(1)
    
    try:
        main()
    except Exception as e:
        print(f"\nERROR: Demo failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)