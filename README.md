# RAG Application

A complete Retrieval-Augmented Generation (RAG) application that allows you to upload documents, process them into embeddings, store them in a vector database, and query them using Ollama for intelligent responses.

## 🚀 Features

- **Document Upload**: Support for PDF and TXT files
- **Automatic Chunking**: Intelligently splits documents into manageable chunks
- **Vector Embeddings**: Uses sentence transformers to create embeddings
- **Vector Database**: Stores embeddings in FAISS for efficient retrieval
- **AI-Powered Queries**: Uses Ollama (llama2 or other models) to generate responses
- **Modern UI**: Clean React-based frontend with drag-and-drop upload
- **Real-time Status**: Shows system health and document statistics

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**
- **Node.js 16+** and npm
- **Ollama** - [Install Ollama](https://ollama.ai/)

## 🛠️ Installation

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Start Ollama service
ollama serve

# Pull a model (in a new terminal)
ollama pull llama2
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env if needed (optional)
# The default settings should work fine
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install
```

## 🚀 Running the Application

### Start Backend Server

```bash
# In the backend directory with virtual environment activated
cd backend
source venv/bin/activate  # Activate venv if not already active
python main.py
```

The backend API will start at `http://localhost:8000`

You can access the API documentation at `http://localhost:8000/docs`

### Start Frontend Server

```bash
# In the frontend directory (new terminal)
cd frontend
npm start
```

The frontend will start at `http://localhost:3000`

## 📖 Usage

1. **Upload Documents**:
   - Drag and drop a PDF or TXT file into the upload area
   - Or click "Browse Files" to select a file
   - Wait for the document to be processed and chunked

2. **Query Documents**:
   - Type your question in the query box
   - Select the number of source chunks to use (3-10)
   - Click "Ask Question"
   - View the AI-generated answer and source references

3. **Monitor Status**:
   - Check the header for Ollama availability
   - See the number of uploaded documents and chunks

## 🏗️ Project Structure

```
Rag/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment variables template
│   ├── .gitignore
│   └── utils/
│       ├── __init__.py
│       ├── document_loader.py  # PDF/TXT loading
│       ├── text_chunker.py     # Text chunking logic
│       ├── embeddings.py       # Embedding generation & Ollama client
│       └── vector_store.py     # ChromaDB integration
│
└── frontend/
    ├── package.json
    ├── .env                    # Frontend environment variables
    ├── public/
    │   └── index.html
    └── src/
        ├── index.js
        ├── index.css
        ├── App.js              # Main application component
        ├── App.css
        ├── api.js              # API client
        └── components/
            ├── Header.js       # Header with status
            ├── Header.css
            ├── FileUpload.js   # File upload component
            ├── FileUpload.css
            ├── QueryInterface.js # Query interface
            └── QueryInterface.css
```

## 🔧 Configuration

### Backend (.env)

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
FAISS_PERSIST_DIRECTORY=./faiss_db
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
```

### Frontend (.env)

```env
REACT_APP_API_URL=http://localhost:8000
```

## 🧪 API Endpoints

### Health Check
- `GET /health` - Check system health

### Document Management
- `POST /upload` - Upload a document
- `DELETE /documents` - Delete all documents
- `GET /stats` - Get document statistics

### Query
- `POST /query` - Query the document database

## 🔍 How It Works

1. **Document Upload**:
   - User uploads a PDF/TXT file
   - Backend extracts text from the document
   - Text is split into chunks (1000 chars with 200 char overlap)
   - Each chunk is converted to embeddings using sentence-transformers
   - Embeddings are stored in FAISS vector index

2. **Querying**:
   - User submits a question
   - Question is converted to an embedding
   - FAISS finds the most similar document chunks using L2 distance
   - Retrieved chunks are sent to Ollama as context
   - Ollama generates an answer based on the context
   - Answer and sources are returned to the user

## 🛡️ Technologies Used

### Backend
- **FastAPI** - Modern web framework for Python
- **FAISS** - Efficient similarity search and vector database by Facebook AI
- **Sentence Transformers** - Generate embeddings
- **PyPDF2** - PDF text extraction
- **Ollama** - Local LLM for answer generation

### Frontend
- **React** - UI framework
- **Axios** - HTTP client
- **React Dropzone** - File upload component

## 🚨 Troubleshooting

### Ollama not available
- Make sure Ollama is running: `ollama serve`
- Check if the model is pulled: `ollama list`
- Pull the model if missing: `ollama pull llama2`

### Backend errors
- Ensure virtual environment is activated
- Check all dependencies are installed
- Verify .env file exists and is configured

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check REACT_APP_API_URL in frontend/.env
- Check CORS settings in backend/main.py

### PDF upload fails
- Check file size (default max 10MB)
- Ensure PDF contains extractable text (not scanned images)

## 📝 Notes

- The application uses the `all-MiniLM-L6-v2` model for embeddings (automatically downloaded on first use)
- FAISS indices are persisted in the `faiss_db` directory
- Uploaded files are stored in the `uploads` directory
- Both directories are created automatically
- FAISS provides very fast similarity search and is compatible with all platforms

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.
