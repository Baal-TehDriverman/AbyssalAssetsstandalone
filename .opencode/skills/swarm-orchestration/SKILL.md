# Swarm Orchestration

Multi-agent parallel execution system synthesized from `swarm_orchestrator.ps1`, `swarm_wave_manager.py`, `swarm_agents.json`, and all `swarm_worker.*` files.

## Architecture

```
                    ┌──────────────┐
                    │ Orchestrator  │
                    │  (dispatcher) │
                    └──┬───┬───┬───┘
              ┌────────┼───┼───┼────────┐
              │        │   │   │        │
         ┌────▼──┐ ┌──▼───▼───▼──┐ ┌───▼────┐
         │Agent 1│ │Agent 2 ... N│ │Sovereign│
         └───────┘ └─────────────┘ └────────┘
```

## Agent Definition (swarm-agents.json)

Each agent has:
- `id` — unique name
- `role` — functional description
- `trigger` — invocation pattern
- `deployment` — `"local"` or `"remote"`
- `model` — preferred model (e.g. `"nemotron-mini"`)

## Concurrency Control

| Parameter | Default | Description |
|-----------|---------|-------------|
| max_concurrent | 5 | Max agents running simultaneously |
| queue_depth | 3 | Max queued tasks per agent |
| timeout | 300s | Task timeout before kill |
| circuit_breaker | 3 | Failures before cooldown |
| cooldown | 300s | Circuit breaker pause |

## Process Lifecycle

```
IDLE → QUEUED → RUNNING → COMPLETED
                   │
                   └──→ FAILED → COOLDOWN → IDLE
```

## Wave Manager

`swarm_wave_manager.py` deploys agents in configurable waves:
- **Wave 0 (Nigredo)**: foundation agents (memory, research)
- **Wave 1 (Albedo)**: creative agents (manuscript, code, narrative)
- **Wave 2 (Citrinitas)**: synthesis agents (monitor, skillgen, bridge)
- **Wave 3 (Rubedo)**: sovereign convergence

## Backpressure

When queue_depth exceeds threshold, the orchestrator:
1. Halts new task assignment to overloaded agent
2. Redistributes to available peers
3. Logs overage to `runtime/swarm/overage.log`
4. Resumes when queue drops below threshold/2

## Health Monitoring

`/status` endpoint aggregates:
- `alive`: agents with active PID
- `idle`: alive agents with empty queue
- `working`: alive agents with active task
- `queued`: total pending tasks
- `convergence`: weighted health score (0.0–1.0)
