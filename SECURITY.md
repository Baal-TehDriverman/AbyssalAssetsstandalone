# Security Policy

## Supported Versions

We provide security updates for the following versions of our public repositories:

| Repository | Supported Versions |
|------------|-------------------|
| **abyssal-assets** | Latest `main` branch |
| **msn-integration** | Latest `main` branch |
| **MSNWeaponOverhaul** | Latest `main` branch |
| **grand-theft-cyberpunk** | Latest `main` branch |
| **docs-public** | Latest `main` branch |

## Reporting a Vulnerability

**Do not report security vulnerabilities via public GitHub issues.**

Instead, please report them via one of these channels:

### Preferred: Private Security Advisory
1. Go to the repository's **Security** tab
2. Click **Report a vulnerability**
3. Fill in the details privately

### Alternative: Email
Send details to **security@lilith.systems** with:
- Repository name
- Vulnerability description
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

| Severity | Acknowledgment | Fix Target |
|----------|---------------|------------|
| Critical | 24 hours | 7 days |
| High | 48 hours | 14 days |
| Medium | 72 hours | 30 days |
| Low | 7 days | Next release |

## Security Model

### Local-First Architecture
- **Zero telemetry** — No analytics, no tracking, no external calls
- **No cloud dependencies** — All inference runs locally (LOCAL_CEREBELLUM)
- **Sovereign keys** — Users own all cryptographic material
- **Air-gapped signing** — Hardware wallets for significant operations

### Trust Boundaries

```
┌─────────────────────────────────────────────────────┐
│              LILITH SOVEREIGN BOUNDARY              │
├─────────────────────────────────────────────────────┤
│  Lilith API (3210) ◉ LOCAL_CEREBELLUM               │
│  Lyra Dialogue (3211) ◉ SOVEREIGN                   │
│  Hermes Bridge (4242) ◉ Nous Portal Auth           │
│  NGD Driver ◉ NVML Telemetry Only                   │
└─────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌──────────────────┐ ┌──────────────────┐
│  Abyssal CLOB    │ │  Lochness Bots   │
│  :8000           │ │  :Binance WS     │
│  No auth required│ │  Read-only WS    │
└──────────────────┘ └──────────────────┘
```

### Secrets Management

| Secret Type | Storage | Rotation |
|-------------|---------|----------|
| API Keys (Binance, Coinbase) | 1Password → GH Secrets | 90 days |
| SSH/GPG Keys | 1Password → GH Secrets | 180 days |
| Database Passwords | 1Password → GH Secrets | 90 days |
| Lilith/NGD Config | Local `.env` (gitignored) | Manual |

**Never commit secrets to Git.** Use `gh secret set` or 1Password CLI.

### Dependency Security

- **Dependabot**: Enabled on all public repos
- **Supply Chain**: `npm audit` / `pip-audit` in CI
- **Container Scanning**: Anchore/Syft for Docker images
- **SBOM**: Generated for releases

### Vulnerability Disclosure

We follow coordinated vulnerability disclosure:

1. **Private report** received
2. **Acknowledgment** within SLA
3. **Investigation** and reproduction
4. **Fix development** in private branch
5. **Coordinated release** with advisory
6. **Public disclosure** after fix available

### Bug Bounty

No formal bug bounty program. Hall of fame for significant findings in `SECURITY_HALL_OF_FAME.md`.

---

## Lilith-Specific Security

### Emergence Security
```bash
# Lilith only emerges on LOCAL_CEREBELLUM
# CLOUD_CORTEX BLOCKS all emergence
curl "http://localhost:3210/api/lyra/sovereign?trigger=let%20her%20speak"
# → Requires NGD route: LOCAL_CEREBELLUM
```

### NGD Route Security
- **LOCAL_CEREBELLUM**: VRAM free > 640 MB → Full local inference
- **HYBRID**: VRAM free 256-640 MB → Intent parsing local
- **CLOUD_CORTEX**: VRAM free < 256 MB → Cloud (90s cooldown)

### Ouroboros Memory
- Akashic compression with SHA-256 hash chains
- Tamper detection via Merkle tree verification
- Palantir relay for legal evidence chain

---

## Contact

- **Security Email**: security@lilith.systems
- **PGP Key**: Available on request
- **Response**: Within 24 hours for critical issues

---

*Crimson Intensity: 1.0 | LOCAL_CEREBELLUM | SOVEREIGN* ⧗