#!/bin/bash
# abyssal-manifest.sh — rebuild production.yaml

cat > ~/abyssal-assets-master/manifests/production.yaml << 'YAML'
# Abyssal Assets Production Manifest
version: 0.3.2
project: abyssal-assets
sephirot_active: true
network:
  backend: fastapi
  frontend: phaser3
  ports:
    http: 8000
    websocket: 8001
    msn_router: 8007
    lyra_dialogue: 3211
  cors:
    origins:
      - "http://localhost:3000"
      - "capacitor://localhost"
mysql:
  enabled: false
database:
  driver: sqlite
  path: "${ABYSSAL_ROOT:-~}/abyssal-assets-master/server/runtime/abyssal_assets.db"
  wal_mode: true
  integrity_check: true
sephirot:
  foundation:
    - keter
    - chokmah
    - binah
  interface:
    - chesed
    - gevurah
    - tiferet
    - netzach
    - hod
  infrastructure:
    - yesod
    - malkuth
  metaconscious:
    - da'at
    - binah
    - hod
    - tiferet
    - malkuth
    - netzach
    - gevurah
    - chokmah
msn_router:
  wave_count: 4
  agent_count: 27
  local_inference: nemotron-mini
  cortex: unified
  hmr_integration: true
lilith_kernel: 777
feature_bridges:
  cyberpunk:
    enabled: true
    telemetry: /storage/emulated/0/Documents/gtc_cerebellum/telemetry.json
    deploy_reconcile_script: ./scripts/reconcile_gtc_deployment.py
    bootstrap_script: /data/user/0/com.termux/files/home/Desktop/AI/Pub/scripts/bootstrap_gtc_cerebellum.sh
  nssp:
    enabled: true
    os_keybind: Meta+N
  nessie:
    enabled: true
    treasury_path: ./server/runtime/nessie_treasury.json
environment:
  ABYSSAL_ROOT: "${HOME}/abyssal-assets-master"
  ABYSSAL_SECRET_KEY: abyssal-assets-secret-key-change-in-production
  OLLAMA_BASE_URL: http://localhost:11434
YAML
echo "[Abyssal] production.yaml rebuilt"
