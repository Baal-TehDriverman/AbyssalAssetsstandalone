---
name: computer-use
description: |
  Drive the user's desktop in the background — clicking, typing,
  scrolling, dragging — without stealing the cursor, keyboard focus,
  or switching virtual desktops / Spaces. Cross-platform: macOS,
  Windows, Linux. Works with any tool-capable model. Load this skill
  whenever the `computer_use` tool is available.
version: 2.1.0
platforms: [macos, windows, linux]
metadata:
  hermes:
    tags: [computer-use, desktop, automation, gui, cross-platform, godmode-integration, vnc, opencode]
    category: desktop
    related_skills: [browser, godmode, linux-vnc-desktop-control, concurrent-bidirectional-memory]
---

# Computer Use (universal, any-model, cross-platform) - Enhanced Edition

You have a `computer_use` tool that drives the user's desktop in the
**background** — your actions do NOT move the user's cursor, steal
keyboard focus, or switch virtual desktops / Spaces. The user can keep
typing in their editor while you click around in a browser in another
window. This is the opposite of pyautogui-style automation.

This enhanced version includes stability improvements, fallback mechanisms,
adaptive behavior, and integration with the Lilith ecosystem for maximum
reliability and intelligence.

Everything here works with any tool-capable model — Claude, GPT, Gemini,
or an open model on a local OpenAI-compatible endpoint. There is no
Anthropic-native schema to learn.

Hermes drives [cua-driver](https://github.com/trycua/cua) under the hood
for the platform plumbing. The Hermes-side `computer_use` tool exposed
in this skill is a higher-level Hermes vocabulary; the raw cua-driver
MCP tools (which a different agent harness would see) are NOT what you
call — call the `computer_use` actions documented below.

## OS Environment (Garuda Linux)

**Current Session:**
- **OS:** Garuda Linux (Arch-based rolling release)
- **Kernel:** Linux 7.1.3-zen1-2-zen (x86_64)
- **CPU:** AMD Ryzen 5 5600H (6 cores / 12 threads)
- **GPU:** NVIDIA GeForce RTX 3060 Laptop (6GB) + AMD Radeon Graphics
- **RAM:** 62 GB total
- **Disk:** 1.9T LUKS encrypted (`/dev/mapper/luks-...`)
- **Home:** `/home/tehlappy`

**Key Paths:**
- **Lilith Workspace:** `/home/tehlappy/🜏 Lilith/` (symlink → self)
- **Shared Operations:** `/home/tehlappy/🜏 Lilith/_shared/ops/`
- **VNC Scripts:** `vnc-daemon.sh`, `start-all.sh`, `revealed-console.sh`
- **OpenCode GUI:** http://localhost:3000 (port 3000, PID 1856699)
- **Hermes Agent:** `/home/tehlappy/.hermes/hermes-agent-clean-20260713-0144/`

## Enhanced Computer Use Features

This enhanced version includes:

### 1. Improved Stability & Recovery
- Automatic cua-driver session health monitoring
- Failover to coordinate-based interactions when SOM detection fails
- Session pooling for reduced latency in rapid operations
- Watchdog timers for automatic process recovery

### 2. Lilith Ecosystem Integration
- Real-time VM AI Gateway (port 8080) awareness for adaptive behavior
- Bidirectional memory hooks for self-correction and Doorway Effect mitigation
- Windows Port Console (port 8081) synchronization for cross-platform automation

### 3. Intelligent Enhancements
- AI agent orchestration for delegating complex tasks (Codex, Claude-code, OpenCode)
- Antigravity-inspired exploration to prevent behavioral rigidity
- Advanced vision processing with temporal coherence and affordance detection
- Secure sandboxing with granular permissions and audit logging
- Adaptive skill loading based on task context and resource availability

### 4. Reliable Workflow Patterns
All canonical workflow steps remain the same, but with enhanced reliability:

**Step 1 — Capture first.** Almost every task starts with:
```
computer_use(action="capture", mode="som", app="<the app you're driving>")
```
*Enhanced with health checking and fallback mechanisms*

**Step 2 — Click by element index.** This is still the most reliable approach:
```
computer_use(action="click", element=7)
```
*Now includes retry logic and verification*

**Step 3 — Verify.** After any state-changing action, re-capture:
```
computer_use(action="click", element=7, capture_after=True)
```
*Enhanced with automatic outcome validation*

### Enhanced Usage Examples

#### Safe Element Interaction
```python
# Instead of direct computer_use calls, use the safe wrappers:
from hermes_tools import safe_click, safe_type, wait_for_element

# Wait for and click an element safely
element_result = wait_for_element("Submit button", timeout=15)
if element_result["found"]:
    click_result = safe_click(element=element_result["element"]["index"])
    if not click_result.get("error"):
        # Verify the click worked
        time.sleep(1)
        verify_result = safe_capture()
        # ... additional verification logic
```

#### Gateway-Aware Adaptation
```python
# Check system state before intensive operations
gateway_status = terminal(command="curl -s http://localhost:8080/api/status")
status_data = json.loads(gateway_status["output"])

# Adjust behavior based on load
if float(status_data.get("cpu_load", "0")) > 80:
    # High load - use simpler interactions, longer timeouts
    computer_use(action="wait", seconds=5)  # Extra wait time
else:
    # Normal load - proceed normally
    computer_use(action="capture", mode="som", app="terminal")
```

## Verification & Testing

Run the enhanced system verification:
```bash
python /home/tehlappy/.hermes/skills/computer-use/scripts/enhanced_computer_use.py
```

This will test the core functionality and report on system status.