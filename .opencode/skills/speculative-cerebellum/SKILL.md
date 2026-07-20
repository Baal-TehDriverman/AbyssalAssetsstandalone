# Speculative Cerebellum

Bounded local prep + cloud reasoning pattern synthesized from `speculative_cerebellum.py`.

## Pattern

```
User Prompt → Local Speculation → Cloud Verification → Output
                  ↓
            Bounded context
            (≤4k tokens)
```

## How It Works

1. **Local speculation**: Ollama (nemotron-mini) generates a bounded initial response using partial context
2. **Cloud verification**: Rich model (Nemotron 3 Ultra / GPT / Claude) reviews, refines, or overrides
3. **Merge**: Local seed + cloud refinement → combined output
4. **Fallback**: If cloud unavailable, return best local speculation

## Use Cases

| Scenario | Local | Cloud |
|----------|-------|-------|
| Code generation | Skeleton, imports | Logic, edge cases |
| Creative writing | Outline, characters | Prose, dialogue |
| Analysis | Summary, data extraction | Deep insight, pattern finding |
| Debugging | Trace parsing | Root cause, fix |

## Configuration

- `local_model`: Ollama model name (default: nemotron-mini)
- `cloud_endpoint`: API endpoint for rich model
- `cloud_api_key`: From environment, never hardcoded
- `max_local_tokens`: 4096 (bounded by design)
- `temperature_local`: 0.3 for code, 0.7 for creative
- `temperature_cloud`: 0.1 for verification

## Circuit Breaker

- 3 consecutive cloud failures → local-only mode for 300s
- Health check on `/health` before each cloud call
- Timeout: 30s local, 60s cloud

## When to Use

- LLM inference optimization (cheap local + expensive cloud)
- Latency-sensitive tasks (local responds <1s)
- Privacy-sensitive data (keep on GPU, never send raw)
- Hybrid routing per NGD route state
