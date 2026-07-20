# Hermes MCP Bridge

FastMCP server bridging the Hermes skill ecosystem to modern MCP tools, synthesized from `hermes_mcp_server.py`.

## Protocol Mapping

| Hermes Concept | MCP Equivalent |
|----------------|---------------|
| Skill | Tool |
| Hermes Agent | Server |
| Skill Registry | Tool Registry |
| Marketplace | Package Manager |
| Codex Mode | Capability Flag |
| God Engine | Client Host |

## Tools Exposed

| Tool | Description |
|------|-------------|
| `skill_discover` | List all known skills by tag, mode, or path |
| `skill_inject` | Inject skill context into system prompt |
| `swarm_status` | Query swarm agent health and queue depth |
| `orchestrate_task` | Dispatch a task to the swarm |
| `memdir_read` | Read from file-based persistent memory |
| `memdir_write` | Write to file-based persistent memory |
| `telemetry_push` | Push metrics to NGD telemetry |
| `nvdia_smi_query` | Query GPU state via nvidia-smi |

## MCP Transport

- **Mode**: stdio (default for Claude Code / opencode integration)
- **Protocol**: JSON-RPC 2.0 over stdin/stdout
- **Server header**: `hermes-mcp-bridge/1.0`

## Configuration

- `SKILL_REGISTRY_PATH`: path to unified skill manifest
- `SWARM_RUNTIME_PATH`: path to swarm agent runtime state
- `MEMDIR_PATH`: path to memdir storage
- `NGD_TELEMETRY_PATH`: path to NGD telemetry log

## Integration with opencode

Register in `opencode.json`:
```json
"mcp_servers": {
  "hermes-bridge": {
    "command": "python",
    "args": ["scripts/hermes_mcp_server.py"]
  }
}
```

## Fallback Mode

If the full Hermes ecosystem is not available (no skill registry, no swarm runtime), the bridge operates in **standalone mode** with built-in in-memory skill definitions and no-op swarm stubs. This ensures it never fails to start.
