from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import uuid
import shutil
from dotenv import load_dotenv
import logging

from utils.document_loader import DocumentLoader
from utils.text_chunker import TextChunker
from utils.embeddings import EmbeddingGenerator, OllamaClient
from utils.vector_store import VectorStore

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="RAG Application API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
FAISS_PERSIST_DIR = os.getenv("FAISS_PERSIST_DIRECTORY", "./faiss_db")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB default

# Create upload directory
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize components
document_loader = DocumentLoader()
text_chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
embedding_generator = EmbeddingGenerator()
ollama_client = OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

# Cache for vector stores by collection name
vector_stores = {}

def get_vector_store(collection_name: str = "default") -> VectorStore:
    """Get or create a vector store for a specific collection."""
    if collection_name not in vector_stores:
        vector_stores[collection_name] = VectorStore(
            persist_directory=FAISS_PERSIST_DIR,
            collection_name=collection_name
        )
    return vector_stores[collection_name]


# Pydantic models
class QueryRequest(BaseModel):
    query: str
    num_results: Optional[int] = 5
    collection: Optional[str] = "default"


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    num_sources: int
    total_chunks_in_db: int
    chunks_used: int
    source_metadata: List[dict]
    collection_used: str


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_created: int
    document_id: str
    collection: str


class HealthResponse(BaseModel):
    status: str
    ollama_status: str
    documents_count: int
    collections: Dict[str, int]


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {"message": "RAG Application API is running"}


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check the health of the application and its dependencies."""
    try:
        ollama_available = ollama_client.check_health()
        
        # Get all collections info
        collections_info = VectorStore.get_collection_info(FAISS_PERSIST_DIR)
        total_docs = sum(collections_info.values())
        
        return HealthResponse(
            status="healthy",
            ollama_status="available" if ollama_available else "unavailable",
            documents_count=total_docs,
            collections=collections_info
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_document(file: UploadFile = File(...), collection: str = "default"):
    """
    Upload and process a document (PDF or text file) into a specific collection.
    
    Collections act as partitions to organize documents by category/topic.
    This allows for faster, more targeted searches.
    
    Args:
        file: The document file to upload
        collection: Name of the collection/partition (default: "default")
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.txt')):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files are supported"
            )
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIR, f"{document_id}{file_extension}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Saved file: {file.filename} as {document_id}{file_extension}")
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            text = document_loader.load_pdf(file_path)
        else:
            text = document_loader.load_text(file_path)
        
        # Chunk the text
        chunks = text_chunker.chunk_text(text)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No text could be extracted from the document")
        
        # Generate embeddings
        embeddings = embedding_generator.generate_embeddings(chunks)
        
        # Prepare metadata
        metadata = [
            {
                "document_id": document_id,
                "filename": file.filename,
                "chunk_index": i,
                "text": chunk,
                "collection": collection
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Generate IDs for chunks
        chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Get or create vector store for this collection
        vector_store = get_vector_store(collection)
        
        # Store in vector database
        vector_store.add_documents(
            texts=chunks,
            embeddings=embeddings,
            metadata=metadata,
            ids=chunk_ids
        )
        
        logger.info(f"Successfully processed document: {file.filename} into collection: {collection}")
        
        return UploadResponse(
            message="Document uploaded and processed successfully",
            filename=file.filename,
            chunks_created=len(chunks),
            document_id=document_id,
            collection=collection
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_documents(request: QueryRequest):
    """
    Query the document database using natural language.
    
    Searches within a specific collection for faster, more targeted results.
    
    Args:
        request: Query request containing the question, number of results, and collection name
    """
    try:
        # Get vector store for the specified collection
        vector_store = get_vector_store(request.collection)
        
        # Generate embedding for the query
        query_embedding = embedding_generator.generate_embeddings([request.query])[0]
        
        # Search vector database
        results = vector_store.query(
            query_embedding=query_embedding,
            n_results=request.num_results
        )
        
        # Get total chunks in database
        total_chunks = vector_store.get_collection_count()
        
        # Extract relevant chunks
        if not results['documents'] or not results['documents'][0]:
            return QueryResponse(
                query=request.query,
                answer="I couldn't find any relevant information in the uploaded documents to answer your question.",
                sources=[],
                num_sources=0,
                total_chunks_in_db=total_chunks,
                chunks_used=0,
                source_metadata=[],
                collection_used=request.collection
            )
        
        relevant_chunks = results['documents'][0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]
        
        # Prepare source metadata with additional information
        source_metadata = []
        for i, (chunk, metadata, distance) in enumerate(zip(relevant_chunks, metadatas, distances)):
            source_info = {
                "chunk_number": i + 1,
                "text": chunk,
                "filename": metadata.get("filename", "Unknown"),
                "document_id": metadata.get("document_id", "Unknown"),
                "chunk_index": metadata.get("chunk_index", -1),
                "similarity_score": float(distance) if distance else 0.0,
                "collection": metadata.get("collection", request.collection)
            }
            source_metadata.append(source_info)
        
        # Generate answer using Ollama
        answer = ollama_client.generate(
            prompt=request.query,
            context=relevant_chunks
        )
        
        logger.info(f"Successfully answered query in collection '{request.collection}': {request.query[:50]}... using {len(relevant_chunks)}/{total_chunks} chunks")
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=relevant_chunks,
            num_sources=len(relevant_chunks),
            total_chunks_in_db=total_chunks,
            chunks_used=len(relevant_chunks),
            source_metadata=source_metadata,
            collection_used=request.collection
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.delete("/documents", tags=["Documents"])
async def delete_all_documents(collection: Optional[str] = None):
    """Delete all documents from the vector database or a specific collection."""
    try:
        if collection:
            # Delete specific collection
            vector_store = get_vector_store(collection)
            vector_store.reset_collection()
            if collection in vector_stores:
                del vector_stores[collection]
            message = f"Collection '{collection}' deleted successfully"
        else:
            # Delete all collections
            collections = VectorStore.list_collections(FAISS_PERSIST_DIR)
            for coll_name in collections:
                vs = get_vector_store(coll_name)
                vs.reset_collection()
            vector_stores.clear()
            message = "All collections deleted successfully"
        
        # Clean up uploaded files
        for file in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        logger.info(message)
        return {"message": message}
    
    except Exception as e:
        logger.error(f"Error deleting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting documents: {str(e)}")


@app.get("/stats", tags=["Documents"])
async def get_stats():
    """Get statistics about the document database."""
    try:
        # Get all collections info
        collections_info = VectorStore.get_collection_info(FAISS_PERSIST_DIR)
        total_chunks = sum(collections_info.values())
        
        # Count uploaded files
        uploaded_files = len([f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))])
        
        return {
            "total_chunks": total_chunks,
            "uploaded_files": uploaded_files,
            "collections": collections_info,
            "num_collections": len(collections_info)
        }
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.get("/collections", tags=["Collections"])
async def list_collections():
    """List all available collections/partitions."""
    try:
        collections_info = VectorStore.get_collection_info(FAISS_PERSIST_DIR)
        return {
            "collections": collections_info,
            "total_collections": len(collections_info),
            "total_documents": sum(collections_info.values())
        }
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing collections: {str(e)}")


@app.get("/collections/{collection_name}", tags=["Collections"])
async def get_collection_info(collection_name: str):
    """Get information about a specific collection."""
    try:
        vector_store = get_vector_store(collection_name)
        doc_count = vector_store.get_collection_count()
        
        return {
            "collection_name": collection_name,
            "document_count": doc_count,
            "exists": doc_count > 0
        }
    except Exception as e:
        logger.error(f"Error getting collection info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting collection info: {str(e)}")


@app.delete("/collections/{collection_name}", tags=["Collections"])
async def delete_collection(collection_name: str):
    """Delete a specific collection."""
    try:
        vector_store = get_vector_store(collection_name)
        vector_store.reset_collection()
        
        if collection_name in vector_stores:
            del vector_stores[collection_name]
        
        logger.info(f"Deleted collection: {collection_name}")
        return {"message": f"Collection '{collection_name}' deleted successfully"}
    
    except Exception as e:
        logger.error(f"Error deleting collection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting collection: {str(e)}")


@app.get("/collections/{collection_name}/documents", tags=["Documents"])
async def list_documents_in_collection(collection_name: str):
    """List all documents in a specific collection with their chunks."""
    try:
        vector_store = get_vector_store(collection_name)
        
        if not hasattr(vector_store, 'metadata_store') or not vector_store.metadata_store:
            return {
                "collection_name": collection_name,
                "documents": [],
                "total_documents": 0,
                "total_chunks": 0
            }
        
        # Group chunks by document_id
        documents_dict = {}
        for metadata in vector_store.metadata_store:
            doc_id = metadata.get("document_id", "unknown")
            if doc_id not in documents_dict:
                documents_dict[doc_id] = {
                    "document_id": doc_id,
                    "filename": metadata.get("filename", "Unknown"),
                    "collection": collection_name,
                    "chunks": []
                }
            
            documents_dict[doc_id]["chunks"].append({
                "chunk_index": metadata.get("chunk_index", -1),
                "text": metadata.get("text", ""),
                "preview": metadata.get("text", "")[:100] + "..." if len(metadata.get("text", "")) > 100 else metadata.get("text", "")
            })
        
        # Convert to list and sort chunks
        documents = []
        for doc in documents_dict.values():
            doc["chunks"].sort(key=lambda x: x["chunk_index"])
            doc["num_chunks"] = len(doc["chunks"])
            documents.append(doc)
        
        return {
            "collection_name": collection_name,
            "documents": documents,
            "total_documents": len(documents),
            "total_chunks": sum(doc["num_chunks"] for doc in documents)
        }
    
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@app.get("/collections/{collection_name}/documents/{document_id}", tags=["Documents"])
async def get_document_details(collection_name: str, document_id: str):
    """Get detailed information about a specific document."""
    try:
        vector_store = get_vector_store(collection_name)
        
        if not hasattr(vector_store, 'metadata_store') or not vector_store.metadata_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Find all chunks for this document
        chunks = []
        filename = None
        for metadata in vector_store.metadata_store:
            if metadata.get("document_id") == document_id:
                if filename is None:
                    filename = metadata.get("filename", "Unknown")
                chunks.append({
                    "chunk_index": metadata.get("chunk_index", -1),
                    "text": metadata.get("text", "")
                })
        
        if not chunks:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Sort by chunk index
        chunks.sort(key=lambda x: x["chunk_index"])
        
        return {
            "document_id": document_id,
            "filename": filename,
            "collection": collection_name,
            "num_chunks": len(chunks),
            "chunks": chunks
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting document details: {str(e)}")


@app.delete("/collections/{collection_name}/documents/{document_id}", tags=["Documents"])
async def delete_document(collection_name: str, document_id: str):
    """Delete a specific document and all its chunks from a collection."""
    try:
        vector_store = get_vector_store(collection_name)
        
        if not hasattr(vector_store, 'metadata_store') or not vector_store.metadata_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Find indices of chunks belonging to this document
        indices_to_delete = []
        chunks_to_delete = 0
        filename = None
        
        for i, metadata in enumerate(vector_store.metadata_store):
            if metadata.get("document_id") == document_id:
                indices_to_delete.append(i)
                chunks_to_delete += 1
                if filename is None:
                    filename = metadata.get("filename", "Unknown")
        
        if not indices_to_delete:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from index (in reverse order to maintain indices)
        import numpy as np
        import faiss
        
        # Create new index without the deleted vectors
        remaining_indices = [i for i in range(len(vector_store.metadata_store)) if i not in indices_to_delete]
        
        if remaining_indices:
            # Get remaining vectors
            remaining_vectors = np.array([vector_store.index.reconstruct(i) for i in remaining_indices])
            remaining_metadata = [vector_store.metadata_store[i] for i in remaining_indices]
            
            # Create new index
            dimension = vector_store.index.d
            new_index = faiss.IndexFlatL2(dimension)
            new_index.add(remaining_vectors)
            
            vector_store.index = new_index
            vector_store.metadata_store = remaining_metadata
        else:
            # No remaining documents, reset collection
            vector_store.reset_collection()
        
        # Save the updated index
        vector_store._save_index()
        
        # Delete the uploaded file if it exists
        for file in os.listdir(UPLOAD_DIR):
            if file.startswith(document_id):
                file_path = os.path.join(UPLOAD_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted file: {file}")
        
        logger.info(f"Deleted document {document_id} ({filename}) with {chunks_to_delete} chunks from collection {collection_name}")
        
        return {
            "message": f"Document deleted successfully",
            "document_id": document_id,
            "filename": filename,
            "chunks_deleted": chunks_to_delete,
            "collection": collection_name
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@app.get("/collections/{collection_name}/chunks", tags=["Chunks"])
async def list_chunks(collection_name: str, limit: int = 100, offset: int = 0):
    """List all chunks in a collection with pagination."""
    try:
        vector_store = get_vector_store(collection_name)
        
        if not hasattr(vector_store, 'metadata_store') or not vector_store.metadata_store:
            return {
                "collection_name": collection_name,
                "chunks": [],
                "total_chunks": 0,
                "limit": limit,
                "offset": offset
            }
        
        total_chunks = len(vector_store.metadata_store)
        chunks_slice = vector_store.metadata_store[offset:offset + limit]
        
        chunks = [
            {
                "chunk_id": f"{meta.get('document_id', 'unknown')}_chunk_{meta.get('chunk_index', -1)}",
                "document_id": meta.get("document_id", "unknown"),
                "filename": meta.get("filename", "Unknown"),
                "chunk_index": meta.get("chunk_index", -1),
                "text": meta.get("text", ""),
                "preview": meta.get("text", "")[:100] + "..." if len(meta.get("text", "")) > 100 else meta.get("text", ""),
                "collection": collection_name
            }
            for meta in chunks_slice
        ]
        
        return {
            "collection_name": collection_name,
            "chunks": chunks,
            "total_chunks": total_chunks,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_chunks
        }
    
    except Exception as e:
        logger.error(f"Error listing chunks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing chunks: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
