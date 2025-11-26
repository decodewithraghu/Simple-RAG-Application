from typing import List
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextChunker:
    """Handles text chunking for document processing."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        # Clean the text
        text = self._clean_text(text)
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph exceeds chunk_size, save current chunk
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                current_chunk = self._get_overlap(current_chunk) + paragraph
            else:
                current_chunk += paragraph + "\n\n"
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # If no paragraphs or chunks are too large, use character-based chunking
        if not chunks or any(len(chunk) > self.chunk_size * 1.5 for chunk in chunks):
            chunks = self._character_based_chunking(text)
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Remove extra whitespace and normalize text."""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Replace multiple newlines with double newline
        text = re.sub(r'\n+', '\n\n', text)
        return text.strip()
    
    def _get_overlap(self, text: str) -> str:
        """Get the last chunk_overlap characters from text."""
        if len(text) <= self.chunk_overlap:
            return text
        return text[-self.chunk_overlap:]
    
    def _character_based_chunking(self, text: str) -> List[str]:
        """Fallback to simple character-based chunking."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence end
                sentence_end = text.rfind('. ', start, end)
                if sentence_end > start:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    space = text.rfind(' ', start, end)
                    if space > start:
                        end = space
            
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap if end < len(text) else end
        
        return chunks
