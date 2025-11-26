# Quick Start Guide

## ⚡ Quick Setup (3 Steps)

### 1. Install & Start Ollama

```bash
# Install Ollama (if not already installed)
brew install ollama

# Start Ollama in a terminal
ollama serve

# In another terminal, pull the model
ollama pull llama2
```

### 2. Setup Backend

```bash
cd backend
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create the `.env` configuration file
- Set up necessary directories

### 3. Start Backend Server

```bash
cd backend
./start.sh
```

The backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 4. Setup & Start Frontend

```bash
# In a new terminal
cd frontend
npm install
npm start
```

The frontend will open at http://localhost:3000

## 🎯 Using the Application

1. **Upload a Document**
   - Drag & drop a PDF or TXT file
   - Wait for processing (you'll see chunk count)

2. **Query Your Documents**
   - Type a question in the query box
   - Select number of sources (3-10)
   - Click "Ask Question"
   - View the AI-generated answer with sources

## 🔧 Troubleshooting

### Ollama not available
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Backend errors
```bash
# Ensure you're in the virtual environment
cd backend
source venv/bin/activate
python3 main.py
```

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

## 📦 What Was Installed

### Backend Dependencies
- FastAPI - Web framework
- FAISS - Vector database (Facebook AI Similarity Search)
- Sentence Transformers - Text embeddings
- PyPDF2 - PDF processing
- Uvicorn - ASGI server

### Frontend Dependencies
- React - UI framework
- Axios - HTTP client
- React Dropzone - File upload

## 🎨 Features

- ✅ PDF and TXT file upload
- ✅ Automatic text chunking
- ✅ Vector embeddings with sentence-transformers
- ✅ Fast similarity search with FAISS
- ✅ AI-powered answers with Ollama
- ✅ Source attribution
- ✅ Real-time health monitoring

## 📊 System Requirements

- Python 3.8+
- Node.js 16+
- Ollama
- macOS, Linux, or Windows

## 🚀 Next Steps

1. Try uploading a PDF document
2. Ask questions about its content
3. Experiment with different Ollama models
4. Customize chunk size and overlap in `backend/main.py`

For more details, see the main [README.md](../README.md)
