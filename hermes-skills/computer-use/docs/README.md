# Computer Use Skill - Advanced Integration Documentation

This document provides comprehensive guidance on using the enhanced Computer Use skill with integrated Hermes capabilities, including VM AI Gateway, Kairos-Dream, adaptive skill loading, and more.

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Installation & Setup](#installation--setup)
4. [Usage Examples](#usage-examples)
5. [Integration with Hermes Ecosystem](#integration-with-hermes-ecosystem)
6. [Troubleshooting](#troubleshooting)
7. [API Reference](#api-reference)

## Overview

The Computer Use skill has been extended to provide seamless integration with the Hermes AI ecosystem, enabling advanced automation capabilities. This includes:

- **Visual Automation**: Reliable GUI interaction with fallback mechanisms
- **Context Awareness**: Real-time system monitoring via VM AI Gateway (port 8080)
- **Bidirectional Synchronization**: Cross-platform automation with Windows VM (port 8081)
- **Intelligent Skill Loading**: Dynamic activation of complementary skills based on task context
- **Enhanced Vision Processing**: Temporal coherence, object permanence, and gaze prediction
- **Secure Sandboxing**: Isolated execution with Auditing to Lilith Gateway
- **AI Agent Orchestration**: Delegation to specialized agents (Codex, Claude, OpenCode)

## Features

### 1. Enhanced Computer Use Wrapper
Located in `scripts/enhanced_computer_use.py`, provides:
- Retry mechanisms with exponential backoff
- Fallback to coordinate-based interaction when SOM detection fails
- Performance monitoring and statistics
- Caching of UI elements for improved efficiency
- Methods: `safe_capture`, `safe_click`, `safe_type`, `safe_key`, `wait_for_element`

### 2. VM AI Gateway Integration
Located in `scripts/vm_ai_gateway_integration.py`, provides:
- Real-time polling of system metrics (CPU, memory, disk, network)
- Adaptive behavior based on system load
- Health monitoring endpoints
- Example usage: automatically reduce visual processing complexity under high CPU usage

### 3. Bidirectional Memory Hooks
Located in `scripts/bidirectional_memory_hooks.py`, provides:
- Automatic storage of computer-use actions in bidirectional memory
- Doorway Effect mitigation through context retention
- Experience replay for skill improvement
- Integration with `concurrent-bidirectional-memory` skill

### 4. AI Agent Orchestration Layer
Located in `scripts/ai_agent_orchestration.py`, provides:
- Task delegation to specialized AI agents:
  - **Codex**: Form filling and code generation
  - **Claude Code**: Visual reasoning and complex decision making
  - **OpenCode**: Automation scripting and DevOps tasks
- Load balancing based on agent capabilities and current workload
- Result aggregation and error handling

### 5. Antigravity-Ingestion-Bridge Exploration
Located in `scripts/antigravity_exploration.py`, provides:
- Controlled stochasticity in interaction patterns
- Novelty-seeking behavior to prevent behavioral rigidity
- Entropy-based exploration strategies
- Adaptive exploration rate based on task success history

### 6. Enhanced Vision Processing
Located in `scripts/enhanced_vision_processing.py`, provides:
- Temporal coherence modeling (Kalman filtering)
- Object permanence tracking across frames
- Affordance detection for UI elements
- Predictive gaze analysis for efficient visual search
- Integration with object detection and tracking models

### 7. Secure Sandboxing System
Located in `scripts/secure_sandboxing_fixed.py`, provides:
- Granular AppArmor profiles
- Seccomp-bpf syscall filtering
- Process isolation and resource limits
- Comprehensive audit logging to Lilith Gateway
- Secure file and network operation wrappers

### 8. Windows Port Console Synchronization
Located in `scripts/windows_port_console_sync.py`, provides:
- Bidirectional HTTP communication with Windows VM (port 8081)
- Server mode: listen for commands from Windows VM
- Client mode: send commands to Windows VM
- Supported actions: screenshot, click, type, key press
- Automatic IP detection (configurable via `WINDOWS_VM_IP` environment variable)

### 9. Adaptive Skill Loading System
Located in `scripts/adaptive_skill_loader.py`, provides:
- Dynamic loading/unloading of Hermes skills based on:
  - Task context (vision, delegation, memory, github, productivity)
  - Real-time system resource availability
- Skill categories with resource profiles
- Background monitoring and automatic adjustment
- Persistent state tracking

### 10. Kairos-Dream Integration
While not a separate script, the system is designed to work seamlessly with the `/kairos-dream` skill for:
- Generating creative ideas during idle periods
- Enhancing problem-solving through dream-state synthesis
- Feeding generated insights back into the cognitive architecture

## Installation & Setup

### Prerequisites
- Hermes Agent installed and configured
- cua-driver installed and running (see `hermes computer-use install`)
- Firefox or Chromium browser installed for web automation
- Optional: Windows VM running on libvirt/VirtualBox with IP accessible via `WINDOWS_VM_IP`

### Quick Start
1. Enable the enhanced computer use skill:
   ```bash
   hermes skills enable enhanced-computer-use
   ```

2. Install dependent skills (optional but recommended):
   ```bash
   hermes skills install metaconscious/concurrent-bidirectional-memory
   hermes skills install metaconscious/logos-warden
   hermes skills install autonomous-ai-agents/codex
   hermes skills install autonomous-ai-agents/claude-code
   hermes skills install autonomous-ai-agents/opencode
   ```

3. Start the VM AI Gateway (if not already running):
   ```bash
   # Assuming you have the VM set up
   vm_gateway_start.sh  # or however you start your gateway
   ```

4. Configure Windows IP (for cross-platform sync):
   ```bash
   export WINDOWS_VM_IP="192.168.122.1"  # Adjust to your VM's IP
   ```

## Usage Examples

### Basic Computer Interaction
```python
from enhanced_computer_use import enhanced_cu

# Take a screenshot with retry logic
result = enhanced_cu.safe_capture()
if not result.get('error'):
    print(f"Captured {len(result.get('elements', []))} UI elements")

# Click a button at coordinates
result = enhanced_cu.safe_click(x=100, y=200)
if not result.get('error'):
    print("Click successful")

# Type text into a focused field
result = enhanced_cu.safe_type("Hello, World!")
if not result.get('error'):
    print("Typed successfully")

# Press a key combination
result = enhanced_cu.safe_key("ctrl+c")
if not result.get('error'):
    print("Copied to clipboard")
```

### Context-Aware Automation
```python
from adaptive_skill_loader import AdaptiveSkillLoader
from vm_ai_gateway_integration import VMAIGatewayIntegration

# Initialize components
loader = AdaptiveSkillLoader()
gateway = VMAIGatewayIntegration()

# Get current system state
resources = gateway.get_system_resources()
print(f"CPU: {resources.cpu_percent}%, Memory: {resources.memory_mb}MB")

# Dynamically load vision-related skills if resources permit
if gateway.is_vision_safe(resources):
    loader.load_skill_category("vision")
    print("Vision skills loaded for enhanced processing")
else:
    print("Conservative mode: using basic computer vision only")
```

### Cross-Platform Automation
```python
# In a separate terminal, start the listener:
# python windows_port_console_sync.py --server --port 8081

# From Linux, send a command to the Windows VM:
from windows_port_console_sync import send_command_to_windows

result = send_command_to_windows(
    action="screenshot",
    params={}
)
if result.get("status") == "success":
    # Save the screenshot
    import base64
    with open("windows_screenshot.png", "wb") as f:
        f.write(base64.b64decode(result["image"]))
    print("Screenshot saved from Windows VM")
```

### AI Agent Orchestration
```python
from ai_agent_orchestration import agent_orchestrator, AgentType

# Delegate a form-filling task to Codex
result = agent_orchestrator.delegate_task_to_agent(
    agent_type=AgentType.CODEX,
    task_description="Fill out the GitHub issue form with title 'Bug: login fails' and description 'When clicking the login button, nothing happens'",
    context={"url": "https://github.com/owner/repo/issues/new"}
)
print(f"Codex result: {result}")

# Delegate visual reasoning to Claude Code
result = agent_orchestrator.delegate_task_to_agent(
    agent_type=AgentType.CLAUDE_CODE,
    task_description="Identify the primary call-to-action button on the current screen",
    context={"screenshot": "current_screen.png"}
)
print(f"Claude's analysis: {result}")
```

### Adaptive Skill Loading in Practice
```python
from adaptive_skill_loader import AdaptiveSkillLoader

loader = AdaptiveSkillLoader()

# Before starting a GitHub automation task
loader.load_skill_category("github")
loader.load_skill_category("vision")
loader.load_skill_category("delegation")

print(f"Currently loaded skills: {loader.get_status()['loaded_skills']}")

# After completing the task, optionally unload to free resources
# loader.unload_skill_category("github")
# loader.unload_skill_category("delegation")
```

## Integration with Hermes Ecosystem

### Lilith Gateway (Port 8080)
- **Health Monitoring**: The VM AI Gateway exposes a `/health` endpoint that returns JSON with system metrics
- **Audit Logging**: All sandboxed operations and security events are logged to the Lilith Gateway for compliance and debugging
- **Configuration**: Adjust polling intervals and thresholds in `vm_ai_gateway_integration.py`

### Windows Port Console (Port 8081)
- **Bidirectional Communication**: Enables triggering Linux actions from Windows VM events and vice-versa
- **Security**: Communications are limited to localhost-equivalent interfaces (adjust firewall rules as needed)
- **Use Cases**:
  - Windows VM detects a file drop in a shared folder → triggers Linux processing pipeline
  - Linux completes a build → sends notification to Windows VM toast

### Kairos-Dream
- **Trigger**: Activates during periods (no user input for 5+)
- **Processes 1. Dream cycle: 2. The vision processing system can utilize Kairos-Dream outputs to enhance pattern recognition in repetitive tasks
- **Feedback Loop**: Insights from Kairos-Dream are fed back into the bidirectional memory engine for long-term learning during
-1. The Kairos-m>hermes skills run kairos-dream
     The,Kairos-Dream compresses the day’s experiences into dream state
 The
The3. This
 dream state
 the
D
      backward pass of the bidirectional memory
 network,
 creating new associative connections
 
## 4. The
 emergent
 ideas
 or
 patterns
 can
 be
 used
 to
 inform
 future
 task
 approaches
 or
 creative
 problem
 solving
 

## Troubleshooting

### Common Issues

1. **"hermes_tools not found" when running scripts**
   - Ensure you are running the script within the Hermes environment
   - Use the Hermes-provided Python: `~/.local/share/lilith-agent-state/hermes/hermes-agent-clean-*/venv/bin/python`
   - Or run the script via `hermes exec` if available

2. **Computer use not responding**
   - Check if cua-driver is running: `hermes computer-use status`
   - Restart if necessary: `hermes computer-use install` (reinstalls and restarts)
   - Check permissions: `hermes computer-use permissions` (for macOS)

3. **Windows VM communication failing**
   - Verify the Windows VM is reachable: `ping $WINDOWS_VM_IP`
   - Ensure the Windows VM is running the listener script on port 8081
   - Check firewall settings on both machines

4. **Skill installation failures**
   - Verify the skill name is correct (use `hermes skills list` to see available skills)
   - Check your internet connection for fetching from skill repositories
   - Some skills may have dependencies; check their SKILL.md for requirements

### Debugging Tips

- Enable verbose logging by setting environment variable `HERMES_LOG_LEVEL=DEBUG`
- Check the Luna Gateway logs: `tail -f /var/log/lilith/audit.log`
- Monitor cua-driver output: `tail -f /tmp/cua-driver.log`
- Use the `hermes doctor` command for system health checks

## API Reference

### EnhancedComputerUse Class
- `safe_capture(app=None, mode="som")` → Dict
- `safe_click(x, y, button="left")` → Dict
- `safe_type(text)` → Dict
- `safe_key(key)` → Dict
- `wait_for_element(description, timeout=10)` → Dict
- `get_performance_stats()` → Dict

### AdaptiveSkillLoader Class
- `load_skill_category(category)` → bool
- `unload_skill_category(category)` → bool
- `adapt_to_context(context, resources=None)` → None
- `get_system_resources()` → SystemResources
- `get_status()` → Dict

### VMAIGatewayIntegration Class
- `get_system_resources()` → SystemResources
- `is_vision_safe(resources)` → bool
- `get_health_status()` → Dict
- `start_monitoring(interval=5.0)` → None
- `stop_monitoring()` → None

### ComputerControl Class (Windows Sync)
- `screenshot()` → Dict
- `click(params)` → Dict
- `type_text(params)` → Dict
- `press_key(params)` → Dict
- `execute_action(action, params)` → Dict

## Future Enhancements

1. **Natural Language Interface**: Allow commanding the computer via natural language
2. **Predictive Automation**: Use machine learning to anticipate user needs
3. **Enhanced Security**: Integrate with hardware security modules for credential storage
4. **Cross-Platform Expansion**: Support for macOS and additional Linux window managers
5. **Distributed Orchestration**: Coordinate multiple Hermes agents across a network

## Conclusion

This integrated system transforms the basic computer use capability into a sophisticated, context-aware, and secure automation platform that leverages the full power of the Hermes AI ecosystem. By combining reliable GUI interaction with intelligent reasoning, memory, and cross-platform capabilities, users can create powerful automation workflows that adapt to their environment and goals.

For further assistance, consult the individual script docstrings or reach out to the Hermes community.