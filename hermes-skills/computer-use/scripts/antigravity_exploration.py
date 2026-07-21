#!/usr/bin/env python3
"""
Antigravity-Ingestion-Bridge Inspired Exploration Mechanisms for Computer Use
Adds controlled stochasticity and novelty-seeking behavior to prevent 
behavioral rigidity in interaction patterns.
"""

import random
import time
import math
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
import sys
import os

# Add the computer-use scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

class ExplorationStrategy(Enum):
    """Different exploration strategies for adding novelty"""
    EPSILON_GREEDY = "epsilon_greedy"      # Mostly exploit, sometimes explore
    BOLTZMANN = "boltzmann"                # Temperature-based exploration
    THOMPSON_SAMPLING = "thompson_sampling" # Bayesian exploration
    NOVELTY_SEEKING = "novelty_seeking"    # Seek novel states/actions
    CURIOUSITY_DRIVEN = "curiousity_driven" # Intrinsic motivation for novelty

class AntigravityExploration:
    """
    Implements antigravity-ingestion-bridge inspired exploration mechanisms
    to prevent behavioral rigidity in computer-use interaction patterns.
    """
    
    def __init__(self, 
                 exploration_rate: float = 0.1,
                 exploration_decay: float = 0.995,
                 min_exploration_rate: float = 0.01,
                 novelty_threshold: float = 0.3,
                 history_size: int = 100):
        """
        Initialize the exploration system.
        
        Args:
            exploration_rate: Probability of exploration vs exploitation (0-1)
            exploration_decay: Rate at which exploration decreases over time
            min_exploration_rate: Minimum exploration rate to maintain
            novelty_threshold: Threshold for considering something novel
            history_size: Number of past actions to remember for novelty detection
        """
        self.exploration_rate = exploration_rate
        self.initial_exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = min_exploration_rate
        self.novelty_threshold = novelty_threshold
        self.history_size = history_size
        
        # History tracking
        self.action_history: List[Dict[str, Any]] = []
        self.state_history: List[Dict[str, Any]] = []
        self.outcome_history: List[float] = []  # Success/reward values
        
        # Exploration statistics
        self.total_actions = 0
        self.exploration_count = 0
        
        # For novelty detection
        self.action_frequencies: Dict[str, int] = {}
        self.state_visits: Dict[str, int] = {}
        
    def should_explore(self) -> bool:
        """
        Determine whether to explore or exploit based on current exploration rate.
        
        Returns:
            True if should explore, False if should exploit
        """
        # Decay exploration rate over time
        self.exploration_rate = max(
            self.min_exploration_rate,
            self.exploration_rate * self.exploration_decay
        )
        
        return random.random() < self.exploration_rate
    
    def record_action(self, action: Dict[str, Any], outcome: float = 0.5):
        """
        Record an action and its outcome for learning.
        
        Args:
            action: The action that was taken
            outcome: The result/success of the action (0.0 = failure, 1.0 = success)
        """
        self.action_history.append({
            'action': action.copy(),
            'timestamp': time.time(),
            'outcome': outcome
        })
        
        self.outcome_history.append(outcome)
        self.total_actions += 1
        
        # Keep history bounded
        if len(self.action_history) > self.history_size:
            self.action_history.pop(0)
            self.outcome_history.pop(0)
        
        # Update action frequencies for novelty detection
        action_key = self._get_action_key(action)
        self.action_frequencies[action_key] = self.action_frequencies.get(action_key, 0) + 1
    
    def _get_action_key(self, action: Dict[str, Any]) -> str:
        """Generate a unique key for an action type."""
        action_type = action.get('type', 'unknown')
        params = action.get('params', {})
        
        # Create a simplified representation for frequency counting
        key_parts = [action_type]
        for k, v in sorted(params.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}:{v}")
        
        return "|".join(key_parts)
    
    def get_exploration_bonus(self, action: Dict[str, Any]) -> float:
        """
        Calculate exploration bonus for an action based on novelty.
        
        Args:
            action: The action to evaluate
            
        Returns:
            Exploration bonus value (higher = more novel)
        """
        action_key = self._get_action_key(action)
        frequency = self.action_frequencies.get(action_key, 0)
        
        # Inverse frequency bonus - rarer actions get higher bonus
        if frequency == 0:
            novelty_score = 1.0
        else:
            novelty_score = 1.0 / (1.0 + math.log(frequency))
        
        # Normalize by total actions
        if self.total_actions > 0:
            normalized_novelty = novelty_score * math.log(self.total_actions + 1) / self.total_actions
        else:
            normalized_novelty = novelty_score
            
        return min(normalized_novelty, 1.0)  # Cap at 1.0
    
    def explore_click_coordinates(self, 
                                element_bounds: List[int], 
                                exploration_factor: float = 0.3) -> List[int]:
        """
        Apply exploration to click coordinates within element bounds.
        
        Args:
            element_bounds: [x1, y1, x2, y2] bounding box of element
            exploration_factor: How much to deviate from center (0-1)
            
        Returns:
            Modified coordinates [x, y] for clicking
        """
        if len(element_bounds) != 4:
            return [element_bounds[0] + (element_bounds[2] - element_bounds[0]) // 2,
                    element_bounds[1] + (element_bounds[3] - element_bounds[1]) // 2]
        
        x1, y1, x2, y2 = element_bounds
        
        # Calculate center
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        # Calculate exploration radius
        width = x2 - x1
        height = y2 - y1
        radius_x = int(width * exploration_factor // 2)
        radius_y = int(height * exploration_factor // 2)
        
        # Add random offset within exploration radius
        offset_x = random.randint(-radius_x, radius_x)
        offset_y = random.randint(-radius_y, radius_y)
        
        # Ensure we stay within bounds
        final_x = max(x1, min(x2, center_x + offset_x))
        final_y = max(y1, min(y2, center_y + offset_y))
        
        return [final_x, final_y]
    
    def explore_timing(self, base_delay: float, 
                      exploration_factor: float = 0.5) -> float:
        """
        Add exploratory variation to timing delays.
        
        Args:
            base_delay: Base delay in seconds
            exploration_factor: How much to vary the delay (0-1)
            
        Returns:
            Modified delay with exploration noise
        """
        if exploration_factor <= 0:
            return base_delay
            
        # Add Gaussian noise to the delay
        noise = random.gauss(0, base_delay * exploration_factor)
        return max(0.01, base_delay + noise)  # Ensure minimum delay
    
    def select_exploratory_action(self, 
                                available_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select an action using exploration strategy.
        
        Args:
            available_actions: List of possible actions to choose from
            
        Returns:
            Selected action with exploration applied
        """
        if not available_actions:
            return None
            
        if len(available_actions) == 1:
            # Only one option, apply parameter exploration
            return self._explore_action_parameters(available_actions[0])
        
        # Calculate exploration bonuses for each action
        action_scores = []
        for action in available_actions:
            # Base score from historical performance (if available)
            base_score = 0.5  # Default neutral score
            
            # Add exploration bonus for novelty
            exploration_bonus = self.get_exploration_bonus(action)
            
            # Combined score
            total_score = base_score + exploration_bonus
            action_scores.append((action, total_score))
        
        # Sort by score (descending)
        action_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Sometimes select randomly from top options to encourage exploration
        if random.random() < 0.3 and len(action_scores) > 1:
            # Select from top 3 options
            top_n = min(3, len(action_scores))
            selected_action = random.choice(action_scores[:top_n])[0]
        else:
            # Select the best action
            selected_action = action_scores[0][0]
        
        # Apply parameter-level exploration
        return self._explore_action_parameters(selected_action)
    
    def _explore_action_parameters(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply exploration to the parameters of an action.
        
        Args:
            action: The base action to explore
            
        Returns:
            Action with explored parameters
        """
        explored_action = action.copy()
        explored_action['params'] = action.get('params', {}).copy()
        
        action_type = action.get('type', '')
        
        # Apply different exploration strategies based on action type
        if action_type == 'click':
            # Explore click timing and precise location
            if 'coordinate' in explored_action['params']:
                coord = explored_action['params']['coordinate']
                if isinstance(coord, list) and len(coord) == 2:
                    # Add small random offset to coordinates
                    jitter_x = random.randint(-5, 5)
                    jitter_y = random.randint(-5, 5)
                    explored_action['params']['coordinate'] = [
                        coord[0] + jitter_x,
                        coord[1] + jitter_y
                    ]
            
            # Vary click timing
            if 'duration' in explored_action['params']:
                base_duration = explored_action['params']['duration']
                explored_action['params']['duration'] = max(
                    0.01, 
                    base_duration * random.uniform(0.5, 2.0)
                )
        
        elif action_type == 'type':
            # Explore typing speed and timing
            if 'interval' in explored_action['params']:
                base_interval = explored_action['params']['interval']
                explored_action['params']['interval'] = max(
                    0.001,
                    base_interval * random.uniform(0.5, 2.0)
                )
            
            # Occasionally add typos and correct them (for realism)
            if random.random() < 0.1:  # 10% chance of typo exploration
                text = explored_action['params'].get('text', '')
                if text and len(text) > 3:
                    # Introduce a small typo
                    pos = random.randint(0, len(text)-1)
                    char_list = list(text)
                    # Replace with adjacent key (simplified)
                    char_list[pos] = chr(ord(char_list[pos]) + 1) if char_list[pos] != 'z' else 'a'
                    explored_action['params']['text'] = ''.join(char_list)
                    # Note: In a real implementation, we'd add a correction action afterwards
        
        elif action_type == 'key':
            # Explore key timing and combinations
            pass  # Key presses are harder to meaningfully explore
        
        # Mark this as an exploratory action
        explored_action['explored'] = True
        explored_action['exploration_timestamp'] = time.time()
        
        return explored_action
    
    def get_exploration_stats(self) -> Dict[str, Any]:
        """Get statistics about exploration usage."""
        exploration_rate = self.exploration_count / max(1, self.total_actions)
        
        return {
            'total_actions': self.total_actions,
            'exploration_count': self.exploration_count,
            'exploration_rate': exploration_rate,
            'current_exploration_rate': self.exploration_rate,
            'unique_actions': len(self.action_frequencies),
            'most_common_action': max(self.action_frequencies.items(), key=lambda x: x[1]) if self.action_frequencies else None,
            'recent_success_rate': sum(self.outcome_history[-10:]) / min(10, len(self.outcome_history)) if self.outcome_history else 0.0
        }
    
    def reset_exploration(self):
        """Reset exploration statistics (useful for starting new tasks)."""
        self.exploration_rate = self.initial_exploration_rate
        self.action_history.clear()
        self.state_history.clear()
        self.outcome_history.clear()
        self.action_frequencies.clear()
        self.state_visits.clear()
        self.total_actions = 0
        self.exploration_count = 0

# Global exploration instance
exploration_engine = AntigravityExploration()

def explore_action(action: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply exploration to an action using the global exploration engine.
    
    Args:
        action: The action to explore
        
    Returns:
        Explored action
    """
    if exploration_engine.should_explore():
        exploration_engine.exploration_count += 1
        return exploration_engine.explore_action_parameters(action)
    else:
        # Still update statistics even when exploiting
        exploration_engine.total_actions += 1
        return action

def record_action_outcome(action: Dict[str, Any], outcome: float):
    """
    Record the outcome of an action for learning.
    
    Args:
        action: The action that was taken
        outcome: The result (0.0 = failure, 1.0 = success)
    """
    exploration_engine.record_action(action, outcome)

def get_exploration_state() -> Dict[str, Any]:
    """Get the current state of the exploration system."""
    return exploration_engine.get_exploration_stats()

# Example usage and testing
if __name__ == "__main__":
    print("Antigravity-Inspired Exploration System - Test Suite")
    print("=" * 55)
    
    # Test exploration decision
    print("\n1. Testing exploration decision...")
    exploration_rates = []
    for i in range(20):
        explore = exploration_engine.should_explore()
        exploration_rates.append(explore)
        if explore:
            exploration_engine.exploration_count += 1
        exploration_engine.total_actions += 1
    
    explore_percentage = sum(exploration_rates) / len(exploration_rates) * 100
    print(f"   Exploration rate: {explore_percentage:.1f}% ({sum(exploration_rates)}/20)")
    
    # Test coordinate exploration
    print("\n2. Testing coordinate exploration...")
    test_bounds = [100, 100, 200, 200]  # x1, y1, x2, y2
    original_center = [150, 150]
    
    explored_coords = []
    for _ in range(10):
        explored = exploration_engine.explore_click_coordinates(test_bounds, 0.4)
        explored_coords.append(explored)
    
    avg_x = sum(c[0] for c in explored_coords) / len(explored_coords)
    avg_y = sum(c[1] for c in explored_coords) / len(explored_coords)
    print(f"   Average explored position: ({avg_x:.1f}, {avg_y:.1f})")
    print(f"   Expected center: ({original_center[0]}, {original_center[1]})")
    
    # Test timing exploration
    print("\n3. Testing timing exploration...")
    base_delay = 0.5
    explored_delays = []
    for _ in range(10):
        delayed = exploration_engine.explore_timing(base_delay, 0.3)
        explored_delays.append(delayed)
    
    avg_delay = sum(explored_delays) / len(explored_delays)
    print(f"   Average explored delay: {avg_delay:.3f}s")
    print(f"   Base delay: {base_delay}s")
    
    # Test action selection exploration
    print("\n4. Testing action selection exploration...")
    test_actions = [
        {'type': 'click', 'params': {'element': 5}},
        {'type': 'type', 'params': {'text': 'hello world'}},
        {'type': 'key', 'params': {'keys': 'enter'}}
    ]
    
    selected_actions = []
    for _ in range(5):
        selected = exploration_engine.select_exploratory_action(test_actions)
        if selected:
            selected_actions.append(selected['type'])
    
    from collections import Counter
    action_counts = Counter(selected_actions)
    print(f"   Action selection distribution: {dict(action_counts)}")
    
    # Test exploration stats
    print("\n5. Exploration statistics...")
    stats = exploration_engine.get_exploration_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n✓ Antigravity exploration system initialized successfully")