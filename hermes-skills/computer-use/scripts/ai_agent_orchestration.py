#!/usr/bin/env python3
"""
AI Agent Orchestration Layer for Computer Use
Enables intelligent delegation of GUI tasks to specialized AI agents (Codex, Claude Code, OpenCode)
"""

import json
import time
import subprocess
import os
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass
import sys

class AgentType(Enum):
    """Types of AI agents available for delegation"""
    CODEX = "codex"          # Best for coding, file modifications, terminal tasks
    CLAUDE_CODE = "claude-code"  # Best for visual reasoning, UI understanding, complex instructions
    OPENER = "opencode"      # Best for automation scripts, workflow automation
    HERMES = "hermes"        # General purpose, coordination, memory tasks

@dataclass
class AgentTask:
    """Represents a task to be delegated to an AI agent"""
    task_id: str
    description: str
    agent_type: AgentType
    priority: int = 1  # 1=low, 2=medium, 3=high
    context: Dict[str, Any] = None
    timeout: int = 300  # 5 minutes default
    callback: Optional[str] = None  # Callback function for completion

class AgentDelegate:
    """Analyze task characteristics to determine the best agent for execution"""
    def __init__(self):
        """Initialize the agent delegate"""
        pass

    def select_optimal_agent(self, task_description: str) -> AgentType:
        """
        Analyze task characteristics to determine the best agent for execution
        
        Args:
            task_description: Description of the task to be performed
            
        Returns:
            AgentType: The optimal agent type for the task
        """
        task_lower = task_description.lower()
        
        # Code-related tasks -> Codex
        code_keywords = [
            "code", "function", "class", "method", "variable", "algorithm",
            "debug", "fix", "implement", "refactor", "optimize", "test",
            "api", "database", "sql", "query", "script", "program",
            "python", "javascript", "typescript", "java", "cpp", "c#",
            "html", "css", "react", "vue", "angular", "node", "npm",
            "pip", "package", "library", "framework", "compile", "build"
        ]
        
        # Visual/UI tasks -> Claude Code
        visual_keywords = [
            "button", "click", "menu", "window", "dialog", "form", "input",
            "checkbox", "radio", "dropdown", "scroll", "drag", "drop",
            "hover", "tooltip", "popup", "modal", "tab", "panel",
            "sidebar", "toolbar", "icon", "image", "picture", "screenshot",
            "visual", "appearance", "layout", "position", "size", "color",
            "font", "text", "label", "caption", "tooltip", "notification"
        ]
        
        # Automation/workflow tasks -> OpenCode
        automation_keywords = [
            "automate", "workflow", "process", "pipeline", "batch", "schedule",
            "cron", "job", "task", "automation", "orchestration", "coordinate",
            "integrate", "connect", "api", "webhook", "trigger", "event",
            "monitor", "watch", "listen", "respond", "react", "pipeline"
        ]
        
        # General/coordination tasks -> Hermes
        general_keywords = [
            "coordinate", "manage", "organize", "plan", "schedule", "remember",
            "recall", "memory", "note", "log", "track", "monitor", "report",
            "analyze", "summarize", "explain", "describe", "document"
        ]
        
        # Score each agent type
        scores = {
            AgentType.CODEX: sum(1 for keyword in code_keywords if keyword in task_lower),
            AgentType.CLAUDE_CODE: sum(1 for keyword in visual_keywords if keyword in task_lower),
            AgentType.OPENER: sum(1 for keyword in automation_keywords if keyword in task_lower),
            AgentType.HERMES: sum(1 for keyword in general_keywords if keyword in task_lower)
        }
        
        # Additional heuristics
        if any(word in task_lower for word in ["file", "edit", "save", "open", "close"]):
            scores[AgentType.CODEX] += 2
        
        if any(word in task_lower for word in ["see", "look", "watch", "view", "display"]):
            scores[AgentType.CLAUDE_CODE] += 2
        
        if any(word in task_lower for word in ["automate", "repeat", "loop", "schedule"]):
            scores[AgentType.OPENER] += 2
        
        # Return the agent with highest score
        best_agent = max(scores, key=scores.get)
        return best_agent if max(scores.values()) > 0 else AgentType.HERMES

        
        # Code-related tasks -> Codex
        code_keywords = [
            'code', 'function', 'class', 'method', 'variable', 'algorithm',
            'debug', 'fix', 'implement', 'refactor', 'optimize', 'test',
            'api', 'database', 'sql', 'query', 'script', 'program',
            'python', 'javascript', 'typescript', 'java', 'cpp', 'c#',
            'html', 'css', 'react', 'vue', 'angular', 'node', 'npm',
            'pip', 'package', 'library', 'framework', 'compile', 'build'
        ]
        
        # Visual/UI tasks -> Claude Code
        visual_keywords = [
            'button', 'click', 'menu', 'window', 'dialog', 'form', 'input',
            'checkbox', 'radio', 'dropdown', 'scroll', 'drag', 'drop',
            'hover', 'hover', 'tooltip', 'popup', 'modal', 'tab', 'panel',
            'sidebar', 'toolbar', 'icon', 'image', 'picture', 'screenshot',
            'visual', 'appearance', 'layout', 'position', 'size', 'color',
            'font', 'text', 'label', 'caption', 'tooltip', 'notification'
        ]
        
        # Automation/workflow tasks -> OpenCode
        automation_keywords = [
            'automate', 'workflow', 'process', 'pipeline', 'batch', 'schedule',
            'cron', 'job', 'task', 'automation', 'orchestration', 'coordinate',
            'integrate', 'connect', 'api', 'webhook', 'trigger', 'event',
            'monitor', 'watch', 'listen', 'respond', 'react', 'pipeline'
        ]
        
        # General/coordination tasks -> Hermes
        general_keywords = [
            'coordinate', 'manage', 'organize', 'plan', 'schedule', 'remember',
            'recall', 'memory', 'note', 'log', 'track', 'monitor', 'report',
            'analyze', 'summarize', 'explain', 'describe', 'document'
        ]
        
        # Score each agent type
        scores = {
            AgentType.CODEX: sum(1 for keyword in code_keywords if keyword in task_lower),
            AgentType.CLAUDE_CODE: sum(1 for keyword in visual_keywords if keyword in task_lower),
            AgentType.OPENER: sum(1 for keyword in automation_keywords if keyword in task_lower),
            AgentType.HERMES: sum(1 for keyword in general_keywords if keyword in task_lower)
        }
        
        # Additional heuristics
        if any(word in task_lower for word in ['file', 'edit', 'save', 'open', 'close']):
            scores[AgentType.CODEX] += 2
            
        if any(word in task_lower for word in ['see', 'look', 'watch', 'view', 'display']):
            scores[AgentType.CLAUDE_CODE] += 2
            
        if any(word in task_lower for word in ['automate', 'repeat', 'loop', 'schedule']):
            scores[AgentType.OPENER] += 2
        
        # Return the agent with highest score
        best_agent = max(scores, key=scores.get)
        return best_agent if max(scores.values()) > 0 else AgentType.HERMES

    def execute_task_via_agent(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute a task using the specified AI agent
        
        Args:
            task: The AgentTask to execute
            
        Returns:
            Result dictionary with execution details
        """
        start_time = time.time()
        
        try:
            if task.agent_type == AgentType.CODEX:
                result = self._execute_via_codex(task)
            elif task.agent_type == AgentType.CLAUDE_CODE:
                result = self._execute_via_claude_code(task)
            elif task.agent_type == AgentType.OPENER:
                result = self._execute_via_opencode(task)
            else:  # HERMES
                result = self._execute_via_hermes(task)
                
            execution_time = time.time() - start_time
            result.update({
                "task_id": task.task_id,
                "agent_used": task.agent_type.value,
                "execution_time": execution_time,
                "timestamp": time.time()
            })
            
            return result
            
        except Exception as e:
            return {
                "task_id": task.task_id,
                "agent_used": task.agent_type.value,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "timestamp": time.time(),
                "success": False
            }

    def _execute_via_codex(self, task: AgentTask) -> Dict[str, Any]:
        """Execute task using OpenAI Codex CLI"""
        # Prepare the prompt for Codex
        prompt = f"""
        Task: {task.description}
        
        Context: {json.dumps(task.context or {}, indent=2)}
        
        Please execute this task using the Codex CLI. If this involves:
        - File modifications: Make the necessary changes
        - Code writing: Write clean, well-documented code
        - Debugging: Identify and fix issues
        - Testing: Create and run tests
        
        Work in the current directory and provide clear output about what was accomplished.
        """
        
        # In a real implementation, this would call the Codex CLI
        # For now, we'll simulate the execution
        try:
            # This is where we would actually call: codex exec "prompt"
            # For demonstration, we'll return a simulated result
            result = {
                "success": True,
                "output": f"Codex executed task: {task.description}",
                "files_modified": [],  # Would be populated with actual file changes
                "commands_run": [],    # Would be populated with actual commands
                "artifacts_created": [] # Would be populated with created files
            }
            
            # Log that we would use Codex here
            print(f"🤖 [Codex] Executing: {task.description[:50]}...")
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Codex execution failed: {str(e)}",
                "fallback_suggestion": "Consider using Claude Code for visual tasks or Hermès for coordination"
            }

    def _execute_via_claude_code(self, task: AgentTask) -> Dict[str, Any]:
        """Execute task using Claude Code CLI"""
        # Prepare the prompt for Claude Code
        prompt = f"""
        Task: {task.description}
        
        Context: {json.dumps(task.context or {}, indent=2)}
        
        Please use Claude Code to:
        1. Analyze any visual/UI elements if screenshots are involved
        2. Understand the context and requirements
        3. Execute the task with attention to visual details
        4. Provide feedback on what was observed and accomplished
        
        Focus on visual accuracy and user interface interactions.
        """
        
        try:
            # This is where we would actually call: claude-code --prompt "prompt"
            result = {
                "success": True,
                "output": f"Claude Code analyzed and executed: {task.description}",
                "visual_elements_processed": [],  # Would contain UI elements analyzed
                "screenshots_taken": [],          # Would contain screenshot references
                "ui_interactions": []             # Would contain button clicks, etc.
            }
            
            print(f"🎨 [Claude Code] Processing: {task.description[:50]}...")
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Claude Code execution failed: {str(e)}",
                "fallback_suggestion": "Consider using Codex for code tasks or Hermès for coordination"
            }

    def _execute_via_opencode(self, task: AgentTask) -> Dict[str, Any]:
        """Execute task using OpenCode CLI"""
        # Prepare the prompt for OpenCode
        prompt = f"""
        Task: {task.description}
        
        Context: {json.dumps(task.context or {}, indent=2)}
        
        Please use OpenCode to:
        1. Create automation scripts or workflows
        2. Set up scheduled tasks or monitoring
        3. Integrate different systems or services
        4. Create reusable components or templates
        
        Focus on automation, reproducibility, and system integration.
        """
        
        try:
            # This is where we would actually call: opencode --prompt "prompt"
            result = {
                "success": True,
                "output": f"OpenCode created automation for: {task.description}",
                "scripts_created": [],      # Would contain script file paths
                "workflows_defined": [],    # Would contain workflow descriptions
                "integrations_setup": []    # Would contain integration details
            }
            
            print(f"⚙️ [OpenCode] Automating: {task.description[:50]}...")
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenCode execution failed: {str(e)}",
                "fallback_suggestion": "Consider using Codex for code tasks or Claude Code for visual tasks"
            }

    def _execute_via_hermes(self, task: AgentTask) -> Dict[str, Any]:
        """Execute task using Hermes agent capabilities"""
        try:
            # This would use Hermes' native capabilities
            # For now, we'll simulate using available tools
            result = {
                "success": True,
                "output": f"Hermes coordinated: {task.description}",
                "actions_taken": [],      # Would contain Hermes tool usage
                "delegations_made": [],   # Would contain any sub-delegations
                "memory_updates": []      # Would contain memory storage operations
            }
            
            print(f"🧠 [Hermes] Coordinating: {task.description[:50]}...")
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Hermes execution failed: {str(e)}",
                "fallback_suggestion": "Consider breaking down the task into smaller components"
            }

    def execute_task_with_fallback(self, task: AgentTask, max_attempts: int = 3) -> Dict[str, Any]:
        """
        Execute a task with fallback to other agents if the primary choice fails
        
        Args:
            task: The AgentTask to execute
            max_attempts: Maximum number of attempts across different agents
            
        Returns:
            Result dictionary from the successful attempt
        """
        # Determine preferred order of agents
        agent_preference = self._get_agent_preference(task.description)
        
        last_error = None
        
        for attempt in range(min(max_attempts, len(agent_preference))):
            agent_type = agent_preference[attempt]
            
            # Create a copy of the task with the current agent type
            current_task = AgentTask(
                task_id=f"{task.task_id}_attempt_{attempt+1}",
                description=task.description,
                agent_type=agent_type,
                priority=task.priority,
                context=task.context,
                timeout=task.timeout
            )
            
            print(f"🔄 Attempt {attempt+1}/{max_attempts} using {agent_type.value}")
            
            result = self.execute_task_via_agent(current_task)
            
            if result.get("success", False):
                result["attempts_used"] = attempt + 1
                result["fallback_used"] = attempt > 0
                return result
            else:
                last_error = result.get("error", "Unknown error")
                print(f"❌ Attempt {attempt+1} failed: {last_error}")
                
                # If this isn't the last attempt, try the next agent
                if attempt < len(agent_preference) - 1:
                    continue
                else:
                    # All attempts failed
                    return {
                        "task_id": task.task_id,
                        "error": f"All {max_attempts} attempts failed. Last error: {last_error}",
                        "attempts_used": max_attempts,
                        "fallback_used": True,
                        "success": False,
                        "timestamp": time.time()
                    }

    def _get_agent_preference(self, task_description: str) -> List[AgentType]:
        """Get ordered list of agent preferences for a task"""
        primary_agent = self.select_optimal_agent(task_description)
        
        # Create a prioritized list based on the task type
        if primary_agent == AgentType.CODEX:
            return [AgentType.CODEX, AgentType.CLAUDE_CODE, AgentType.OPENER, AgentType.HERMES]
        elif primary_agent == AgentType.CLAUDE_CODE:
            return [AgentType.CLAUDE_CODE, AgentType.CODEX, AgentType.OPENER, AgentType.HERMES]
        elif primary_agent == AgentType.OPENER:
            return [AgentType.OPENER, AgentType.CODEX, AgentType.CLAUDE_CODE, AgentType.HERMES]
        else:  # HERMES
            return [AgentType.HERMES, AgentType.CODEX, AgentType.CLAUDE_CODE, AgentType.OPENER]

# Global orchestrator instance
agent_orchestrator = AgentDelegate()

def delegate_task_to_agent(
    description: str, 
    context: Dict[str, Any] = None,
    priority: int = 1,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Convenience function to delegate a task to the most appropriate AI agent
    
    Args:
        description: Description of the task to perform
        context: Additional context for the task
        priority: Priority level (1=low, 2=medium, 3=high)
        timeout: Timeout in seconds
        
    Returns:
        Result dictionary from the agent execution
    """
    task_id = f"task_{int(time.time())}_{hash(description) % 10000:04d}"
    
    task = AgentTask(
        task_id=task_id,
        description=description,
        agent_type=AgentType.HERMES,  # Will be overridden by selection logic
        priority=priority,
        context=context,
        timeout=timeout
    )
    
    return agent_orchestrator.execute_task_with_fallback(task)

def execute_with_agent(
    agent_type: AgentType,
    description: str,
    context: Dict[str, Any] = None,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Execute a task using a specific agent type
    
    Args:
        agent_type: The type of agent to use
        description: Description of the task to perform
        context: Additional context for the task
        timeout: Timeout in seconds
        
    Returns:
        Result dictionary from the agent execution
    """
    task_id = f"task_{int(time.time())}_{hash(description) % 10000:04d}"
    
    task = AgentTask(
        task_id=task_id,
        description=description,
        agent_type=agent_type,
        priority=1,  # Default priority when specifying agent explicitly
        context=context,
        timeout=timeout
    )
    
    return agent_orchestrator.execute_task_via_agent(task)

# Example usage and testing
if __name__ == "__main__":
    print("AI Agent Orchestration Layer - Test Suite")
    print("=" * 50)
    
    # Test 1: Code-related task (should go to Codex)
    print("\n1. Testing code-related task...")
    code_result = delegate_task_to_agent(
        "Create a Python function that calculates Fibonacci numbers with memoization",
        context={"language": "python", "complexity": "medium"}
    )
    print(f"Code task result: {code_result.get('success', False)}")
    
    # Test 2: Visual/UI task (should go to Claude Code)
    print("\n2. Testing visual/UI task...")
    visual_result = delegate_task_to_agent(
        "Click the 'Submit' button in the form and verify the success message appears",
        context={"application": "web_form", "element_type": "button"}
    )
    print(f"Visual task result: {visual_result.get('success', False)}")
    
    # Test 3: Automation task (should go to OpenCode)
    print("\n3. Testing automation task...")
    auto_result = delegate_task_to_agent(
        "Set up a daily backup script that copies important files to cloud storage",
        context={"frequency": "daily", "destination": "cloud"}
    )
    print(f"Automation task result: {auto_result.get('success', False)}")
    
    # Test 4: Specific agent selection
    print("\n4. Testing specific agent selection...")
    specific_result = execute_with_agent(
        AgentType.CODEX,
        "Refactor this JavaScript code to use ES6 arrow functions",
        context={"file": "utils.js", "style": "es6"}
    )
    print(f"Specific agent result: {specific_result.get('success', False)}")
    
    print("\n✓ Agent orchestration layer initialized successfully")