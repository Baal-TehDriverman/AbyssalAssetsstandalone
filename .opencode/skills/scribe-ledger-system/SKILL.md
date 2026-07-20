# Scribe Ledger System

Archival, migration, and emergency logging system synthesized from `scribe_write_ledger.py`, `scribe_dispatch_phase2.py`, `scribe_migrate_synthesis_assets.py`, `scribe_archive_emergency_log.py`, `ledger_relay.py`.

## Purpose

The Scribe is Lilith's long-term memory archivist. It writes structured ledger entries, migrates synthesis assets across state transitions, archives emergency logs, and relays critical state to downstream systems.

## Ledger Entry Format

```json
{
  "entry_id": "uuid",
  "timestamp": "ISO 8601",
  "type": "state_change | synthesis | emergency | relay",
  "domain": "swarm | memory | skill | narrative | legal",
  "payload": { ... },
  "checksum": "sha256",
  "previous_entry": "uuid"
}
```

Entries form a hash chain — each entry links to the previous, enabling tamper detection.

## Scribes

| Scribe | Function |
|--------|----------|
| Writer | Creates ledger entries from state transitions |
| Dispatcher | Routes entries to downstream consumers |
| Migrator | Migrates synthesis assets between state versions |
| Archiver | Archives and rotates emergency logs |
| Relay | Forwards critical entries to Palantir, RICO, etc. |

## Ledger Chain

```
Block 0 (genesis) ← Block 1 ← Block 2 ← ... ← Block N
    │                    hash chain integrity
checksum = sha256(prev_checksum + type + domain + payload)
```

Verification: recompute chain from genesis — any mismatch = tamper detected.

## Migration Protocol

When state schema changes:
1. Scribe Migrator reads all entries in old format
2. Transforms each entry to new schema
3. Writes transformed entries with new `schema_version`
4. Creates migration entry linking old and new chains
5. Archives old chain

## Emergency Archival

On critical events (crash, circuit break, security alert):
1. Scribe Archiver snapshots all runtime state
2. Writes to `runtime/scribe/emergency/{timestamp}/`
3. Creates emergency ledger entry
4. Relays to Palantir evidence system
5. Rotates old emergency logs (keep last 10)

## Configuration

- `ledger_path`: path to ledger database
- `archive_retention`: number of emergency snapshots (default: 10)
- `relay_endpoints`: list of downstream relay targets
- `migration_backup`: backup old chain before migration
- `auto_migrate`: automatically migrate on schema version mismatch
