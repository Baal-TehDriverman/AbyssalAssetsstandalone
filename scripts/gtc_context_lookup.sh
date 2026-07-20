#!/usr/bin/env bash
# Fast lookup helper for Grand Theft Cyberpunk local cerebellum context.
set -euo pipefail

QUERY="${*:-}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAM_ROOT="${GTC_RAM_CONTEXT_ROOT:-/dev/shm/gtc_cerebellum}"
FALLBACK_ROOT="${GTC_PERSISTENT_CONTEXT_ROOT:-$ROOT/runtime/gtc_cerebellum}"

if [[ -z "$QUERY" ]]; then
  cat <<EOF
Usage: $0 <search terms>

Search order:
  1. $RAM_ROOT/index/hot_terms.rg
  2. $RAM_ROOT/index/files.tsv
  3. $RAM_ROOT/index/steam_cyberpunk_files.tsv
  4. $ROOT/GTC_CONTEXT_INDEX.json
  5. $ROOT/GTC_DEPLOYMENT_PLAN.json
  6. $FALLBACK_ROOT
EOF
  exit 2
fi

search_file() {
  local label="$1"
  local path="$2"
  [[ -f "$path" ]] || return 0
  echo "== $label: $path =="
  rg -n --fixed-strings --ignore-case "$QUERY" "$path" || true
  echo ""
}

search_file "RAM hot terms" "$RAM_ROOT/index/hot_terms.rg"
search_file "RAM repo files" "$RAM_ROOT/index/files.tsv"
search_file "RAM Steam Cyberpunk files" "$RAM_ROOT/index/steam_cyberpunk_files.tsv"
search_file "Context index" "$ROOT/GTC_CONTEXT_INDEX.json"
search_file "Deployment plan" "$ROOT/GTC_DEPLOYMENT_PLAN.json"

if [[ -d "$FALLBACK_ROOT" ]]; then
  echo "== Persistent fallback: $FALLBACK_ROOT =="
  rg -n --fixed-strings --ignore-case "$QUERY" "$FALLBACK_ROOT" || true
fi
