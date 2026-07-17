#!/bin/bash
# Abyssal Assets - Local Build Script
# Run this on a machine with Node.js, Android SDK, and Java 17+

set -e

echo "🌊 Abyssal Assets - Local Build Script"
echo "====================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT_DIR="$PROJECT_ROOT/client"
ANDROID_DIR="$CLIENT_DIR/android"

echo -e "${BLUE}Project root:${NC} $PROJECT_ROOT"
echo -e "${BLUE}Client dir:${NC} $CLIENT_DIR"

# Check prerequisites
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 found: $("$1" --version 2>&1 | head -1)"
        return 0
    else
        echo -e "${RED}✗${NC} $1 not found"
        return 1
    fi
}

echo ""
echo "Checking prerequisites..."

MISSING=0
check_command node || MISSING=1
check_command npm || MISSING=1
check_command java || MISSING=1
check_command gradle || echo -e "${YELLOW}!${NC} gradle not in PATH (using wrapper)"

if [ $MISSING -eq 1 ]; then
    echo -e "${RED}Missing required tools. Please install Node.js, npm, and Java 17+.${NC}"
    exit 1
fi

# Check Android SDK
if [ -z "$ANDROID_HOME" ] && [ -z "$ANDROID_SDK_ROOT" ]; then
    echo -e "${YELLOW}!${NC} ANDROID_HOME not set. Attempting common locations..."
    if [ -d "$HOME/Android/Sdk" ]; then
        export ANDROID_HOME="$HOME/Android/Sdk"
        echo -e "${GREEN}✓${NC} Found Android SDK at $ANDROID_HOME"
    elif [ -d "$HOME/Library/Android/sdk" ]; then
        export ANDROID_HOME="$HOME/Library/Android/sdk"
        echo -e "${GREEN}✓${NC} Found Android SDK at $ANDROID_HOME"
    else
        echo -e "${RED}✗${NC} Android SDK not found. Set ANDROID_HOME."
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} ANDROID_HOME: ${ANDROID_HOME:-$ANDROID_SDK_ROOT}"
fi

# Navigate to client directory
cd "$CLIENT_DIR"

echo ""
echo -e "${BLUE}Step 1: Install npm dependencies${NC}"
npm ci --legacy-peer-deps

echo ""
echo -e "${BLUE}Step 2: Build web app${NC}"
npm run build

echo ""
echo -e "${BLUE}Step 3: Initialize Capacitor (if needed)${NC}"
if [ ! -f "capacitor.config.ts" ]; then
    echo "Initializing Capacitor..."
    npx cap init "Abyssal Assets" "com.lilithsystems.abyssalassets" --web-dir=dist
fi

echo ""
echo -e "${BLUE}Step 4: Add Android platform (if needed)${NC}"
if [ ! -d "android" ]; then
    echo "Adding Android platform..."
    npx cap add android
fi

echo ""
echo -e "${BLUE}Step 5: Sync Capacitor${NC}"
npx cap sync android

echo ""
echo -e "${BLUE}Step 6: Build Android APK${NC}"
cd android

# Use gradle wrapper
if [ -f "./gradlew" ]; then
    chmod +x ./gradlew
    ./gradlew assembleRelease
else
    echo -e "${RED}Gradle wrapper not found!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Build complete!${NC}"
echo ""
echo "APK location:"
find . -name "*.apk" -path "*/build/outputs/*" | head -5

echo ""
echo -e "${BLUE}To install on device:${NC}"
echo "  adb install ./app/build/outputs/apk/release/app-release.apk"
echo ""
echo -e "${BLUE}To open in Android Studio:${NC}"
echo "  npx cap open android"