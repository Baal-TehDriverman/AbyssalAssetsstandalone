# AI System Improvement Report

Generated for the local AI/cerebellum improvement loop.

## Current System Evidence

- OS: Garuda Linux, Arch-like rolling distro.
- Kernel observed: `7.0.12-zen1-1-zen`.
- CPU: AMD Ryzen 5 5600H, 6 cores / 12 threads.
- RAM: 62 GiB total, about 54 GiB available during audit.
- Swap: 130 GiB zram, unused during audit.
- Storage: root on encrypted Btrfs, 409 GiB filesystem with about 282 GiB available; additional Samsung 990 EVO 2 TB device is present but not mounted.
- GPU: RTX 3060 Laptop GPU, 6 GiB VRAM. Real `nvidia-smi` showed driver `610.43.02`, CUDA UMD `13.3`, about 4.7 GiB VRAM used by Ollama `llama-server`.
- Himalaya: installed at `v1.2.0`; account doctor passes with real network access.
- Running AI services include Lilith API, Lyra API, Hermes Bridge/Gateway, MSN Router, NGD, NGD Cerebellum, Cyberpunk NGD bridge, God Engine, Antigravity Bridge, Swarm Orchestrator, and Quantum Terminal.

## Current Hot Findings

1. Ollama is actively using most of the 6 GiB GPU VRAM.
   - Keep local models quantized and context-bounded.
   - Avoid launching a second GPU-heavy local model while Cyberpunk is running.
   - `gpu_vram_policy.py` reported `red` when Ollama held about 4.7 GiB VRAM and only about 1.1 GiB remained free.
   - The latest full audit recorded `yellow`: about 2.8 GiB Ollama VRAM and about 2.9 GiB free.

2. A generated improvement database exists at `~/Desktop/AI/Pub/_mill_.db`.
   - Observed size: about 631 MiB.
   - Treat it as generated bulk data, not source code.
   - Prefer compact manifests and queryable indexes over millions of repetitive rows.

3. `systemctl --user` shows the AI stack is already running.
   - Add health/readiness gates before starting duplicate services.
   - Prefer status checks and circuit breakers over blind restarts.
   - `ai_service_health_gate.py` currently reports all 12 expected local AI services active.
   - `launch_gtc.sh` now prints service/GPU gate status before starting services.
   - `launch_nssp.sh` now checks ports non-destructively and only kills existing processes when `NSSP_KILL_EXISTING=1`.

4. `nvidia-smi` fails inside the sandbox but works unsandboxed.
   - Agent scripts should treat GPU telemetry as optional and report capability status explicitly.
   - NGD/cerebellum services should keep using real host telemetry when available.

5. The local GTC cerebellum is organized and verified.
   - Use `scripts/bootstrap_gtc_cerebellum.sh`.
   - Use `scripts/verify_gtc_cerebellum.py`.
   - Use `scripts/gtc_context_lookup.sh <term>`.
   - Use `scripts/reconcile_gtc_deployment.py` for dry-run/staged mod deployment.

## AI Breakthroughs To Apply

Public sources checked on June 19, 2026:

- OpenAI News lists recent work on near-autonomous AI chemistry, LifeSciBench, and pre-release behavior prediction by simulating deployment.
- Anthropic News lists Claude Opus 4.8 with stronger coding/agentic work and policy work on rapidly advancing AI.
- Google DeepMind highlights Gemini agent systems, multi-agent safety research, DiffusionGemma faster text generation, Genie interactive worlds, Gemini Robotics, and AlphaEvolve algorithm design.
- NVIDIA technical materials remain relevant for local inference: bounded VRAM, Flash Attention, batching, quantization, and telemetry-aware routing.

Refresh on June 19, 2026:

- Google DeepMind's current news page emphasizes AI-agent safety, multi-agent safety research, DiffusionGemma faster generation, Gemma 4 12B, Gemini for Science, and Antigravity-style agentic development.
- NVIDIA's developer blog emphasizes agentic coding benchmarks, long-context agent workflows, DiffusionGemma on NVIDIA hardware, Nemotron 3 Ultra for long-running agents, and on-device game agents.
- Local application made in this pass: `SYSTEM_AI_AUDIT.json` now includes a structured `summary` so agents can reason from parsed host/service/GPU state instead of scraping raw command logs.
- Local application made in this pass: `scripts/render_system_ai_report.py` writes `SYSTEM_AI_AUDIT_SUMMARY.md`, giving planner/executor/verifier agents a shared compact state artifact before launch or deployment work.
- Local application made in this pass: `AGENTS.md` now points agents at the generated audit summary before GTC launch/deploy decisions.
- Local application made in this pass: `scripts/ai_failure_triage.py` provides read-only service journal and endpoint failure triage so agents investigate first and restart only targeted failed services.

Code-level applications:

1. Add deployment simulation before real changes.
   - Already started with `GTC_DEPLOYMENT_PLAN.json` and dry-run reconciliation.

2. Add readiness/eval gates.
   - Already started with `verify_gtc_cerebellum.py`.
   - Extend the pattern to Lilith/Hermes/MSN services.

3. Prefer agentic workflows with bounded state.
   - Keep RAM context indexes compact and regenerate them.
   - Use persistent fallback mirrors for sandboxed agents.

4. Use multi-agent safety ideas locally.
   - Separate planner, executor, verifier, and rollback roles.
   - Never let the same step both decide and apply Steam mod writes without a dry-run artifact.

5. Apply faster local generation practices.
   - Keep Ollama context windows no larger than needed.
   - Use batch-friendly prompts.
   - Preserve VRAM headroom for Cyberpunk and desktop compositor.

## First 25 Practical Improvements

1. Keep `runtime/` ignored so generated cerebellum mirrors do not pollute commits.
2. Use `scripts/system_ai_audit.py` before major PC/code optimization passes.
3. Use `scripts/verify_gtc_cerebellum.py` after every GTC bootstrap.
4. Treat `~/Desktop/AI` as source and Steam Cyberpunk paths as deploy targets.
5. Use `GTC_DEPLOYMENT_PLAN.md` before any mod copy.
6. Use `reconcile_gtc_deployment.py` dry-run before staging or applying.
7. Require `--apply --yes` for real Steam writes.
8. Keep generated million-row databases out of source control.
9. Add health checks before restarting running AI services.
10. Avoid duplicate NGD/cerebellum drivers unless explicitly needed.
11. Track GPU telemetry and fall back gracefully if `nvidia-smi` is unavailable.
12. Cap local model concurrency when Cyberpunk is running.
13. Reserve VRAM headroom for the compositor and game.
14. Prefer compact JSON/TSV indexes in RAM over broad filesystem scans.
15. Keep persistent fallback context for sandboxed agents.
16. Make every agent read `AGENTS.md` and `GTC_CONTEXT.md` first.
17. Keep deployment drift visible as counts and file lists.
18. Add validation reports instead of claiming success from exit code alone.
19. Use source-to-target path maps for redscript deployment differences.
20. Prefer staged deployment directories for review.
21. Keep Himalaya checks read-only unless sending mail is explicitly requested.
22. Use primary AI sources for breakthrough tracking.
23. Record breakthrough-to-code mappings in this report.
24. Re-run audit after driver/model/service changes.
25. Convert repeated manual checks into scripts with JSON output.
26. Run `gpu_vram_policy.py` before loading another local model.
27. Run `ai_service_health_gate.py` before starting or restarting the AI stack.
28. Launch scripts should print gate status before starting services.
29. Launch scripts should skip duplicate foreground starts when ports are already active.
30. Port killing must be explicit and opt-in.
31. Check HTTP endpoints after service checks; active systemd units can still expose broken APIs.
32. Treat Lyra endpoint failures as degraded mode while Lilith/Hermes/MSN remain available; investigate Lyra separately before dialogue work.
33. Use `ollama_vram_guard.py` to inspect Ollama models before unloading or restarting Ollama.

## Commands

```bash
./scripts/system_ai_audit.py
python3 scripts/render_system_ai_report.py
./scripts/gpu_vram_policy.py
./scripts/ollama_vram_guard.py
./scripts/ai_service_health_gate.py
./scripts/ai_endpoint_health_gate.py
./scripts/ai_failure_triage.py
./scripts/bootstrap_gtc_cerebellum.sh
./scripts/verify_gtc_cerebellum.py
./scripts/gtc_context_lookup.sh msn_cerebellum
./scripts/reconcile_gtc_deployment.py --plan-name primary_mod_source_to_installed_msn_integration --limit 3
```
