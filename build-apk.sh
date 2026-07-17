#!/usr/bin/env bash
# Abyssal Assets - Android APK Build Script
# Usage: ./build-apk.sh [debug|release]

set -euo pipefail

BUILD_TYPE="${1:-release}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT_DIR="$PROJECT_ROOT/client"
ANDROID_DIR="$CLIENT_DIR/android"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Abyssal Assets - Android APK Builder                        ║"
echo "║  Build Type: $BUILD_TYPE                                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# Check prerequisites
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ $1 not found. Please install $1"
        exit 1
    fi
    echo "✓ $1 found: $("$1" --version 2>&1 | head -1)"
}

echo "🔍 Checking prerequisites..."
check_command node
check_command npm
check_command java

# Check for Android SDK
if [[ -z "${ANDROID_HOME:-}" && -z "${ANDROID_SDK_ROOT:-}" ]]; then
    echo "⚠️  ANDROID_HOME not set. Checking common locations..."
    for path in \
        "$HOME/Android/Sdk" \
        "$HOME/Library/Android/sdk" \
        "/opt/android-sdk" \
        "/usr/local/android-sdk"; do
        if [[ -d "$path" ]]; then
            export ANDROID_HOME="$path"
            export ANDROID_SDK_ROOT="$path"
            echo "✓ Found Android SDK at $ANDROID_HOME"
            break
        fi
    done
fi

if [[ -z "${ANDROID_HOME:-}" ]]; then
    echo "❌ Android SDK not found. Please install Android Studio and set ANDROID_HOME"
    exit 1
fi

export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin:$PATH"

# Build web app
echo ""
echo "📦 Building web app..."
cd "$CLIENT_DIR"

if [[ ! -d "node_modules" ]]; then
    echo "📥 Installing npm dependencies..."
    npm ci --prefer-offline --no-audit
fi

echo "🏗️  Running Vite build..."
npm run build

# Initialize Capacitor if needed
if [[ ! -f "capacitor.config.ts" ]]; then
    echo "⚡ Initializing Capacitor..."
    npx cap init "Abyssal Assets" com.lilithsystems.abyssalassets --web-dir=dist
fi

# Add Android platform if needed
if [[ ! -d "$ANDROID_DIR" ]]; then
    echo "📱 Adding Android platform..."
    npx cap add android
fi

# Sync Capacitor
echo "🔄 Syncing Capacitor..."
npx cap sync android

# Build Android
echo ""
echo "🤖 Building Android $BUILD_TYPE..."
cd "$ANDROID_DIR"

if [[ ! -f "gradlew" ]]; then
    echo "❌ gradlew not found. Run 'npx cap sync android' first."
    exit 1
fi

chmod +x gradlew

GRADLE_TASK="assemble${BUILD_TYPE^}"
if [[ "$BUILD_TYPE" == "release" ]]; then
    GRADLE_TASK="assembleRelease"
    echo "🔐 Building RELEASE APK (signed)"
else
    GRADLE_TASK="assembleDebug"
    echo "🔧 Building DEBUG APK"
fi

echo "⚙️  Running: ./gradlew $GRADLE_TASK"
./gradlew "$GRADLE_TASK" -Pandroid.enableR8=true --no-daemon --max-workers=4

# Output APK location
if [[ "$BUILD_TYPE" == "release" ]]; then
    APK_PATH="$ANDROID_DIR/app/build/outputs/apk/release/app-release.apk"
    AAB_PATH="$ANDROID_DIR/app/build/outputs/bundle/release/app-release.aab"
else
    APK_PATH="$ANDROID_DIR/app/build/outputs/apk/debug/app-debug.apk"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ BUILD COMPLETE                                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📱 APK: $APK_PATH"

if [[ -f "$APK_PATH" ]]; then
    APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
    echo "📦 Size: $APK_SIZE"
    
    # Copy to project root for easy access
    cp "$APK_PATH" "$PROJECT_ROOT/abyssal-assets-${BUILD_TYPE}.apk"
    echo "📋 Copied to: $PROJECT_ROOT/abyssal-assets-${BUILD_TYPE}.apk"
else
    echo "❌ APK not found at expected path"
    exit 1
fi

if [[ "$BUILD_TYPE" == "release" && -f "$AAB_PATH" ]]; then
    AAB_SIZE=$(du -h "$AAB_PATH" | cut -f1)
    echo "📦 AAB: $AAB_PATH ($AAB_SIZE)"
    cp "$AAB_PATH" "$PROJECT_ROOT/abyssal-assets-release.aab"
    echo "📋 Copied to: $PROJECT_ROOT/abyssal-assets-release.aab"
fi

echo ""
echo "🚀 Ready to install!"
echo "   adb install -r $PROJECT_ROOT/abyssal-assets-${BUILD_TYPE}.apk"
echo ""
echo "📲 Or transfer to your phone and install manually."