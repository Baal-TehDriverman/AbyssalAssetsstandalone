# Hermes Skills for Abyssal Assets

This directory contains Hermes Agent skills that can be used on mobile devices via Hermes Agent on Android.

## Available Skills

### computer-use
Enhanced Computer Use system integrating cua-driver with Lilith ecosystem components for robust, intelligent GUI automation. Includes session management, AI agent orchestration, adaptive skill loading, and cross-platform synchronization.

**Location:** `computer-use/`

**Files:**
- `SKILL.md` - Main skill definition
- `scripts/` - Python scripts for enhanced computer use functionality
- `docs/` - Documentation and examples

## Usage on Hermes Mobile

To use these skills on Hermes Agent on your Android device:

1. The skills are automatically available when you sync this repository with Hermes
2. Load a skill using the `skill_view` tool or via the Hermes skill manager
3. The `computer_use` tool will be available for desktop automation

## Scripts Included

### Core Enhanced Computer Use
- `enhanced_computer_use.py` - Main enhanced computer use class with session management
- `simple_enhanced_cu.py` - Simplified wrapper for basic operations
- `working_enhanced_cu.py` - Working implementation with all features

### AI Integration
- `ai_agent_orchestration.py` - Delegate tasks to Codex, Claude Code, OpenCode
- `adaptive_skill_loader.py` - Dynamic skill loading based on context
- `vm_ai_gateway_integration.py` - VM AI Gateway (port 8080) integration

### Advanced Features
- `bidirectional_memory_hooks.py` - Memory hooks for self-correction
- `antigravity_exploration.py` - Exploration strategies to prevent rigidity
- `enhanced_vision_processing.py` - Advanced vision with temporal coherence
- `secure_sandboxing.py` / `secure_sandboxing_fixed.py` - Secure sandboxing

### Platform Integration
- `windows_port_console_sync.py` - Windows Port Console (port 8081) sync
- `github_automation_demo.py` - GitHub automation examples
- `demo_github_kairos.py` - Kairos integration demo

### Demos & Testing
- `demo_integrated.py` - Integrated demo
- `final_demo.py` - Final demonstration

## Setup

These skills are designed to work with the Hermes Agent on Garuda Linux and can be synced to mobile devices running Hermes Agent for Android.