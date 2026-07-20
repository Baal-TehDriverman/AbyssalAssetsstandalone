# Antigravity Ingestion Bridge

Async ingestion pipeline with WebSocket reality feed, synthesized from the full `antigravity_bridge/` directory (`main.py`, `ag_client.py`, `ag_client_async.py`, `query_db.py`, `start_bridge.py`).

## Purpose

Streams data from multiple sources into a unified SQLite store with a WebSocket "reality feed" for real-time subscribers.

## Data Flow

```
Sources ──→ Ingestion API ──→ SQLite Store ──→ WebSocket Feed
  │                                                   │
  ├─ File drops                                  Subscribers
  ├─ HTTP POSTs                                   │
  ├─ Directory watches                      ┌──────┼──────┐
  └─ WebSocket clients                      │      │      │
                                        Lyra  Lilith  Swarm
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ingest` | Single data point (JSON body) |
| POST | `/ingest/batch` | Batch ingestion (JSON array) |
| GET | `/query` | Query stored data with filters |
| GET | `/health` | Bridge health check |
| WS | `/feed` | WebSocket reality feed subscription |

## Client Libraries

### Synchronous
```python
from antigravity_bridge import AntigravityClient
client = AntigravityClient("http://localhost:8002")
client.ingest({"type": "event", "data": {...}})
```

### Async
```python
from antigravity_bridge import AntigravityClientAsync
async with AntigravityClientAsync("http://localhost:8002") as c:
    await c.ingest_batch([item1, item2])
```

## Reality Feed (WebSocket)

Subscribers receive:
- `delta`: new data point with metadata
- `batch_complete`: batch processing notification
- `ping`: keepalive (30s interval)
- `error`: processing error

## Configuration

- `db_path`: SQLite database path
- `max_batch_size`: 1000 items per batch
- `ws_ping_interval`: 30 seconds
- `retention_days`: auto-prune data older than N days (0 = never)
- `rate_limit`: max requests per minute (default: 1000)
