"""
Embedding generation using Ollama's nomic-embed-text model.

Provides batch embedding generation with caching and error handling.
"""

from typing import List, Optional

import requests
from loguru import logger

from src.config.settings import get_settings


class OllamaEmbeddings:
    """Interface for Ollama embedding models."""
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize Ollama embeddings interface.
        
        Args:
            model: Embedding model name (defaults to nomic-embed-text)
        """
        self.settings = get_settings()
        self.model = model or self.settings.ollama.embedding_model
        self.base_url = self.settings.ollama.base_url
        self.dimension = 768  # nomic-embed-text dimension
        
        logger.info(f"Initialized OllamaEmbeddings with model: {self.model}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                },
                timeout=30,
            )
            response.raise_for_status()
            
            embedding = response.json()["embedding"]
            
            if len(embedding) != self.dimension:
                logger.warning(
                    f"Unexpected embedding dimension: {len(embedding)} (expected {self.dimension})"
                )
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True,
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with batching.
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once
            show_progress: Whether to show progress bar
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        total = len(texts)
        
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(range(0, total, batch_size), desc="Generating embeddings")
            except ImportError:
                iterator = range(0, total, batch_size)
        else:
            iterator = range(0, total, batch_size)
        
        for i in iterator:
            batch = texts[i:i + batch_size]
            
            for text in batch:
                try:
                    embedding = self.embed_text(text)
                    embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"Failed to embed text at index {i}: {e}")
                    # Add zero vector as placeholder
                    embeddings.append([0.0] * self.dimension)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    def embed_documents(
        self,
        documents: List[str],
        **kwargs,
    ) -> List[List[float]]:
        """
        Generate embeddings for documents (alias for embed_batch).
        
        Args:
            documents: List of document texts
            **kwargs: Additional parameters for embed_batch
            
        Returns:
            List of embedding vectors
        """
        return self.embed_batch(documents, **kwargs)
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query (alias for embed_text).
        
        Args:
            query: Search query text
            
        Returns:
            Embedding vector
        """
        return self.embed_text(query)
    
    def check_health(self) -> bool:
        """
        Check if embedding model is available.
        
        Returns:
            True if model is accessible, False otherwise
        """
        try:
            test_embedding = self.embed_text("test")
            return len(test_embedding) == self.dimension
        except Exception as e:
            logger.error(f"Embedding model health check failed: {e}")
            return False


def get_embeddings(model: Optional[str] = None) -> OllamaEmbeddings:
    """
    Factory function to get an embeddings instance.
    
    Args:
        model: Embedding model name
        
    Returns:
        OllamaEmbeddings instance
    """
    return OllamaEmbeddings(model=model)
