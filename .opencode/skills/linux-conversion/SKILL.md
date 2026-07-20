---
name: linux-conversion
description: Use when migrating any Windows-specific code (.bat, .ps1, pwsh.exe, NSSM, hardcoded Windows paths) to Linux equivalents (bash scripts, systemd services, Linux paths). Covers patterns from the full Pub/Lilith ecosystem migration.
---

# Linux Conversion Patterns

## Migration from the Pub/Lilith Migration (268 files fixed)

### Paths
- **Windows**: `D:\pub`, `C:\Users\emhil\...`, `D:\pub\00_CORE_SERVICES`
- **Linux**: Use `PUB_ROOT` env var or `os.path.dirname(__file__)`
- Always use `pathlib.Path` or `os.path.join` — never string concatenation
- Centralize path resolution in a `lilith_paths.py` module

### Shell Scripts
- **Windows**: `.bat`, `.ps1`, `pwsh.exe -Command`, `pwsh.exe -File`
- **Linux**: `.sh` with `#!/bin/bash` shebang, or direct Python
- Never spawn `pwsh.exe` — use `bash` subprocess or Python subprocess
- Example: `subprocess.run(["bash", script])` instead of `subprocess.run(["pwsh", "-File", script])`

### Services
- **Windows**: NSSM (Non-Sucking Service Manager), Windows Task Scheduler
- **Linux**: systemd user services at `~/.config/systemd/user/<name>.service`
  - `Type=simple` for long-running servers
  - `Restart=on-failure` with `RestartSec=5`
  - `WorkingDirectory` set to the app directory
  - `Environment=` for configuration
  - Enable: `systemctl --user enable --now <name>.service`

### Python Virtual Environment
- **Windows**: `python -m venv .venv`, activate with `.venv\Scripts\activate`
- **Linux**: `python -m venv .venv`, activate with `source .venv/bin/activate`
- On Arch/Garuda: use `.venv-pub/` (not system python, PEP 668)
- Always specify full venv path in service files: `ExecStart=/path/to/.venv/bin/python3 script.py`

### Ollama
- **Windows**: Ollama runs as Windows service or manual `ollama serve`
- **Linux**: `systemctl is-active ollama` — system-level service
- Model paths are just model names, not file paths

### Fish Shell Launcher
- Functions in `~/.config/fish/functions/<name>.fish`
- Auto-loaded by Fish when first called
- Status checks via `systemctl --user is-active --quiet <service>`
- Color output: `set_color green/red/normal`
- REPL loops with `read -p 'echo "$prompt"' input` and `switch` statements

### File Watchers / Hot Reload
- **Windows**: PowerShell loops with `Get-Content -Wait`
- **Linux**: `inotifywait` (inotify-tools), or Node.js `chokidar`/`nodemon`

## For Abyssal Assets Specifically
- Server: Python FastAPI — already Linux-native
- Client: Phaser 3/Vite/TypeScript — already Linux-native
- Docker Compose for PostgreSQL — Linux-native
- No .bat/.ps1 in this project (clean)
- GDD mentions NSSM at line 35 — replace with systemd when deploying
