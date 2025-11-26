from typing import List
import requests
import logging
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for text using sentence transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(texts, show_progress_bar=True)
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Base URL of Ollama API
            model: Model name to use for generation
        """
        self.base_url = base_url
        self.model = model
        logger.info(f"Initialized Ollama client with model: {model}")
    
    def generate(self, prompt: str, context: List[str] = None) -> str:
        """
        Generate response using Ollama.
        
        Args:
            prompt: User query
            context: List of context strings to include
            
        Returns:
            Generated response
        """
        try:
            # Build the full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info("Successfully generated response from Ollama")
            return result.get("response", "")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def _build_prompt(self, query: str, context: List[str] = None) -> str:
        """Build prompt with context."""
        if not context:
            return query
        
        context_text = "\n\n".join(context)
        prompt = f"""Based on the following context, please answer the question.

Context:
{context_text}

Question: {query}

Answer:"""
        return prompt
    
    def check_health(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
