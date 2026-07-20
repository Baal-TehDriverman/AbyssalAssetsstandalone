# NVIDIA Gratitude Driver (NGD)

GPU-aware AI routing engine synthesized from the full invite repo: `driver.py`, `state.py`, `gpu.py`, `governor.py`, `config.py`, `browser.py`, `term_events.py`, `slo.py`, `tracing.py`, `diagnostics.py`.

## Purpose

The Local Cerebellum of the Neural Sovereign Systems Platform (NSSP). Routes AI inference between local GPU (RTX 3060 6GB), hybrid, and cloud based on real-time telemetry.

## Hysteresis Router

Three-state routing with hysteresis to prevent flapping:

| State | Condition | Action |
|-------|-----------|--------|
| LOCAL_CEREBELLUM | model_vram + safety_margin < total_free | Run locally |
| HYBRID | Between clear and breach | Token budget, split |
| CLOUD_CORTEX | free < model_vram × 0.5 | Offload to cloud |

EWMA smoothing (α=0.22) on VRAM samples. Cooldown extends (does not reset) to prevent rapid cycling.

## GPU Telemetry

Dual-path sensor:
- **Primary**: NVML via `pynvml` (direct driver access)
- **Fallback**: `nvidia-smi` subprocess (CSV parsing, 3s timeout)
- Metrics: VRAM total/used/free, GPU util, mem util, temp, power

## Nemotron Prompt Governor

Quota-respecting prompt optimizer:
- SHA-256 prompt hashing with 30-day TTL cache
- Compression hints per size band (<4k, 4k-12k, >12k)
- Route-aware routing hints
- Renic: no account rotation, no rate limit bypass

## Chrome Coexistence

Aggregate-only Chrome telemetry: process count, working set, GPU/renderer counts. No URLs, cookies, or content.

## Prometheus & OpenTelemetry

- `/metrics` endpoint for Prometheus scraping
- OTLP export for traces and metrics
- Correlation ID propagation via ContextVar

## Configuration

Pydantic-based: YAML/TOML files, `NGD_` env vars, CLI overrides.
Configure: GPU index, VRAM thresholds, cooldown, EWMA alpha, runtime paths.

## Service Level Objectives

| Metric | Target |
|--------|--------|
| Telemetry availability | 99.9% |
| Latency P50 | 100ms |
| Latency P95 | 500ms |
| Latency P99 | 1s |
| Health endpoint | 99.99% |
