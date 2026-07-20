# System AI Audit Summary

- Generated: `2026-06-19T16:33:27.563433+00:00`
- Host: `tehlappy-a5k1`
- Platform: `Linux-7.0.12-zen1-1-zen-x86_64-with-glibc2.43`
- CPU: `AMD Ryzen 5 5600H with Radeon Graphics`
- RAM: `62Gi` total, `54Gi` available
- Swap: `130Gi` total, `0B` used
- Running user services: `46`

## Current Gates

- GPU/VRAM policy: `red`; free `1104` MiB; after reserve `-944` MiB
- AI services: ok=`True`, running `12/12`
- Endpoints: ok=`True`, required failures `0`, optional failures `4`
- GTC cerebellum: ok=`True`, RAM available=`False`

## Findings

- GPU VRAM policy is red: 1104 MiB free, -944 MiB after Cyberpunk/desktop reserve.
- AI service gate: 12/12 expected services running.
- Endpoint gate: 10 endpoints checked; required failures=0.
- GTC cerebellum verification ok=True; ram_available=False.
- Samsung 990 EVO 2TB appears present but unmounted.
- Ollama loaded models: hermes3:8b.

## Recommendations

- Unload or downshift Ollama before launching Cyberpunk or another GPU-heavy local model.
- Mount the Samsung 990 EVO as a large asset/model workspace after deciding mountpoint and filesystem policy.

## Source Artifacts

- JSON audit: `SYSTEM_AI_AUDIT.json`
- GTC context: `GTC_CONTEXT_INDEX.json`
- GTC deployment plan: `GTC_DEPLOYMENT_PLAN.md`
- Persistent local cerebellum: `runtime/gtc_cerebellum/AGENT_README.md`
