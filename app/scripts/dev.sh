#!/bin/bash

# Auto-Applier v2 - Development Script
# Runs FastAPI backend, Vite frontend, and Tauri concurrently

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Auto-Applier v2 Development Environment${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
TAURI_DIR="$SCRIPT_DIR/tauri"

# Kill any existing processes
echo -e "${YELLOW}Cleaning up existing processes...${NC}"
pkill -f "python -m auto_applier_api" || true
pkill -f "vite" || true

# Start FastAPI backend
echo -e "${GREEN}Starting FastAPI backend...${NC}"
cd "$BACKEND_DIR"
python -m auto_applier_api &
BACKEND_PID=$!

# Wait for backend to start and get port
sleep 3

# Start Vite frontend
echo -e "${GREEN}Starting Vite frontend...${NC}"
cd "$FRONTEND_DIR"
npm run dev &
VITE_PID=$!

# Wait for Vite to start
sleep 2

# Start Tauri
echo -e "${GREEN}Starting Tauri...${NC}"
cd "$TAURI_DIR"
npm run tauri dev &
TAURI_PID=$!

echo ""
echo -e "${GREEN}All services started:${NC}"
echo "  - FastAPI backend (PID: $BACKEND_PID)"
echo "  - Vite frontend (PID: $VITE_PID)"
echo "  - Tauri dev (PID: $TAURI_PID)"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Function to clean up on exit
cleanup() {
    echo -e "\n${RED}Shutting down all services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $VITE_PID 2>/dev/null || true
    kill $TAURI_PID 2>/dev/null || true
    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

# Trap SIGINT and SIGTERM
trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait
