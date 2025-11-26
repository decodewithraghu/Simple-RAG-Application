#!/bin/bash

# RAG Application Startup Script
# This script starts both backend and frontend services

set -e

echo "🚀 Starting RAG Application..."
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    lsof -ti:$1 > /dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    if check_port $1; then
        echo -e "${YELLOW}Port $1 is in use. Killing existing process...${NC}"
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Start Backend
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📦 Starting Backend Server...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found at $BACKEND_DIR${NC}"
    exit 1
fi

cd "$BACKEND_DIR"

# Find Python executable
if [ -f "venv/bin/python3" ]; then
    PYTHON_BIN="$BACKEND_DIR/venv/bin/python3"
elif [ -f "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14" ]; then
    PYTHON_BIN="/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14"
else
    PYTHON_BIN="python3"
fi

echo -e "${GREEN}Using Python: $PYTHON_BIN${NC}"

# Check if required packages are installed
if ! $PYTHON_BIN -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Python dependencies not found. Installing...${NC}"
    $PYTHON_BIN -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install backend dependencies${NC}"
        exit 1
    fi
fi

# Clear port 8000
kill_port 8000

# Start backend
echo -e "${GREEN}✅ Starting FastAPI server on http://localhost:8000${NC}"
$PYTHON_BIN main.py > /tmp/rag-backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo -n "⏳ Waiting for backend to start"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo ""
        echo -e "${RED}❌ Backend failed to start. Check logs at /tmp/rag-backend.log${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
done

echo ""

# Start Frontend
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🎨 Starting Frontend Server...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend directory not found at $FRONTEND_DIR${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
fi

# Verify react-scripts is available
if ! [ -f "node_modules/.bin/react-scripts" ]; then
    echo -e "${YELLOW}⚠️  react-scripts not found. Reinstalling dependencies...${NC}"
    rm -rf node_modules package-lock.json
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
fi

# Clear port 3000
kill_port 3000

# Start frontend
echo -e "${GREEN}✅ Starting React development server on http://localhost:3000${NC}"
BROWSER=none npm start > /tmp/rag-frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo -n "⏳ Waiting for frontend to start"
for i in {1..60}; do
    if check_port 3000; then
        echo ""
        echo -e "${GREEN}✅ Frontend is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 60 ]; then
        echo ""
        echo -e "${RED}❌ Frontend failed to start. Check logs at /tmp/rag-frontend.log${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi
done

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 RAG Application Started Successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📍 Application URLs:${NC}"
echo -e "   Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "   Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "   API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}📋 Process IDs:${NC}"
echo -e "   Backend PID:  ${YELLOW}$BACKEND_PID${NC}"
echo -e "   Frontend PID: ${YELLOW}$FRONTEND_PID${NC}"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "   Backend:  ${YELLOW}/tmp/rag-backend.log${NC}"
echo -e "   Frontend: ${YELLOW}/tmp/rag-frontend.log${NC}"
echo ""
echo -e "${YELLOW}💡 To stop the application, press Ctrl+C or run:${NC}"
echo -e "   ${YELLOW}kill $BACKEND_PID $FRONTEND_PID${NC}"
echo ""
echo -e "${GREEN}✨ Opening application in browser...${NC}"
sleep 2
open http://localhost:3000 2>/dev/null || true

# Keep script running and handle shutdown
trap 'echo ""; echo "🛑 Shutting down..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "✅ Shutdown complete"; exit 0' INT TERM

# Wait for processes
wait
