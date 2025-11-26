#!/bin/bash

echo "🔧 Setting up RAG Application Backend..."
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Create necessary directories
mkdir -p uploads
mkdir -p faiss_db

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the backend server, run:"
echo "  cd backend && ./start.sh"
echo ""
echo "Or manually:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python3 main.py"
