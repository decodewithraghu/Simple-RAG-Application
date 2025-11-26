import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector database operations using FAISS."""
    
    def __init__(self, persist_directory: str = "./faiss_db", collection_name: str = "documents"):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.index_path = os.path.join(persist_directory, f"{collection_name}.index")
        self.metadata_path = os.path.join(persist_directory, f"{collection_name}.pkl")
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize or load index
        self.dimension = 384  # Default dimension for all-MiniLM-L6-v2
        self.index = None
        self.metadata_store = []
        self.document_store = []
        
        self._load_index()
        
        logger.info(f"Initialized vector store with collection: {collection_name}")
    
    @staticmethod
    def list_collections(persist_directory: str = "./faiss_db") -> List[str]:
        """List all available collections in the persist directory."""
        if not os.path.exists(persist_directory):
            return []
        
        collections = set()
        for file in os.listdir(persist_directory):
            if file.endswith('.index'):
                collection_name = file[:-6]  # Remove .index extension
                collections.add(collection_name)
        
        return sorted(list(collections))
    
    @staticmethod
    def get_collection_info(persist_directory: str = "./faiss_db") -> Dict[str, int]:
        """Get information about all collections including document counts."""
        collections_info = {}
        collections = VectorStore.list_collections(persist_directory)
        
        for collection_name in collections:
            try:
                vs = VectorStore(persist_directory, collection_name)
                collections_info[collection_name] = vs.get_collection_count()
            except Exception as e:
                logger.error(f"Error loading collection {collection_name}: {e}")
                collections_info[collection_name] = 0
        
        return collections_info
    
    def _load_index(self):
        """Load existing index or create new one."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata_store = data.get('metadata', [])
                    self.document_store = data.get('documents', [])
                logger.info(f"Loaded existing index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.warning(f"Failed to load index: {e}. Creating new index.")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata_store = []
        self.document_store = []
    
    def _save_index(self):
        """Save index and metadata to disk."""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata_store,
                    'documents': self.document_store
                }, f)
            logger.info("Saved index to disk")
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]] = None,
        ids: List[str] = None
    ):
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadata: Optional metadata for each chunk
            ids: Optional IDs for each chunk
        """
        try:
            # Convert embeddings to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Add to FAISS index
            self.index.add(embeddings_array)
            
            # Store documents and metadata
            self.document_store.extend(texts)
            
            if metadata is None:
                metadata = [{"text": text} for text in texts]
            self.metadata_store.extend(metadata)
            
            # Save to disk
            self._save_index()
            
            logger.info(f"Added {len(texts)} documents to vector store")
        
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Query the vector store.
        
        Args:
            query_embedding: Embedding vector of the query
            n_results: Number of results to return
            
        Returns:
            Dictionary containing results
        """
        try:
            if self.index.ntotal == 0:
                return {
                    'documents': [[]],
                    'metadatas': [[]],
                    'distances': [[]]
                }
            
            # Convert query to numpy array
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Search
            n_results = min(n_results, self.index.ntotal)
            distances, indices = self.index.search(query_array, n_results)
            
            # Retrieve documents and metadata
            retrieved_docs = [self.document_store[i] for i in indices[0]]
            retrieved_metadata = [self.metadata_store[i] for i in indices[0]]
            
            logger.info(f"Retrieved {n_results} results from vector store")
            
            return {
                'documents': [retrieved_docs],
                'metadatas': [retrieved_metadata],
                'distances': distances.tolist()
            }
        
        except Exception as e:
            logger.error(f"Error querying vector store: {str(e)}")
            raise
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        try:
            return self.index.ntotal if self.index else 0
        except Exception as e:
            logger.error(f"Error getting collection count: {str(e)}")
            return 0
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise
    
    def reset_collection(self):
        """Reset the collection by deleting and recreating it."""
        try:
            self.delete_collection()
            self._create_new_index()
            self._save_index()
            logger.info(f"Reset collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            raise
