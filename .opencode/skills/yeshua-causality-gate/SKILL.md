# Yeshua Causality Gate

State reconciliation and causality enforcement system synthesized from `yeshua_gate.py`, `yeshua_reaper.py`, and the court wave 2 Yeshua agents.

## Purpose

Ensures causal consistency across distributed agent states. Yeshua reconciles diverged state forks, the Reaper sweeps orphans, and the Gate blocks causally invalid operations.

## Components

### Yeshua Gate
- Detects state forks across agent runtime directories
- Computes causal merge using last-written-wins with timestamp ordering
- Validates preconditions before allowing state transitions
- Logs every reconciliation to `runtime/yeshua/gate.log`

### Yeshua Reaper
- Periodically scans PID directories for dead/orphan processes
- Cleans up stale `.lock` files, `.pid` files, and FIFO sockets
- Reports reaped processes to the gate for state cleanup
- Safety: never kills processes with parent PID 1 (init)

### Causality Protocol

```
agent-A: assert(state_X) → Gate: validate(preconditions)
  → valid:   state_X committed, timestamp logged
  → invalid: state_X rejected, agent notified with causal error
```

State transitions must specify:
- `from_state`: previous state hash
- `to_state`: proposed state hash
- `preconditions`: list of (key, expected_value) tuples
- `timestamp`: ISO 8601 with microsecond precision

## Use Cases

| Scenario | Action |
|----------|--------|
| Two agents write same key | Gate picks latest timestamp |
| Agent restarts with stale state | Gate replays missing transitions |
| Orphan process after crash | Reaper sweeps within 60s |
| State invariant violated | Gate blocks with causal error |

## Configuration

- `scan_interval`: reaper sweep interval (default: 60s)
- `state_dir`: runtime state directory
- `max_fork_depth`: max versions before forced merge (default: 10)
- `reaper_safety`: skip processes with parent PID 1 (default: true)
- `gate_log`: path to reconciliation log
