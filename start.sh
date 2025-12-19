#!/bin/bash

# OneCard Bot - Easy Startup Script
# This script starts all three services in the background

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting OneCard Bot Services...${NC}\n"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Check if Node/npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Node.js/npm is not installed${NC}"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found. Make sure GOOGLE_API_KEY is set.${NC}\n"
fi

# Create logs directory
mkdir -p logs

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping all services...${NC}"
    kill $MOCK_API_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Start Mock API (Port 5000)
echo -e "${GREEN}📡 Starting Mock API Server (Port 5000)...${NC}"
python3 mock_apis.py > logs/mock_api.log 2>&1 &
MOCK_API_PID=$!
sleep 2

# Start Backend (Port 8000)
echo -e "${GREEN}🤖 Starting AI Backend Server (Port 8000)...${NC}"
python3 backend.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
sleep 3

# Start Frontend (Port 5173)
echo -e "${GREEN}💻 Starting Frontend Dev Server (Port 5173)...${NC}"
cd onecard-bot
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo -e "\n${GREEN}✅ All services started!${NC}\n"
echo -e "${YELLOW}Services running:${NC}"
echo -e "  • Mock API:    http://localhost:5000 (PID: $MOCK_API_PID)"
echo -e "  • Backend:     http://localhost:8000 (PID: $BACKEND_PID)"
echo -e "  • Frontend:    http://localhost:5173 (PID: $FRONTEND_PID)"
echo -e "\n${YELLOW}Logs are in the 'logs/' directory${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Wait for all processes
wait

