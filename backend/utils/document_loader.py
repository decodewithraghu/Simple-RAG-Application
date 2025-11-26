import os
from typing import List
from PyPDF2 import PdfReader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentLoader:
    """Handles loading and extracting text from PDF documents."""
    
    @staticmethod
    def load_pdf(file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        try:
            reader = PdfReader(file_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            logger.info(f"Successfully extracted text from {file_path}")
            return text
        
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            raise Exception(f"Failed to load PDF: {str(e)}")
    
    @staticmethod
    def load_text(file_path: str) -> str:
        """
        Load text from a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Content of the text file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Successfully loaded text from {file_path}")
            return text
        
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {str(e)}")
            raise Exception(f"Failed to load text file: {str(e)}")
