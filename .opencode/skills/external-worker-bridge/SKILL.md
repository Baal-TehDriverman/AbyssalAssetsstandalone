# External Worker Bridge

Bring-your-own-model external inference integration, synthesized from `gpt_worker.py` and `grok_worker.py`.

## Supported Providers

| Provider | Worker Script | Auth Method |
|----------|--------------|-------------|
| OpenAI (GPT-4, o3, etc.) | `gpt_worker.py` | `OPENAI_API_KEY` env var |
| xAI (Grok) | `grok_worker.py` | `XAI_API_KEY` env var |
| Anthropic (Claude) | *(pattern ready)* | `ANTHROPIC_API_KEY` env var |
| Google (Gemini) | *(pattern ready)* | `GOOGLE_API_KEY` env var |
| Custom OpenAI-compatible | *(any worker)* | `CUSTOM_API_KEY` env var |

## Worker Pattern

```python
# Each worker follows this contract:
worker = Worker(api_key=os.environ["PROVIDER_API_KEY"])
response = worker.generate(
    prompt=str,
    system=str | None,
    temperature=float,
    max_tokens=int,
    model=str        # provider-specific model name
)
```

## Routing Logic

```
Request → Router → Available? → Rate Limited?
                      │              │
                    Yes              No
                      │              │
                  Dispatch       Queue/Retry
```

- Priority: local > openai > grok > anthropic > gemini
- Rate limit retry: exponential backoff (1s, 2s, 4s, 8s, max 30s)
- Fallthrough: if provider fails, try next in priority chain
- Circuit breaker: 3 consecutive failures → 5min cooldown

## Configuration

```env
OPENAI_API_KEY=sk-...
XAI_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
DEFAULT_PROVIDER=openai
WORKER_TIMEOUT=120
WORKER_RETRIES=3
```

## Use Cases

| Scenario | Recommended Provider |
|----------|---------------------|
| Code generation | GPT-4o, Claude 3.5 Sonnet |
| Creative writing | Claude 3.5, Grok |
| Analysis/reasoning | o3, Grok |
| Quick tasks | nemotron-mini (local) |
| Cost-sensitive | nemotron-mini (local) |
