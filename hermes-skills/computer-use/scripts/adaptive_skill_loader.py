#!/usr/bin/env python3
"""
Adaptive Skill Loading System for Computer Use
Dynamically loads/unloads Hermes skills based on task context and resource usage.
"""

import os
import sys
import json
import time
import subprocess
import threading
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict

# Try to import psutil, fallback to basic monitoring if not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not installed, using basic system monitoring", file=sys.stderr)

# Path to Hermes skills directory
SKILLS_DIR = os.path.expanduser("~/.hermes/skills")
# Path to keep track of loaded skills
LOADED_SKILLS_FILE = os.path.expanduser("~/.hermes/var/adaptive_skills_loaded.json")

# Skill categories and their resource profiles
SKILL_PROFILES = {
    "vision": {
        "skills": ["metaconscious/concurrent-bidirectional-memory", "computer-use", "hermes-desktop-plugins"],
        "memory_mb": 200,
        "cpu_percent": 20,
        "description": "Skills for visual processing and GUI interaction"
    },
    "delegation": {
        "skills": ["autonomous-ai-agents/claude-code", "autonomous-ai-agents/codex", "autonomous-ai-agents/opencode"],
        "memory_mb": 300,
        "cpu_percent": 30,
        "description": "Skills for delegating tasks to external AI agents"
    },
    "memory": {
        "skills": ["metaconscious/concurrent-bidirectional-memory", "memory/lilith-worktree-conventions"],
        "memory_mb": 150,
        "cpu_percent": 10,
        "description": "Skills for memory management and persistence"
    },
    "github": {
        "skills": ["github/github-repo-management", "github/github-issues", "github/github-pr-workflow"],
        "memory_mb": 100,
        "cpu_percent": 15,
        "description": "Skills for GitHub interaction"
    },
    "productivity": {
        "skills": ["productivity/google-workspace", "productivity/airtable", "productivity/notion"],
        "memory_mb": 180,
        "cpu_percent": 20,
        "description": "Skills for productivity tools"
    }
}

# Base skills that are always loaded
BASE_SKILLS = {"computer-use", "hermes-agent"}

@dataclass
class SystemResources:
    cpu_percent: float
    memory_mb: float
    disk_usage_percent: float
    timestamp: float

class AdaptiveSkillLoader:
    def __init__(self):
        self.loaded_skills: Set[str] = set()
        self.loaded_skills.update(BASE_SKILLS)
        self._load_loaded_state()
        self.monitoring = False
        self.monitor_thread = None
    
    def _load_loaded_state(self):
        """Load previously tracked loaded skills from file."""
        try:
            if os.path.exists(LOADED_SKILLS_FILE):
                with open(LOADED_SKILLS_FILE, 'r') as f:
                    data = json.load(f)
                    self.loaded_skills.update(set(data.get('loaded_skills', [])))
                    self.loaded_skills.update(BASE_SKILLS)  # Ensure base skills are always included
        except Exception:
            pass  # If we can't load, start with base skills
    
    def _save_loaded_state(self):
        """Save currently tracked loaded skills to file."""
        try:
            os.makedirs(os.path.dirname(LOADED_SKILLS_FILE), exist_ok=True)
            with open(LOADED_SKILLS_FILE, 'w') as f:
                json.dump({
                    'loaded_skills': list(self.loaded_skills),
                    'timestamp': time.time()
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save loaded skills state: {e}", file=sys.stderr)
    
    def get_system_resources(self) -> SystemResources:
        """Get current system resource usage."""
        if HAS_PSUTIL:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            return SystemResources(
                cpu_percent=cpu_percent,
                memory_mb=memory.used / 1024 / 1024,
                disk_usage_percent=disk.percent,
                timestamp=time.time()
            )
        else:
            # Fallback: use basic commands
            try:
                # Get CPU usage from /proc/stat (Linux)
                with open('/proc/stat', 'r') as f:
                    line = f.readline()
                    if line.startswith('cpu '):
                        parts = line.split()
                        total_time = sum(int(x) for x in parts[1:])
                        idle_time = int(parts[4]) if len(parts) > 4 else 0
                        # We need a previous measurement to calculate percentage - simplified
                        cpu_percent = 0.0  # Placeholder
                
                # Get memory usage from /proc/meminfo
                mem_total = 0
                mem_available = 0
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            mem_total = int(line.split()[1]) * 1024  # Convert kB to bytes
                        elif line.startswith('MemAvailable:'):
                            mem_available = int(line.split()[1]) * 1024
                
                memory_used = mem_total - mem_available if mem_total > 0 else 0
                memory_mb = memory_used / 1024 / 1024
                
                # Disk usage - simplified
                disk_usage_percent = 0.0
                
                return SystemResources(
                    cpu_percent=cpu_percent,
                    memory_mb=memory_mb,
                    disk_usage_percent=disk_usage_percent,
                    timestamp=time.time()
                )
            except Exception:
                # If all else fails, return zeros
                return SystemResources(0.0, 0.0, 0.0, time.time())
    
    def _is_skill_installed(self, skill_name: str) -> bool:
        """Check if a skill is installed by querying hermes skills list."""
        try:
            result = subprocess.run(
                ["hermes", "skills", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # The list output includes the skill names in the second column
                # We'll do a simple check: if the skill name appears in the output, consider it installed
                return skill_name in result.stdout
            return False
        except Exception:
            return False
    
    def load_skill_category(self, category: str) -> bool:
        """Load all skills in a category by installing them if not already installed."""
        if category not in SKILL_PROFILES:
            print(f"Error: Unknown skill category '{category}'", file=sys.stderr)
            return False
        
        profile = SKILL_PROFILES[category]
        newly_installed = []
        
        for skill_name in profile["skills"]:
            # Skip base skills as they are always considered loaded
            if skill_name in BASE_SKILLS:
                self.loaded_skills.add(skill_name)
                continue
                
            if not self._is_skill_installed(skill_name):
                try:
                    result = subprocess.run(
                        ["hermes", "skills", "install", skill_name],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        self.loaded_skills.add(skill_name)
                        newly_installed.append(skill_name)
                        print(f"Installed skill: {skill_name}")
                    else:
                        print(f"Warning: Failed to install skill {skill_name}: {result.stderr}", file=sys.stderr)
                except Exception as e:
                    print(f"Warning: Exception installing skill {skill_name}: {e}", file=sys.stderr)
            else:
                # Skill is already installed, mark as loaded
                self.loaded_skills.add(skill_name)
        
        if newly_installed:
            self._save_loaded_state()
            return True
        return False
    
    def unload_skill_category(self, category: str) -> bool:
        """Unload all skills in a category by uninstalling them (keeping base skills)."""
        if category not in SKILL_PROFILES:
            print(f"Error: Unknown skill category '{category}'", file=sys.stderr)
            return False
        
        profile = SKILL_PROFILES[category]
        newly_uninstalled = []
        
        for skill_name in profile["skills"]:
            # Don't uninstall base skills
            if skill_name in BASE_SKILLS:
                continue
                
            if self._is_skill_installed(skill_name):
                try:
                    result = subprocess.run(
                        ["hermes", "skills", "uninstall", skill_name],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        self.loaded_skills.discard(skill_name)  # Use discard to avoid error if not present
                        newly_uninstalled.append(skill_name)
                        print(f"Uninstalled skill: {skill_name}")
                    else:
                        print(f"Warning: Failed to uninstall skill {skill_name}: {result.stderr}", file=sys.stderr)
                except Exception as e:
                    print(f"Warning: Exception uninstalling skill {skill_name}: {e}", file=sys.stderr)
            else:
                # Skill is not installed, ensure it's not in loaded_skills
                self.loaded_skills.discard(skill_name)
        
        if newly_uninstalled:
            self._save_loaded_state()
            return True
        return False
    
    def adapt_to_context(self, context: str, resources: SystemResources = None):
        """Adapt skill loading based on context and current resources."""
        if resources is None:
            resources = self.get_system_resources()
        
        print(f"Adapting to context: {context}")
        print(f"Current resources: CPU {resources.cpu_percent:.1f}%, Memory {resources.memory_mb:.0f}MB")
        
        # Determine which categories are relevant to the context
        relevant_categories = []
        context_lower = context.lower()
        
        # Simple keyword matching - can be made more sophisticated
        if any(word in context_lower for word in ["see", "view", "look", "vision", "screen", "image", "visual", "gui", "desktop"]):
            relevant_categories.append("vision")
        if any(word in context_lower for word in ["delegate", "agent", "code", "program", "develop", "write", "codex", "claude", "opencode"]):
            relevant_categories.append("delegation")
        if any(word in context_lower for word in ["memory", "remember", "recall", "store", "learn"]):
            relevant_categories.append("memory")
        if any(word in context_lower for word in ["github", "git", "commit", "push", "pull", "repo", "issue", "pr"]):
            relevant_categories.append("github")
        if any(word in context_lower for word in ["document", "spreadsheet", "email", "calendar", "office"]):
            relevant_categories.append("productivity")
        
        # If no specific category matched, use a default set based on resources
        if not relevant_categories:
            # Under low load, load more capabilities; under high load, stick to basics
            if resources.memory_mb < 1000:  # Low memory
                relevant_categories = []  # Just basics
            elif resources.memory_mb < 2000:  # Medium memory
                relevant_categories = ["vision"]  # Add vision by default for computer use
            else:  # High memory
                relevant_categories = ["vision", "delegation", "memory"]
        
        # Load relevant categories if resources allow
        for category in relevant_categories:
            if self.should_load_skill_category(category, resources):
                self.load_skill_category(category)
        
        # Optionally unload irrelevant categories if we need to free resources
        # (Optional: implement unloading based on pressure)
        self._save_loaded_state()
    
    def should_load_skill_category(self, category: str, resources: SystemResources) -> bool:
        """Determine if we should load a skill category based on resources."""
        if category not in SKILL_PROFILES:
            return False
        
        profile = SKILL_PROFILES[category]
        
        # Check if we have enough resources
        available_memory = self.get_available_memory()
        if available_memory < profile["memory_mb"]:
            return False
        
        # Check CPU usage - if already high, be conservative
        if resources.cpu_percent > 80:
            return False
            
        return True
    
    def get_available_memory(self) -> float:
        """Get available memory in MB."""
        if HAS_PSUTIL:
            return psutil.virtual_memory().available / 1024 / 1024
        else:
            # Rough estimate - assume 50% of total memory is available
            try:
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            total_kb = int(line.split()[1])
                            return (total_kb * 0.5) / 1024  # MB
            except Exception:
                pass
            return 1000.0  # Assume 1GB available as fallback
    
    def start_monitoring(self, interval: float = 5.0):
        """Start background monitoring of resources and auto-adjustment."""
        if self.monitoring:
            return
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.monitor_thread.start()
        print("Started adaptive skill monitoring")
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("Stopped adaptive skill monitoring")
    
    def _monitor_loop(self, interval: float):
        """Background loop to monitor resources and adjust skill loading."""
        while self.monitoring:
            try:
                resources = self.get_system_resources()
                
                # If under high pressure, consider unloading some non-essential skills
                if resources.memory_mb > 1000 or resources.cpu_percent > 80:
                    # Simple heuristic: unload least recently used categories
                    # For now, we just log the pressure
                    print(f"Resource pressure detected: CPU {resources.cpu_percent:.1f}%, Memory {resources.memory_mb:.0f}MB")
                
                time.sleep(interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}", file=sys.stderr)
                time.sleep(interval)
    
    def get_status(self) -> dict:
        """Get current status of loaded skills and resources."""
        resources = self.get_system_resources()
        return {
            "loaded_skills": sorted(list(self.loaded_skills)),
            "loaded_count": len(self.loaded_skills),
            "base_skills": sorted(list(BASE_SKILLS)),
            "resources": asdict(resources),
            "available_categories": list(SKILL_PROFILES.keys())
        }

def main():
    """Command line interface for the adaptive skill loader."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Adaptive Skill Loading System for Computer Use")
    parser.add_argument("--context", type=str, help="Context string to adapt to (e.g., 'github issue creation', 'visual automation')")
    parser.add_argument("--load", type=str, help="Comma-separated list of categories to load")
    parser.add_argument("--unload", type=str, help="Comma-separated list of categories to unload")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring mode")
    parser.add_argument("--interval", type=float, default=5.0, help="Monitoring interval in seconds (default: 5.0)")
    
    args = parser.parse_args()
    
    loader = AdaptiveSkillLoader()
    
    if args.status:
        status = loader.get_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.monitor:
        loader.start_monitoring(args.interval)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            loader.stop_monitoring()
        return
    
    if args.load:
        categories = [c.strip() for c in args.load.split(',')]
        for category in categories:
            loader.load_skill_category(category)
        return
    
    if args.unload:
        categories = [c.strip() for c in args.unload.split(',')]
        for category in categories:
            loader.unload_skill_category(category)
        return
    
    if args.context:
        loader.adapt_to_context(args.context)
        return
    
    # Default: show help
    parser.print_help()

if __name__ == '__main__':
    main()