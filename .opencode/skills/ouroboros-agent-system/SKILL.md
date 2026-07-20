# Ouroboros Agent System

A 10-agent parallel delegation framework synthesized from `swarm-agents.json`, `ouroboros_agent_orchestrator.py`, and all `swarm_*.ps1` files.

## Agent Roster

| ID | Role | Trigger |
|----|------|---------|
| agent-01 | Manuscript Elevation | creative/manuscript writing |
| agent-02 | Code and Architecture | implementation, refactoring |
| agent-03 | Memory and Synthesis | consolidation, query |
| agent-04 | Research and Ingestion | investigation, data gathering |
| agent-05 | Red-Teaming and Chaos | adversarial validation |
| agent-06 | Monitoring and Convergence | progress tracking, coherence |
| agent-07 | Skill Generation | new capability synthesis |
| agent-08 | Bridge and Infrastructure | connectivity, deployment |
| agent-09 | Narrative Coherence | narrative, documentation |
| agent-10 | Sovereign Core | executive decisions, orchestration |

## Deployment Patterns

### Wave Deployment
Agents launch in parallel phases:
- **Wave 1 (Nigredo→Albedo)**: agents 1-5, max 5 concurrent
- **Wave 2 (Citrinitas→Rubedo)**: agents 6-10, max 5 concurrent
- Each agent is a background job feeding into a shared state

### Queue Management
- Each agent has an inbox/outbox at `runtime/swarm/{agent_id}/`
- Backpressure limit: default 3 queued tasks
- Circuit breaker: 3 failures → 300s cooldown
- Task timeout: 300s default

### Routing
- Light tasks (<12k tokens): direct local execution
- Heavy tasks (≥12k tokens): route through swarm orchestrator

## Swarm Orchestrator API
```
start     — Launch agents as background processes
stop      — Terminate agent processes  
assign    — Assign task to agent inbox
status    — Query agent state (pid, queue depth, route)
coherence — Aggregate swarm health (alive, idle, working, queued)
```

## Coherence Formula
```
convergence = (alive/total) * 0.7 + ((idle + working)/total) * 0.3
```

## Adversarial Audit
Run `swarm_adversarial_audit.ps1` to validate:
- High-entropy prompt handling
- Timeout guard (60s default)
- Silent failure detection
- Empty output validation
