#!/usr/bin/env bash
# Refresh Grand Theft Cyberpunk indexes and prime RAM-backed local context.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INDEXER="$ROOT/scripts/index_gtc_context.py"
PRIMER="$ROOT/scripts/prime_gtc_ram_context.sh"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required for GTC context indexing" >&2
  exit 1
fi

AI_ROOT="$(dirname "$ROOT")" python3 "$INDEXER"
AI_ROOT="$ROOT" "$PRIMER"

RAM_ROOT="${GTC_RAM_CONTEXT_ROOT:-/dev/shm/gtc_cerebellum}"
PERSISTENT_ROOT="${GTC_PERSISTENT_CONTEXT_ROOT:-$ROOT/runtime/gtc_cerebellum}"

cat > "$RAM_ROOT/AGENT_README.md" <<EOF
# Grand Theft Cyberpunk Local Cerebellum

Start here for all GTC work.

Read order:

1. $ROOT/GTC_CONTEXT_INDEX.json
2. $ROOT/GTC_DEPLOYMENT_PLAN.md
3. $ROOT/GTC_CONTEXT.md
4. $RAM_ROOT/manifest.tsv
5. $RAM_ROOT/index/files.tsv
6. $RAM_ROOT/index/steam_cyberpunk_files.tsv

Rules:

- Desktop AI paths are source of truth.
- Steam Cyberpunk paths are deployment targets.
- Compare deployment drift before copying or editing installed mod files.
- Prefer RAM indexes for lookup; avoid broad home-directory scans.
- Use $ROOT/scripts/reconcile_gtc_deployment.py for dry-run or staged reconciliation.
- Real Steam writes require $ROOT/scripts/reconcile_gtc_deployment.py --apply --yes.

Key env:

- GTC_RAM_CONTEXT_ROOT=$RAM_ROOT
- GTC_RAM_REPO_ROOT=$RAM_ROOT/repos
- GTC_RAM_INDEX_ROOT=$RAM_ROOT/index
EOF

mkdir -p "$PERSISTENT_ROOT"
cp "$RAM_ROOT/AGENT_README.md" "$PERSISTENT_ROOT/AGENT_README.md"
cp "$ROOT/GTC_CONTEXT.md" "$PERSISTENT_ROOT/GTC_CONTEXT.md"
cp "$ROOT/GTC_CONTEXT_INDEX.json" "$PERSISTENT_ROOT/GTC_CONTEXT_INDEX.json"
cp "$ROOT/GTC_DEPLOYMENT_PLAN.json" "$PERSISTENT_ROOT/GTC_DEPLOYMENT_PLAN.json"
cp "$ROOT/GTC_DEPLOYMENT_PLAN.md" "$PERSISTENT_ROOT/GTC_DEPLOYMENT_PLAN.md"
cp "$RAM_ROOT/manifest.tsv" "$PERSISTENT_ROOT/manifest.tsv"
rm -rf "$PERSISTENT_ROOT/index"
cp -a "$RAM_ROOT/index" "$PERSISTENT_ROOT/index"

echo ""
echo "GTC local cerebellum ready"
echo "  readme:   $RAM_ROOT/AGENT_README.md"
echo "  fallback: $PERSISTENT_ROOT/AGENT_README.md"
echo "  context:  $ROOT/GTC_CONTEXT_INDEX.json"
echo "  deploy:   $ROOT/GTC_DEPLOYMENT_PLAN.json"
echo "  ram root: $RAM_ROOT"
