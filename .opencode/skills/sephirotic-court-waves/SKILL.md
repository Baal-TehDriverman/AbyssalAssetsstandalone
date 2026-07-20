# Sephirotic Court Waves

Wave-based Sephirotic deployment framework synthesized from `run_sephirotic_court_waves.ps1` (137 lines, 2-wave 7-agent deployment).

## Court Members

| Agent | Title | Wave |
|-------|-------|------|
| Nyx | Archon 0: Origin | 1 |
| Abraxas | Archon 1 | 1 |
| Thoth | Archon 2 | 1 |
| Baal | Archon 3 | 1 |
| Lucifer | Archon 4: Adversary | 1 |
| Yeshua | Archon 5 | 2 |
| Legion | Daemon | 2 |

## Wave Deployment

### Wave 1 (Nigredo → Albedo)
Launches Archons 0-4 simultaneously. Each Archon:
1. Validates its `runtime/{agent_id}/` directory exists
2. Loads configuration from `config/court-{agent_id}.json`
3. Registers with the central court endpoint
4. Reports ready status to orchestration log

### Wave 2 (Citrinitas → Rubedo)
Launches Archons 5-6 after Wave 1 stabilizes:
1. Yeshua reconciles Archon states
2. Legion daemon sweeps orphans and stale processes

## Court Rendezvous

All Archons report to `runtime/sephirotic-court/registry.json`:
```json
{
  "{agent_id}": {
    "pid": 12345,
    "status": "alive|halted",
    "started_at": "ISO8601",
    "last_seen": "ISO8601"
  }
}
```

## Orchestration Log

`runtime/sephirotic-court/ouroboros_wave.log` records:
- Wave start/completion timestamps
- Each agent's launch result (pid or error)
- Convergence check results
- Cleanup operations

## Coherence Check

After each wave, the court validates:
1. All expected agents are alive (PID exists)
2. Registry file is consistent
3. No orphan processes from previous runs
4. Log files are writable

## Cleanup

`stop_sephirotic_court.ps1`:
1. Reads registry for all PIDs
2. Kills each process (SIGTERM, then SIGKILL after 5s)
3. Removes socket/lock files
4. Clears registry
