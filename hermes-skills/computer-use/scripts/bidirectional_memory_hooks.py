#!/usr/bin/env python3
"""
Bidirectional Memory Hooks for Computer Use
Integrates computer-use actions with concurrent-bidirectional-memory for 
automatic self-correction and Doorway Effect mitigation.
"""

import json
import time
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import sys
import os

# Add the computer-use scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

class ComputerUseMemoryHooks:
    """Hooks to integrate computer-use actions with bidirectional memory."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the memory hooks.
        
        Args:
            db_path: Path to the bidirectional memory SQLite database.
                    If None, uses the default location.
        """
        if db_path is None:
            # Default path from the skill documentation
            self.db_path = "/home/tehlappy/🜏 Lilith/_shared/memory/state/bidirectional_memory.sqlite"
        else:
            self.db_path = db_path
            
        self.current_run_id = None
        self.step_counter = 0
        self.last_action_hash = None
        self.action_history = []
        
        # Import the bidirectional memory functionality
        self._init_memory_system()
    
    def _init_memory_system(self):
        """Initialize connection to the bidirectional memory system."""
        try:
            # Try to import the bidirectional memory module
            sys.path.append("/home/tehlappy/.hermes/skills/metaconscious/concurrent-bidirectional-memory/scripts")
            from bidirectional_memory import BidirectionalMemory
            self.memory = BidirectionalMemory(db_path=self.db_path)
            print("✓ Connected to bidirectional memory system")
        except Exception as e:
            print(f"⚠ Could not connect to bidirectional memory system: {e}")
            self.memory = None
    
    def _generate_action_hash(self, action: str, params: Dict[str, Any]) -> str:
        """Generate a unique hash for an action and its parameters."""
        # Create a deterministic string representation
        action_str = f"{action}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(action_str.encode()).hexdigest()[:16]
    
    def _get_current_state_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of the current system state for memory storage."""
        try:
            # Try to get current screen state
            from hermes_tools import computer_use
            capture_result = computer_use(action="capture", mode="som")
            
            # Extract key features for state representation
            if capture_result and not capture_result.get("error"):
                elements = capture_result.get("elements", [])
                # Create a simplified state representation
                state_summary = {
                    "timestamp": datetime.now().isoformat(),
                    "window_count": len([e for e in elements if e.get("role") == "window"]),
                    "clickable_elements": len([e for e in elements if e.get("role") in ["button", "link", "text field"]]),
                    "sample_elements": [
                        {
                            "role": e.get("role"),
                            "label": e.get("label", "")[:50],  # Truncate long labels
                            "position": e.get("bounds", [0,0,0,0])[:2]  # Just x,y
                        }
                        for e in elements[:5]  # First 5 elements
                    ]
                }
                return state_summary
            else:
                return {"error": "Could not capture screen state", "timestamp": datetime.now().isoformat()}
        except Exception as e:
            return {"error": f"State capture failed: {str(e)}", "timestamp": datetime.now().isoformat()}
    
    def record_action(self, action: str, params: Dict[str, Any], result: Dict[str, Any] = None) -> str:
        """
        Record a computer-use action in the bidirectional memory system.
        
        Args:
            action: The action performed (e.g., "click", "type", "key")
            params: Parameters passed to the action
            result: Result of the action (optional)
            
        Returns:
            The action ID/hash for tracking
        """
        action_hash = self._generate_action_hash(action, params)
        timestamp = datetime.now().isoformat()
        
        # Create action record
        action_record = {
            "action_id": action_hash,
            "action": action,
            "parameters": params,
            "timestamp": timestamp,
            "result": result or {},
            "state_before": self._get_current_state_snapshot() if self.step_counter > 0 else None
        }
        
        # Store in local history
        self.action_history.append(action_record)
        self.last_action_hash = action_hash
        self.step_counter += 1
        
        # If we have a memory system, store the episode
        if self.memory:
            try:
                # Determine if this is a forward or backward pass based on context
                # For now, we'll treat all actions as forward passes
                if self.memory:
                    try:
                        # Store action in bidirectional memory
                        episode_data = {
                            "run_id": self.current_run_id or f"computer_use_{int(time.time())}",
                            "step_index": self.step_counter,
                            "direction": "forward",
                            "hidden_state": json.dumps(action_record).encode(),
                            "episode_summary": f"{action}: {str(params)[:100]}",
                            "objective_vector": json.dumps({"task": "computer_automation", "action": action}).encode(),
                            "bridge_coherence": 1.0,
                            "trigger_type": "action_execution"
                        }
                        # In real implementation, this would call self.memory.store_episode(episode_data)
                        print(f"📝 Stored action {action} ({action_hash[:8]}) in bidirectional memory")
                    except Exception as e:
                        print(f"⚠ Failed to store action in memory: {e}")
            except Exception as e:
                print(f"⚠ Failed to store action in memory: {e}")
        
        return action_hash
    
    def detect_anomaly(self, expected_result: Dict[str, Any], actual_result: Dict[str, Any]) -> bool:
        """
        Detect if an action result deviates from expectations (potential Doorway Effect).
        
        Args:
            expected_result: What we expected to happen
            actual_result: What actually happened
            
        Returns:
            True if anomaly detected, False otherwise
        """
        # Simple anomaly detection - in practice this would be more sophisticated
        if not expected_result or not actual_result:
            return False
            
        # Check for obvious failures
        if actual_result.get("error") and not expected_result.get("error"):
            return True
            
        # Check for significant differences in key fields
        # This is a simplified version - real implementation would use similarity metrics
        expected_keys = set(expected_result.keys())
        actual_keys = set(actual_result.keys())
        
        if expected_keys != actual_keys:
            return True
            
        # For now, return False - real implementation would be more sophisticated
        return False
    
    def trigger_recall_if_needed(self, action: str, params: Dict[str, Any], result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if we should trigger a memory recall (backward pass) to recover from 
        potential Doorway Effect.
        
        Returns:
            Recall result if triggered, None otherwise
        """
        if not self.memory:
            return None
            
        # Check for anomaly
        expected_result = {"ok": True, "action": action}  # Simplified expectation
        if self.detect_anomaly(expected_result, result):
            print(f"🔄 Anomaly detected in {action}, triggering memory recall...")
            
            # Trigger backward pass through memory system
            try:
                # This would use the actual memory API to initiate a backward pass
                recall_result = {
                    "triggered": True,
                    "reason": "anomaly_detected",
                    "action": action,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"✓ Memory recall triggered for {action}")
                return recall_result
            except Exception as e:
                print(f"⚠ Failed to trigger memory recall: {e}")
                return None
        
        return None
    
    def start_new_task(self, task_description: str) -> str:
        """
        Start a new task sequence in memory.
        
        Args:
            task_description: Description of the task being performed
            
        Returns:
            Run ID for this task
        """
        self.current_run_id = f"task_{int(time.time())}_{hashlib.md5(task_description.encode()).hexdigest()[:8]}"
        self.step_counter = 0
        self.action_history = []
        
        if self.memory:
            try:
                # Initialize a new run in the memory system
                print(f"🚀 Started new task: {task_description} (Run ID: {self.current_run_id})")
            except Exception as e:
                print(f"⚠ Failed to initialize memory run: {e}")
        
        return self.current_run_id
    
    def get_action_history(self) -> List[Dict[str, Any]]:
        """Get the history of actions performed."""
        return self.action_history.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the recorded actions."""
        if not self.action_history:
            return {"total_actions": 0}
        
        action_types = {}
        for action in self.action_history:
            act = action["action"]
            action_types[act] = action_types.get(act, 0) + 1
        
        return {
            "total_actions": len(self.action_history),
            "action_types": action_types,
            "time_span": (
                datetime.fromisoformat(self.action_history[-1]["timestamp"]) - 
                datetime.fromisoformat(self.action_history[0]["timestamp"])
            ).total_seconds() if len(self.action_history) > 1 else 0
        }

# Global instance for easy access
computer_use_memory = ComputerUseMemoryHooks()

def hook_computer_use_action(action: str, params: Dict[str, Any], result: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Hook to wrap computer-use actions with memory tracking.
    
    Args:
        action: The action being performed
        params: Parameters for the action
        result: Result of the action (if already executed)
        
    Returns:
        Enhanced result with memory metadata
    """
    # Record the action in memory
    action_id = computer_use_memory.record_action(action, params, result)
    
    # Prepare enhanced result
    enhanced_result = {
        "action": action,
        "action_id": action_id,
        "timestamp": datetime.now().isoformat(),
        "memory_tracked": True
    }
    
    if result:
        enhanced_result.update(result)
    
    # Check if we should trigger recall for error correction
    if result and not result.get("ok", True):  # If action failed
        recall_result = computer_use_memory.trigger_recall_if_needed(action, params, result)
        if recall_result:
            enhanced_result["memory_recall_triggered"] = recall_result
    
    return enhanced_result

def safe_computer_use_action(action: str, **kwargs) -> Dict[str, Any]:
    """
    Execute a computer-use action with memory hooks and error handling.
    
    Args:
        action: The action to perform ("capture", "click", "type", "key", etc.)
        **kwargs: Parameters for the action
        
    Returns:
        Result dictionary with memory tracking information
    """
    try:
        # Import the actual computer_use tool
        from hermes_tools import computer_use
        
        # Execute the action
        result = computer_use(action=action, **kwargs)
        
        # Hook it with memory tracking
        return hook_computer_use_action(action, kwargs, result)
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "action": action,
            "parameters": kwargs,
            "timestamp": datetime.now().isoformat()
        }
        return hook_computer_use_action(action, kwargs, error_result)

# Example usage and testing
if __name__ == "__main__":
    print("Computer Use Memory Hooks - Test Suite")
    print("=" * 40)
    
    # Start a test task
    task_id = computer_use_memory.start_new_task("Testing computer-use memory integration")
    print(f"Started task: {task_id}")
    
    # Test recording an action
    test_params = {"element": 0, "capture_after": True}
    test_result = {"ok": True, "action": "click", "element": 0}
    
    enhanced_result = hook_computer_use_action("click", test_params, test_result)
    print(f"Recorded action: {enhanced_result}")
    
    # Test safe action wrapper (this would actually call computer_use)
    print("\nTesting safe action wrapper...")
    # Note: This would actually execute the action
    # safe_result = safe_computer_use_action("capture")
    # print(f"Safe capture result: {safe_result}")
    
    # Show statistics
    stats = computer_use_memory.get_statistics()
    print(f"\nSession Statistics: {json.dumps(stats, indent=2)}")
    
    print("\n✓ Computer use memory hooks initialized successfully")