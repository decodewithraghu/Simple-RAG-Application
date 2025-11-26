# RAG Application

A complete Retrieval-Augmented Generation (RAG) application with Progressive Web App (PWA) capabilities that allows you to upload documents, organize them into collections, process them into embeddings, store them in a vector database, and query them using Ollama for intelligent responses.

## 🚀 Features

### Core Features
- **Document Upload**: Support for PDF and TXT files
- **Collection Management**: Organize documents into collections/partitions for faster searches
- **Automatic Chunking**: Intelligently splits documents into manageable chunks
- **Vector Embeddings**: Uses sentence transformers to create embeddings
- **Vector Database**: Stores embeddings in FAISS for efficient retrieval
- **AI-Powered Queries**: Uses Ollama (llama2 or other models) to generate responses
- **Source Tracking**: View which documents and chunks were used in answers
- **Database Viewer**: Browse, view, and manage documents in the vector database

### PWA Features
- **Installable**: Install as a native app on desktop and mobile
- **Offline Support**: Service worker caching for offline functionality
- **Responsive Design**: Works seamlessly on all devices
- **Install Prompt**: User-friendly installation banner
- **Offline Indicator**: Shows when network is unavailable

### UI Features
- **Modern Interface**: Clean React-based frontend with drag-and-drop upload
- **Collection Selector**: Choose or create collections when uploading/querying
- **Real-time Status**: Shows system health and document statistics
- **Tabbed Interface**: Switch between Query and Database views
- **CRUD Operations**: Full create, read, update, delete for documents and collections

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**
- **Node.js 16+** and npm
- **Ollama** - [Install Ollama](https://ollama.ai/)

## 🛠️ Installation

### 1. Install Ollama

### 1. Install Ollama

#### macOS
```bash
# Install via Homebrew
brew install ollama

# Start Ollama service
ollama serve

# Pull a model (in a new terminal)
ollama pull llama2
```

#### Windows
1. Download Ollama installer from [https://ollama.ai/download](https://ollama.ai/download)
2. Run `OllamaSetup.exe` and follow the installation wizard
3. Ollama will automatically start as a Windows service
4. Open PowerShell or Command Prompt and pull a model:
```powershell
ollama pull llama2
```

#### Linux
```bash
# Install via curl
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull a model (in a new terminal)
ollama pull llama2
```

**Verify Installation** (All Platforms):
```bash
# Check if Ollama is running
ollama list

# Test with a simple prompt
ollama run llama2 "Hello, how are you?"
```

### 2. Backend Setup

#### macOS/Linux

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env if needed (optional)
# The default settings should work fine
```

#### Windows

**Note**: Windows Long Path support is required for PyTorch installation.

**Option 1 - Enable Long Paths (Recommended)**:
1. Open PowerShell as Administrator
2. Run: `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force`
3. Restart your terminal

**Option 2 - Use Shorter Path**:
```powershell
# Create virtual environment in shorter path
cd C:\
mkdir rag
cd rag
python -m venv venv
.\venv\Scripts\Activate.ps1

# Navigate to backend and install dependencies
cd C:\path\to\Simple-RAG-Application\backend
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install
```

## 🚀 Running the Application

### Quick Start (Recommended)

The easiest way to start both backend and frontend:

#### macOS/Linux
```bash
# From the project root directory
./start-all.sh
```

#### Windows
```powershell
# From the project root directory
.\start-all.bat
```

This script will:
- ✅ Automatically detect and use the correct Python installation
- ✅ Install missing dependencies (both backend and frontend)
- ✅ Kill any processes using ports 8000 or 3000
- ✅ Start the backend server
- ✅ Start the frontend server
- ✅ Open the application in your browser
- ✅ Display process IDs and log locations

To stop the application, press `Ctrl+C` (macOS/Linux) or any key (Windows) in the terminal.

### Manual Start

#### Start Backend Server

```bash
# In the backend directory
cd backend
python3 main.py
# or if using virtual environment
source venv/bin/activate
python main.py
```

The backend API will start at `http://localhost:8000`

You can access the API documentation at `http://localhost:8000/docs`

#### Start Frontend Server

```bash
# In the frontend directory (new terminal)
cd frontend
npm start
```

The frontend will start at `http://localhost:3000`

## 📖 Usage

### 1. Upload Documents

- Select or create a collection from the dropdown
- Drag and drop a PDF or TXT file into the upload area
- Or click "Browse Files" to select a file
- Wait for the document to be processed and chunked
- Files are organized by collection for faster searches

### 2. Query Documents

- Switch to the "🔍 Query Documents" tab
- Select which collection to search (or use "default")
- Type your question in the query box
- Select the number of source chunks to use (3-10)
- Click "Ask Question"
- View the AI-generated answer with:
  - Collection used
  - Total chunks in database
  - Chunks used in answer
  - Similarity scores
  - Source documents and text

### 3. Manage Database

- Switch to the "📊 View Database" tab
- Browse all collections in the sidebar
- View documents within each collection
- Click "View" to see document details and all chunks
- Delete individual documents or entire collections
- Monitor database statistics

### 4. Install as PWA

- Click "Install" when the installation banner appears
- App will be installed on your device
- Launch from home screen/desktop like a native app
- Works offline after installation

### 5. Monitor Status

- Check the header for:
  - Ollama availability
  - Number of uploaded documents
  - Total chunks in database

## 🏗️ Project Structure

```
Rag/
├── start-all.sh            # Main startup script (macOS/Linux)
├── start-all.bat           # Main startup script (Windows)
├── README.md
├── PWA_GUIDE.md           # PWA implementation details
├── IMPLEMENTATION_SUMMARY.md
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── start.sh                # Backend startup script
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables
│   ├── .gitignore
│   ├── faiss_db/              # FAISS vector indices by collection
│   │   ├── default/
│   │   ├── medical/
│   │   └── programming/
│   ├── uploads/               # Uploaded files
│   └── utils/
│       ├── __init__.py
│       ├── document_loader.py  # PDF/TXT loading
│       ├── text_chunker.py     # Text chunking logic
│       ├── embeddings.py       # Embedding generation & Ollama client
│       └── vector_store.py     # FAISS integration with collections
│
└── frontend/
    ├── package.json
    ├── .env                    # Frontend environment variables
    ├── public/
    │   ├── index.html
    │   ├── manifest.json       # PWA manifest
    │   ├── service-worker.js   # Service worker for offline
    │   ├── logo192.png         # PWA icons
    │   ├── logo512.png
    │   └── favicon.ico
    └── src/
        ├── index.js
        ├── index.css
        ├── App.js              # Main application component
        ├── App.css
        ├── api.js              # API client
        ├── serviceWorkerRegistration.js # PWA service worker
        └── components/
            ├── Header.js       # Header with status
            ├── Header.css
            ├── FileUpload.js   # File upload with collections
            ├── FileUpload.css
            ├── QueryInterface.js # Query interface with collections
            ├── QueryInterface.css
            ├── DatabaseViewer.js # Database management UI
            ├── DatabaseViewer.css
            ├── InstallPWA.js   # PWA install prompt
            ├── InstallPWA.css
            ├── OfflineIndicator.js # Offline status
            └── OfflineIndicator.css
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

### Health & Stats
- `GET /health` - Check system health and collection info
- `GET /stats` - Get document statistics

### Collections
- `GET /collections` - List all collections with document counts
- `GET /collections/{name}` - Get specific collection info
- `DELETE /collections/{name}` - Delete a collection

### Documents
- `POST /upload?collection={name}` - Upload a document to a collection
- `GET /collections/{name}/documents` - List documents in a collection
- `GET /collections/{name}/documents/{id}` - Get document details
- `DELETE /collections/{name}/documents/{id}` - Delete a specific document
- `DELETE /documents?collection={name}` - Delete all documents in a collection

### Chunks
- `GET /collections/{name}/chunks?limit=100&offset=0` - List chunks with pagination

### Query
- `POST /query` - Query the document database
  ```json
  {
    "query": "your question",
    "num_results": 5,
    "collection": "default"
  }
  ```

## 🔍 How It Works

1. **Document Upload**:
   - User selects a collection and uploads a PDF/TXT file
   - Backend extracts text from the document
   - Text is split into chunks (1000 chars with 200 char overlap)
   - Each chunk is converted to embeddings using sentence-transformers
   - Embeddings are stored in collection-specific FAISS vector index
   - Metadata includes document ID, filename, chunk index, and text

2. **Querying**:
   - User selects a collection and submits a question
   - Question is converted to an embedding
   - FAISS searches only the selected collection's index
   - Finds the most similar document chunks using L2 distance
   - Retrieved chunks (with metadata) are sent to Ollama as context
   - Ollama generates an answer based on the context
   - Answer, sources, similarity scores, and statistics are returned

3. **Collection Partitioning**:
   - Each collection has its own FAISS index
   - Searches only within selected collection (faster and more accurate)
   - Collections can be created on-the-fly during upload
   - Allows organizing documents by topic, department, version, etc.

4. **PWA Functionality**:
   - Service worker caches static assets
   - Offline access to previously loaded pages
   - Install prompt for native app experience
   - Background sync capabilities

## 🛡️ Technologies Used

### Backend
- **FastAPI** - Modern web framework for Python
- **FAISS** - Efficient similarity search and vector database by Facebook AI
- **Sentence Transformers** - Generate embeddings
- **PyPDF2** - PDF text extraction
- **Ollama** - Local LLM for answer generation

### Frontend
- **React 18** - UI framework
- **Axios** - HTTP client
- **React Dropzone** - File upload component
- **Service Workers** - PWA offline support
- **Web App Manifest** - PWA configuration

## 💡 Advanced Features

### Collection-Based Partitioning
Organize documents into collections for:
- **Faster searches**: Only search relevant collections
- **Better organization**: Group by topic, department, or category
- **Improved accuracy**: Reduce irrelevant results
- **Scalability**: Performance stays constant as database grows

### Database Management
- View all documents and chunks in the database
- Delete individual documents or entire collections
- Browse document details and chunk content
- Monitor collection statistics

### PWA Capabilities
- Install on any device (desktop, mobile, tablet)
- Offline access to cached content
- Native app experience
- Automatic updates
- See [PWA_GUIDE.md](PWA_GUIDE.md) for details

## 🎯 Use Cases

- **Knowledge Base**: Upload company documents, manuals, policies
- **Research Assistant**: Query research papers and technical docs
- **Customer Support**: Search through support documentation
- **Personal Library**: Organize and query personal documents
- **Multi-Department**: Separate collections per department
- **Version Control**: Different collections for document versions

## 🚨 Troubleshooting

### Application won't start
- **macOS/Linux**: Run `./start-all.sh` from the project root
- **Windows**: Run `.\start-all.bat` from the project root
- Check logs:
  - **macOS/Linux**: `/tmp/rag-backend.log` and `/tmp/rag-frontend.log`
  - **Windows**: `backend\backend.log` and `frontend\frontend.log`
- Ensure ports 8000 and 3000 are available

### Ollama not available
**Check if Ollama is running:**
- **macOS/Linux**: Run `ollama serve` in a terminal
- **Windows**: Ollama runs automatically as a service after installation
  - If not running, search for "Ollama" in Windows Start menu and launch it
  - Or restart the Ollama service from Windows Services

**Verify Ollama installation:**
```bash
# Check available models
ollama list

# Pull the model if missing
ollama pull llama2

# Test Ollama
ollama run llama2 "test"
```

**Windows-specific issues:**
- If `ollama` command not found, restart your terminal after installation
- Check if Ollama service is running: Open Task Manager > Services tab > Look for "Ollama"
- Reinstall from [https://ollama.ai/download](https://ollama.ai/download) if needed

### Dependencies missing
- Backend: `pip install -r backend/requirements.txt`
- Frontend: `cd frontend && npm install`
- Or use `./start-all.sh` which installs automatically

### Backend errors
- Check Python version: `python3 --version` (macOS/Linux) or `python --version` (Windows) - requires 3.8+
- Verify .env file exists in backend directory
- Check backend logs:
  - **macOS/Linux**: `/tmp/rag-backend.log`
  - **Windows**: `backend\backend.log`
- **Windows**: If PyTorch installation fails, see [Backend Setup for Windows](#windows)

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check REACT_APP_API_URL in `frontend/.env`
- Verify CORS settings in `backend/main.py`

### PDF upload fails
- Check file size (default max 10MB)
- Ensure PDF contains extractable text (not scanned images)
- Verify sufficient disk space

### Collection not showing documents
- Ensure documents were uploaded to the correct collection
- Refresh the database viewer
- Check backend logs for errors

### PWA not installing
- Use HTTPS or localhost
- Check if browser supports PWA (Chrome, Edge, Safari)
- Clear browser cache and reload
- Check browser console for manifest errors

## 📝 Notes

- The application uses the `all-MiniLM-L6-v2` model for embeddings (automatically downloaded on first use)
- FAISS indices are persisted in the `faiss_db/{collection_name}` directory
- Each collection has its own index and metadata
- Uploaded files are stored in the `uploads` directory
- All directories are created automatically
- FAISS provides very fast similarity search and is compatible with all platforms
- Service worker caches static assets for offline access
- PWA icons are generated automatically
- Application can be installed on any device

## 📚 Documentation

- [PWA Implementation Guide](PWA_GUIDE.md) - Complete PWA features documentation
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Collection system details
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when backend is running)

## 🚀 Quick Commands

### macOS/Linux
```bash
# Start everything
./start-all.sh

# Stop everything (from start-all.sh terminal)
Ctrl+C

# View backend logs
tail -f /tmp/rag-backend.log

# View frontend logs
tail -f /tmp/rag-frontend.log

# Test backend API
curl http://localhost:8000/health

# Test Ollama
ollama list
ollama run llama2
```

### Windows
```powershell
# Start everything
.\start-all.bat

# Stop everything (from start-all.bat window)
# Press any key

# View backend logs
Get-Content backend\backend.log -Wait

# View frontend logs
Get-Content frontend\frontend.log -Wait

# Test backend API
Invoke-WebRequest http://localhost:8000/health

# Test Ollama
ollama list
ollama run llama2
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.
