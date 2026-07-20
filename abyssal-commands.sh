# Abyssal Assets - Custom Shell Commands
# Source this file in your .bashrc, .zshrc, or run: source ~/abyssal-assets-commands.sh

# ============================================================================
# ABYSSAL ASSETS ALIASES & FUNCTIONS
# ============================================================================

# Project root (adjust if needed)
export ABYSSAL_ROOT="${ABYSSAL_ROOT:-$HOME/abyssal-assets-master}"
export ABYSSAL_CLIENT="$ABYSSAL_ROOT/client"
export ABYSSAL_SERVER="$ABYSSAL_ROOT/server"
export ABYSSAL_ANDROID="$ABYSSAL_CLIENT/android"

# Quick navigation
alias aa='cd "$ABYSSAL_ROOT"'
alias aac='cd "$ABYSSAL_CLIENT"'
alias aas='cd "$ABYSSAL_SERVER"'
alias aad='cd "$ABYSSAL_ANDROID"'

# Build commands
alias aa-build='cd "$ABYSSAL_CLIENT" && npm run build'
alias aa-dev='cd "$ABYSSAL_CLIENT" && npm run dev'
alias aa-lint='cd "$ABYSSAL_CLIENT" && npm run lint'
alias aa-test='cd "$ABYSSAL_CLIENT" && npm run test'

# Capacitor/Android commands
alias aa-cap-sync='cd "$ABYSSAL_CLIENT" && npx cap sync android'
alias aa-cap-open='cd "$ABYSSAL_CLIENT" && npx cap open android'
alias aa-cap-run='cd "$ABYSSAL_CLIENT" && npm run cap:run'
alias aa-cap-build='cd "$ABYSSAL_CLIENT" && npm run cap:build'

# Android Gradle commands
alias aa-gradle='cd "$ABYSSAL_ANDROID" && ./gradlew'
alias aa-assemble-debug='cd "$ABYSSAL_ANDROID" && ./gradlew assembleDebug'
alias aa-assemble-release='cd "$ABYSSAL_ANDROID" && ./gradlew assembleRelease'
alias aa-bundle-release='cd "$ABYSSAL_ANDROID" && ./gradlew bundleRelease'
alias aa-install-debug='cd "$ABYSSAL_ANDROID" && ./gradlew installDebug'
alias aa-install-release='cd "$ABYSSAL_ANDROID" && ./gradlew installRelease'
alias aa-uninstall='adb uninstall com.lilithsystems.abyssalassets'
alias aa-clean='cd "$ABYSSAL_ANDROID" && ./gradlew clean'

# Full build pipeline
alias aa-build-apk='$ABYSSAL_ROOT/build-apk.sh release'
alias aa-build-apk-debug='$ABYSSAL_ROOT/build-apk.sh debug'
alias aa-build-local='$ABYSSAL_ROOT/build-local.sh'

# Server commands
alias aa-server='cd "$ABYSSAL_SERVER" && python main.py'
alias aa-server-dev='cd "$ABYSSAL_SERVER" && uvicorn main:app --reload --port 8000'
alias aa-server-test='cd "$ABYSSAL_SERVER" && python -m pytest'

# Docker commands
alias aa-docker-up='cd "$ABYSSAL_ROOT" && docker-compose up -d'
alias aa-docker-down='cd "$ABYSSAL_ROOT" && docker-compose down'
alias aa-docker-logs='cd "$ABYSSAL_ROOT" && docker-compose logs -f'
alias aa-docker-build='cd "$ABYSSAL_ROOT" && docker-compose build'

# Database
alias aa-db-shell='sqlite3 "$ABYSSAL_ROOT/abyssal_assets.db"'
alias aa-db-backup='cp "$ABYSSAL_ROOT/abyssal_assets.db" "$ABYSSAL_ROOT/abyssal_assets.db.backup.$(date +%Y%m%d_%H%M%S)"'

# Git shortcuts
alias aa-git-status='cd "$ABYSSAL_ROOT" && git status'
alias aa-git-pull='cd "$ABYSSAL_ROOT" && git pull'
alias aa-git-push='cd "$ABYSSAL_ROOT" && git push'
alias aa-git-log='cd "$ABYSSAL_ROOT" && git log --oneline -20'

# Logs & monitoring
alias aa-logs-client='cd "$ABYSSAL_CLIENT" && npm run dev 2>&1 | tail -f'
alias aa-logs-server='journalctl -u abyssal-server -f'
alias aa-adb-log='adb logcat -s "Capacitor*" "chromium*" "AbyssalAssets*" "*:E"'

# Device commands
alias aa-devices='adb devices -l'
alias aa-screenshot='adb shell screencap -p /sdcard/screen.png && adb pull /sdcard/screen.png ~/abyssal-screenshot-$(date +%s).png'
alias aa-screenrecord='adb shell screenrecord /sdcard/recording.mp4 --time-limit 60'

# MSN Router (from msn-integration)
alias aa-msn-start='cd "$HOME/msn-integration" && python msn_router.py 8007'
alias aa-msn-status='curl -s localhost:8007/status | jq .'

# Utility functions
aa-help() {
    echo "╔═══════════════════════════════════════════════════════════════════════╗"
    echo "║                    ABYSSAL ASSETS COMMANDS                           ║"
    echo "╠═══════════════════════════════════════════════════════════════════════╣"
    echo "║ Navigation:                                                          ║"
    echo "║   aa           - Go to project root                                  ║"
    echo "║   aac          - Go to client (Phaser)                               ║"
    echo "║   aas          - Go to server (FastAPI)                              ║"
    echo "║   aad          - Go to Android project                               ║"
    echo "║                                                                        ║"
    echo "║ Building:                                                              ║"
    echo "║   aa-build         - Build web app (Vite)                            ║"
    echo "║   aa-dev           - Start dev server                                ║"
    echo "║   aa-cap-build     - Build + sync Capacitor                          ║"
    echo "║   aa-cap-run       - Build + run on device                           ║"
    echo "║   aa-build-apk     - Full release APK build                          ║"
    echo "║   aa-build-apk-debug - Debug APK build                               ║"
    echo "║   aa-build-local   - Local build script                              ║"
    echo "║                                                                        ║"
    echo "║ Android/Gradle:                                                        ║"
    echo "║   aa-assemble-debug  - Build debug APK                               ║"
    echo "║   aa-assemble-release - Build release APK                            ║"
    echo "║   aa-bundle-release   - Build AAB for Play Store                     ║"
    echo "║   aa-install-debug    - Install debug to device                      ║"
    echo "║   aa-install-release  - Install release to device                    ║"
    echo "║   aa-clean            - Clean Gradle build                           ║"
    echo "║                                                                        ║"
    echo "║ Server:                                                                ║"
    echo "║   aa-server        - Run production server                           ║"
    echo "║   aa-server-dev    - Run dev server with reload                      ║"
    echo "║                                                                        ║"
    echo "║ Docker:                                                                ║"
    echo "║   aa-docker-up     - Start full stack                                ║"
    echo "║   aa-docker-down   - Stop full stack                                 ║"
    echo "║   aa-docker-logs   - Follow logs                                     ║"
    echo "║                                                                        ║"
    echo "║ Device/Debug:                                                          ║"
    echo "║   aa-devices       - List connected devices                          ║"
    echo "║   aa-screenshot    - Take screenshot                                 ║"
    echo "║   aa-screenrecord  - Record screen (60s)                             ║"
    echo "║   aa-adb-log       - Follow Android logs                             ║"
    echo "║                                                                        ║"
    echo "║ Database:                                                              ║"
    echo "║   aa-db-shell      - Open SQLite shell                               ║"
    echo "║   aa-db-backup     - Backup database                                 ║"
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
}

aa-full-build() {
    echo "🌊 Full Abyssal Assets Build Pipeline"
    echo "====================================="
    
    echo "1. Building web app..."
    cd "$ABYSSAL_CLIENT" && npm run build
    
    echo "2. Syncing Capacitor..."
    npx cap sync android
    
    echo "3. Building Android Release APK..."
    cd "$ABYSSAL_ANDROID" && ./gradlew assembleRelease
    
    echo "4. Building AAB for Play Store..."
    ./gradlew bundleRelease
    
    echo ""
    echo "✅ Build complete!"
    echo "APK: $ABYSSAL_ANDROID/app/build/outputs/apk/release/app-release.apk"
    echo "AAB: $ABYSSAL_ANDROID/app/build/outputs/bundle/release/app-release.aab"
}

aa-debug-apk() {
    echo "🔧 Building debug APK and installing..."
    cd "$ABYSSAL_CLIENT" && npm run build
    npx cap sync android
    cd "$ABYSSAL_ANDROID" && ./gradlew assembleDebug installDebug
    echo "✅ Debug APK installed on device"
}

aa-release-install() {
    echo "🚀 Building release APK and installing..."
    cd "$ABYSSAL_CLIENT" && npm run build
    npx cap sync android
    cd "$ABYSSAL_ANDROID" && ./gradlew assembleRelease installRelease
    echo "✅ Release APK installed on device"
}

aa-watch-logs() {
    echo "📜 Following Android logs for Abyssal Assets..."
    adb logcat -s "Capacitor*" "chromium*" "AbyssalAssets*" "*:E" | while read line; do
        echo "$(date '+%H:%M:%S') $line"
    done
}

aa-pwa-install() {
    echo "📱 PWA Installation Instructions:"
    echo "1. Open Chrome on Android"
    echo "2. Navigate to your deployed PWA URL (or localhost:3000)"
    echo "3. Tap menu (⋮) → 'Install app' or 'Add to Home screen'"
    echo "4. The app will install as a standalone PWA"
}

aa-status() {
    echo "╔═══════════════════════════════════════════════════════════════════════╗"
    echo "║                    ABYSSAL ASSETS STATUS                             ║"
    echo "╠═══════════════════════════════════════════════════════════════════════╣"
    echo "║ Project: $ABYSSAL_ROOT"
    echo "║ Client:  $ABYSSAL_CLIENT"
    echo "║ Server:  $ABYSSAL_SERVER"
    echo "║ Android: $ABYSSAL_ANDROID"
    echo "╠═══════════════════════════════════════════════════════════════════════╣"
    
    # Check if directories exist
    [ -d "$ABYSSAL_CLIENT" ] && echo "║ Client:  ✓ Found" || echo "║ Client:  ✗ Missing"
    [ -d "$ABYSSAL_SERVER" ] && echo "║ Server:  ✓ Found" || echo "║ Server:  ✗ Missing"
    [ -d "$ABYSSAL_ANDROID" ] && echo "║ Android: ✓ Found" || echo "║ Android: ✗ Not initialized"
    
    # Check for APK
    if [ -f "$ABYSSAL_ANDROID/app/build/outputs/apk/release/app-release.apk" ]; then
        SIZE=$(du -h "$ABYSSAL_ANDROID/app/build/outputs/apk/release/app-release.apk" | cut -f1)
        echo "║ Release APK: ✓ Built ($SIZE)"
    elif [ -f "$ABYSSAL_ANDROID/app/build/outputs/apk/debug/app-debug.apk" ]; then
        SIZE=$(du -h "$ABYSSAL_ANDROID/app/build/outputs/apk/debug/app-debug.apk" | cut -f1)
        echo "║ Debug APK:   ✓ Built ($SIZE)"
    else
        echo "║ APK:         ✗ Not built"
    fi
    
    # Check connected devices
    DEVICES=$(adb devices | grep -v "List" | grep "device$" | wc -l)
    echo "║ Connected devices: $DEVICES"
    
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
}

# Auto-completion for aa-* commands
_aa_commands() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local commands="aa aac aas aad aa-build aa-dev aa-lint aa-test aa-cap-sync aa-cap-open aa-cap-run aa-cap-build aa-gradle aa-assemble-debug aa-assemble-release aa-bundle-release aa-install-debug aa-install-release aa-uninstall aa-clean aa-build-apk aa-build-apk-debug aa-build-local aa-server aa-server-dev aa-server-test aa-docker-up aa-docker-down aa-docker-logs aa-docker-build aa-db-shell aa-db-backup aa-git-status aa-git-pull aa-git-push aa-git-log aa-logs-client aa-logs-server aa-adb-log aa-devices aa-screenshot aa-screenrecord aa-msn-start aa-msn-status aa-help aa-full-build aa-debug-apk aa-release-install aa-watch-logs aa-pwa-install aa-status"
    COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
}

complete -F _aa_commands aa
complete -F _aa_commands aac
complete -F _aa_commands aas
complete -F _aa_commands aad

# Show help on first load
echo "🌊 Abyssal Assets commands loaded. Type 'aa-help' for all commands."