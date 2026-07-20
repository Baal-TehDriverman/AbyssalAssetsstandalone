# Himalaya Email Swarm

AI-driven email processing pipeline using `himalaya` CLI, synthesized from `himalaya_swarm_pipeline.py`, `himalaya_daemon.py`, `himalaya_pipeline.py`, `run_himalaya_pipeline.ps1`.

## Pipeline

```
Inbox → Filter → Categorize → Route → Response Draft → Queue
                 ↑                            │
             Swarm Agents                Human Review
```

## Processing Flow

1. **Fetch**: `himalaya list` new messages since last check
2. **Filter**: Rule-based + AI pre-filter (known senders, spam patterns)
3. **Categorize**: Swarm agent assigns category:
   - `action_required` → route to task system
   - `information` → summarize and file
   - `legal` → route to Palantir/RICO evidence
   - `financial` → route to ledger/business analytics
   - `personal` → route to Lyra dialogue
   - `spam` → silent discard
4. **Route**: Dispatch to appropriate agent/system
5. **Draft**: AI generates response draft using contextual memory
6. **Queue**: Human-in-the-loop review before sending

## Swarm Agents

| Agent | Role |
|-------|------|
| Email Scanner | Fetch and filter |
| Classifier | Categorize by content/context |
| Drafter | Generate response drafts |
| Legal Scribe | Extract legal/palantir content |
| Ledger Clerk | Parse financial data |
| Archivist | File and reference |

## Dependencies

- `himalaya` CLI (requires `sudo pacman -S himalaya`)
- IMAP/SMTP credentials in `.env`:
  ```
  EMAIL_IMAP_SERVER=imap.gmail.com
  EMAIL_IMAP_PORT=993
  EMAIL_SMTP_SERVER=smtp.gmail.com
  EMAIL_SMTP_PORT=587
  EMAIL_ADDRESS=your@email.com
  EMAIL_PASSWORD=your-app-password
  ```

## Daemon Mode

`himalaya_daemon.py` runs as a systemd user service:
- Check interval: 300s (configurable)
- Rate limit: 30 checks per 15 min (Gmail limit)
- Lock file prevents concurrent runs
- Logs to `runtime/himalaya/daemon.log`
