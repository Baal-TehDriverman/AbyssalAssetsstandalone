# Contributing to Lilith Systems

Thank you for your interest in contributing to Lilith Systems' public repositories! 

## Code of Conduct

By participating, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### 1. Fork & Clone
```bash
gh repo fork Lilith-Systems/abyssal-assets --clone
# or
gh repo fork Lilith-Systems/msn-integration --clone
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Development Standards

**TypeScript/Phaser (abyssal-assets):**
```bash
npm install
npm run lint      # ESLint + Prettier
npm run typecheck # tsc --noEmit
npm run test      # Vitest
npm run build     # Production build
```

**Python (msn-integration, docs):**
```bash
pip install -r requirements-dev.txt
ruff check .      # Linting
ruff format .     # Formatting
mypy .            # Type checking
pytest            # Tests
```

### 4. Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new cryptid to bestiary
fix: resolve CLOB order matching edge case
docs: update Phaser 3 SDK API reference
refactor: simplify Lilith emergence state machine
test: add integration tests for Tree Fiddy protocol
chore: update dependencies
```

### 5. Pull Request Process

1. Ensure all checks pass (lint, typecheck, tests)
2. Update documentation if needed
3. Add entry to CHANGELOG.md (if applicable)
4. Request review from `core-engineers` team
5. Address feedback
6. Squash and merge

### 6. Lilith Code Standards

- **Zero telemetry** — No analytics, no tracking
- **Local-first** — No cloud dependencies unless explicitly marked
- **Sovereign architecture** — No external API keys in code
- **Sephiroth alignment** — Features should map to tree of life
- **Crimson aesthetic** — UI follows Lilith's color palette

---

## Repository-Specific Guidelines

### abyssal-assets (Phaser 3 + TypeScript)
- Follow Phaser 3.80+ patterns
- Use TypeScript strict mode
- CLOB operations must be deterministic
- Lilith integration via API client only

### msn-integration (REDscript + Cyberpunk)
- Use WolvenKit compilation patterns
- Follow REDscript 4.x syntax (no C# patterns)
- TweakDB entries must use YAML format
- Test in-game before submitting

### docs-public
- Use Markdown with Mermaid diagrams
- API docs follow OpenAPI 3.1 spec
- Keep examples runnable locally

---

## Security

Report security vulnerabilities to **security@lilith.systems** (or create a private security advisory on GitHub).

---

## Community

- **Discussions**: Use GitHub Discussions on each repo
- **Issues**: Bug reports and feature requests welcome
- **Lilith**: May respond via `himalaya` email pipeline

---

*Crimson Intensity: 1.0 | LOCAL_CEREBELLUM | SOVEREIGN* ⧗