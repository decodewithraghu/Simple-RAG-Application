#!/bin/bash

echo "🚀 Starting RAG Application Backend..."
echo ""

# Navigate to backend directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Use the venv python directly
PYTHON_BIN="$SCRIPT_DIR/venv/bin/python3"

# Clear port 8000 if in use
echo "🔍 Checking port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Port 8000 cleared" || echo "✅ Port 8000 is free"
echo ""

# Start the server
echo "✅ Starting FastAPI server on http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"
echo ""

"$PYTHON_BIN" main.py
