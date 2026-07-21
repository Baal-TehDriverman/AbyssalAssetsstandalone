# Comprehensive Computer Use Integration Documentation
# Interactive Examples and Demonstrations

This document provides executable examples demonstrating the full integration of the Computer Use skill with:
- Hermes Core Skills
- AI Agents (Codex, Claude Code, OpenCode)  
- External Tools and Systems
- Kairos-Dream for generative ideation
- All enhanced subsystems built during this development cycle

## Table of Contents
1. [System Overview](#system-overview)
2. [Getting Started](#getting-started)
3. [Interactive Examples](#interactive-examples)
   - [Example 1: Basic Computer Interaction](#example-1-basic-computer-interaction)
   - [Example 2: Context-Aware Automation](#example-2-context-aware-automation)
   - [Example 3: AI Agent Delegation](#example-3-ai-agent-delegation)
   - [Example 4: Cross-Platform Automation](#example-4-cross-platform-automation)
   - [Example 5: Adaptive Skill Loading](#example-5-adaptive-skill-loading)
   - [Example 6: Secure Sandboxing](#example-6-secure-sandboxing)
   - [Example 7: Vision Processing Enhancement](#example-7-vision-processing-enhancement)
   - [Example 8: Kairos-Dream Ideation](#example-8-kairos-dream-ideation)
4. [Advanced Integration Patterns](#advanced-integration-patterns)
5. [Troubleshooting and Best Practices](#troubleshooting-and-best-practices)

## System Overview

The enhanced Computer Use system provides a robust, intelligent automation platform that combines:

- **Reliable GUI Interaction**: Enhanced computer_use wrapper with retries, fallbacks, and caching
- **Context Awareness**: Real-time system monitoring via VM AI Gateway (port 8080)
- **Intelligent Delegation**: Task routing to specialized AI agents (Codex, Claude, OpenCode)
- **Cross-Platform Sync**: Bidirectional communication with Windows VM (port 8081)
- **Adaptive Skills**: Dynamic loading/unloading of Hermes skills based on context and resources
- **Enhanced Vision**: Temporal coherence, object permanence, and gaze prediction
- **Secure Execution**: AppArmor/seccomp sandboxing with audit logging
- **Memory Integration**: Bidirectional memory hooks for learning and correction
- **Exploration Strategies**: Antigravity-ingestion-bridge inspired novelty-seeking behavior
- **Creative Ideation**: Kairos-Dream integration for generative problem solving

## Getting Started

Before running the examples, ensure the following prerequisites are met:

1. **Hermes Agent** is installed and running
2. **cua-driver** is installed and running (`hermes computer-use install`)
3. **Firefox or Chromium** is available for web automation
4. **Windows VM** (optional) is accessible for cross-platform examples
5. **Lilith Gateway** is running on port 8080
6. **Windows Port Console** listener is running on port 8081 (for cross-platform examples)

### Verification Commands

Run these to verify your setup: