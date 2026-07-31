#!/bin/bash
# EliClaw Desktop Build Script
# Builds for Windows, macOS, and Linux

set -e

echo "🔨 Building EliClaw Desktop..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Parse arguments
PLATFORM=${1:-all}
ARCH=${2:-x64}

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
npm install

# Build renderer
echo -e "${BLUE}Building renderer...${NC}"
npm run build:renderer

# Build for specific platform
build_platform() {
  local platform=$1
  local arch=$2

  echo -e "${YELLOW}Building for ${platform} (${arch})...${NC}"

  case $platform in
    win)
      npx electron-builder --win --${arch}
      ;;
    mac)
      npx electron-builder --mac --${arch}
      ;;
    linux)
      npx electron-builder --linux --${arch}
      ;;
  esac

  echo -e "${GREEN}✅ ${platform} build complete!${NC}"
}

# Build based on platform selection
case $PLATFORM in
  all)
    build_platform "win" "x64"
    build_platform "mac" "x64"
    build_platform "linux" "x64"
    ;;
  win|windows)
    build_platform "win" $ARCH
    ;;
  mac|macos|darwin)
    build_platform "mac" $ARCH
    ;;
  linux)
    build_platform "linux" $ARCH
    ;;
  *)
    echo "Usage: ./build.sh [all|win|mac|linux] [x64|arm64|ia32]"
    exit 1
    ;;
esac

echo -e "${GREEN}🎉 All builds complete! Check the dist/ folder.${NC}"