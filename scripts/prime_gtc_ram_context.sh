#!/usr/bin/env bash
# Prime Grand Theft Cyberpunk repo context into RAM-backed storage.
set -euo pipefail

AI_ROOT="${AI_ROOT:-$HOME/Desktop/AI}"
STEAM_CYBERPUNK_ROOT="${STEAM_CYBERPUNK_ROOT:-$HOME/.local/share/Steam/steamapps/common/Cyberpunk 2077}"
RAM_ROOT="${GTC_RAM_CONTEXT_ROOT:-/dev/shm/gtc_cerebellum}"
SNAPSHOT_ROOT="$RAM_ROOT/repos"
EXTRA_ROOT="$RAM_ROOT/extra"
INDEX_ROOT="$RAM_ROOT/index"
MANIFEST="$RAM_ROOT/manifest.tsv"
ENV_FILE="$RAM_ROOT/gtc_ram_context.env"

REPO_ROOTS=()
EXTRA_CONTEXT_ROOTS=(
  "$HOME/Desktop/GrandTheftCyberpunk"
  "$AI_ROOT/server/static/gtc"
  "$AI_ROOT/gta_mods"
  "$AI_ROOT/Pub/scripts"
)

discover_repos() {
  local repo
  while IFS= read -r repo; do
    repo="$(dirname "$repo")"
    if git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      REPO_ROOTS+=("$repo")
    fi
  done < <(find "$AI_ROOT" -maxdepth 3 -type d -name .git -print | sort)
}

EXCLUDES=(
  ".git"
  ".venv*"
  "venv"
  "__pycache__"
  "node_modules"
  "dist"
  "build"
  ".cache"
  "*.db"
  "*.sqlite"
  "*.pyc"
  "*.log"
  "*.zip"
  "*.tar"
  "*.tar.gz"
  "*.tgz"
  "runtime"
)

copy_repo() {
  local src="$1"
  local name
  name="$(basename "$src")"
  local dst="$SNAPSHOT_ROOT/$name"

  [[ -d "$src" ]] || return 0

  rm -rf "$dst"
  mkdir -p "$dst"

  if command -v rsync >/dev/null 2>&1; then
    local args=(-a --delete)
    for pattern in "${EXCLUDES[@]}"; do
      args+=(--exclude "$pattern")
    done
    rsync "${args[@]}" "$src/" "$dst/"
  else
    cp -a "$src/." "$dst/"
    find "$dst" \( \
      -name .git -o -name '.venv*' -o -name venv -o -name __pycache__ -o \
      -name node_modules -o -name dist -o -name build -o -name .cache -o \
      -name runtime \
    \) -prune -exec rm -rf {} +
    find "$dst" \( \
      -name '*.db' -o -name '*.sqlite' -o -name '*.pyc' -o -name '*.log' -o \
      -name '*.zip' -o -name '*.tar' -o -name '*.tar.gz' -o -name '*.tgz' \
    \) -delete
  fi
}

copy_extra_context() {
  local src="$1"
  [[ -d "$src" ]] || return 0

  local label
  label="$(printf '%s' "$src" | sed "s#^$HOME/##" | tr '/ ' '__')"
  local dst="$EXTRA_ROOT/$label"

  rm -rf "$dst"
  mkdir -p "$dst"

  if command -v rsync >/dev/null 2>&1; then
    local args=(-a --delete)
    for pattern in "${EXCLUDES[@]}"; do
      args+=(--exclude "$pattern")
    done
    rsync "${args[@]}" "$src/" "$dst/"
  else
    cp -a "$src/." "$dst/"
  fi
}

write_manifest() {
  : > "$MANIFEST"
  for repo in "${REPO_ROOTS[@]}"; do
    [[ -d "$repo" ]] || continue
    local name branch commit size
    name="$(basename "$repo")"
    branch="$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown')"
    commit="$(git -C "$repo" rev-parse --short HEAD 2>/dev/null || printf 'unknown')"
    size="$(du -sh "$SNAPSHOT_ROOT/$name" 2>/dev/null | awk '{print $1}')"
    printf "%s\t%s\t%s\t%s\t%s\n" "$name" "$repo" "$branch" "$commit" "${size:-0}" >> "$MANIFEST"
  done
  for root in "${EXTRA_CONTEXT_ROOTS[@]}"; do
    [[ -d "$root" ]] || continue
    local label size
    label="$(printf '%s' "$root" | sed "s#^$HOME/##" | tr '/ ' '__')"
    size="$(du -sh "$EXTRA_ROOT/$label" 2>/dev/null | awk '{print $1}')"
    printf "%s\t%s\t%s\t%s\t%s\n" "$label" "$root" "extra-context" "no-git" "${size:-0}" >> "$MANIFEST"
  done
}

write_indexes() {
  mkdir -p "$INDEX_ROOT"
  find "$SNAPSHOT_ROOT" -type f \
    \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o \
       -name '*.json' -o -name '*.yaml' -o -name '*.yml' -o -name '*.toml' -o \
       -name '*.reds' -o -name '*.md' -o -name '*.sh' -o -name '*.html' -o \
       -name '*.css' \) \
    -printf '%p\t%s\n' | sort > "$INDEX_ROOT/files.tsv"

  find "$EXTRA_ROOT" -type f \
    \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o \
       -name '*.json' -o -name '*.yaml' -o -name '*.yml' -o -name '*.toml' -o \
       -name '*.reds' -o -name '*.md' -o -name '*.sh' -o -name '*.html' -o \
       -name '*.css' \) \
    -printf '%p\t%s\n' | sort > "$INDEX_ROOT/extra_files.tsv"

  if command -v rg >/dev/null 2>&1; then
    rg -n --no-heading \
      "Grand Theft Cyberpunk|Cyberpunk|cerebellum|NGD|Lilith|Lyra|MSN|Ouroboros|llama|ollama|VRAM|GPU|RAM" \
      "$SNAPSHOT_ROOT" > "$INDEX_ROOT/hot_terms.rg" || true
    rg -n --no-heading \
      "Grand Theft Cyberpunk|Cyberpunk|cerebellum|NGD|Lilith|Lyra|MSN|Ouroboros|llama|ollama|VRAM|GPU|RAM" \
      "$EXTRA_ROOT" > "$INDEX_ROOT/extra_hot_terms.rg" || true
  fi

  if [[ -d "$STEAM_CYBERPUNK_ROOT" ]]; then
    find "$STEAM_CYBERPUNK_ROOT/r6/mods" \
         "$STEAM_CYBERPUNK_ROOT/r6/scripts" \
         "$STEAM_CYBERPUNK_ROOT/r6/tweaks" \
         "$STEAM_CYBERPUNK_ROOT/archive/pc/mod" \
         "$STEAM_CYBERPUNK_ROOT/bin/x64/plugins/cyber_engine_tweaks/mods" \
         -type f \( -name '*.reds' -o -name '*.yaml' -o -name '*.yml' -o \
                    -name '*.toml' -o -name '*.json' -o -name '*.archive' -o \
                    -name '*.xl' -o -name '*.lua' -o -name '*.cpmodproj' \) \
         -printf '%p\t%s\n' 2>/dev/null | sort > "$INDEX_ROOT/steam_cyberpunk_files.tsv" || true
  else
    : > "$INDEX_ROOT/steam_cyberpunk_files.tsv"
  fi
}

main() {
  mkdir -p "$SNAPSHOT_ROOT" "$EXTRA_ROOT" "$INDEX_ROOT"
  discover_repos

  for repo in "${REPO_ROOTS[@]}"; do
    copy_repo "$repo"
  done
  for root in "${EXTRA_CONTEXT_ROOTS[@]}"; do
    copy_extra_context "$root"
  done

  write_manifest
  write_indexes

  if [[ -f "$AI_ROOT/GTC_CONTEXT.md" ]]; then
    cp "$AI_ROOT/GTC_CONTEXT.md" "$RAM_ROOT/GTC_CONTEXT.md"
  fi
  if [[ -f "$AI_ROOT/GTC_CONTEXT_INDEX.json" ]]; then
    cp "$AI_ROOT/GTC_CONTEXT_INDEX.json" "$RAM_ROOT/GTC_CONTEXT_INDEX.json"
  fi
  if [[ -f "$AI_ROOT/GTC_DEPLOYMENT_PLAN.json" ]]; then
    cp "$AI_ROOT/GTC_DEPLOYMENT_PLAN.json" "$RAM_ROOT/GTC_DEPLOYMENT_PLAN.json"
  fi
  if [[ -f "$AI_ROOT/GTC_DEPLOYMENT_PLAN.md" ]]; then
    cp "$AI_ROOT/GTC_DEPLOYMENT_PLAN.md" "$RAM_ROOT/GTC_DEPLOYMENT_PLAN.md"
  fi

  cat > "$ENV_FILE" <<EOF
export GTC_RAM_CONTEXT_ROOT="$RAM_ROOT"
export GTC_RAM_REPO_ROOT="$SNAPSHOT_ROOT"
export GTC_RAM_EXTRA_ROOT="$EXTRA_ROOT"
export GTC_RAM_INDEX_ROOT="$INDEX_ROOT"
export GTC_RAM_MANIFEST="$MANIFEST"
export GTC_STEAM_CYBERPUNK_ROOT="$STEAM_CYBERPUNK_ROOT"
EOF

  echo "GTC RAM context primed"
  echo "  root:     $RAM_ROOT"
  echo "  repos:    $SNAPSHOT_ROOT"
  echo "  extra:    $EXTRA_ROOT"
  echo "  manifest: $MANIFEST"
  echo "  index:    $INDEX_ROOT/files.tsv"
  echo "  extra ix: $INDEX_ROOT/extra_files.tsv"
  echo "  steam:    $INDEX_ROOT/steam_cyberpunk_files.tsv"
  echo "  context:  $RAM_ROOT/GTC_CONTEXT_INDEX.json"
  echo "  deploy:   $RAM_ROOT/GTC_DEPLOYMENT_PLAN.json"
  du -sh "$RAM_ROOT" 2>/dev/null || true
}

main "$@"
