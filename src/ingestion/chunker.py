"""
Text chunking strategies for document ingestion.

Provides semantic and fixed-size chunking with overlap for optimal retrieval.
"""

import re
from typing import List

from loguru import logger


class TextChunker:
    """Base class for text chunking strategies."""
    
    def chunk(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Input text
            
        Returns:
            List of text chunks
        """
        raise NotImplementedError("Subclasses must implement chunk()")


class FixedSizeChunker(TextChunker):
    """Fixed-size chunking with overlap."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize fixed-size chunker.
        
        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, text: str) -> List[str]:
        """Split text into fixed-size chunks with overlap."""
        if not text.strip():
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings within the last 20% of the chunk
                search_start = end - int(self.chunk_size * 0.2)
                search_text = text[search_start:end + 50]
                
                # Find last sentence ending
                match = None
                for pattern in [r'\. ', r'\.\n', r'! ', r'!\n', r'\? ', r'\?\n']:
                    matches = list(re.finditer(pattern, search_text))
                    if matches:
                        match = matches[-1]
                        break
                
                if match:
                    end = search_start + match.end()
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Ensure we make progress
            if start <= chunks[-1] if chunks else 0:
                start = end
        
        logger.debug(f"Created {len(chunks)} fixed-size chunks")
        return chunks


class SemanticChunker(TextChunker):
    """Semantic chunking based on sentence boundaries."""
    
    def __init__(
        self,
        max_chunk_size: int = 1500,
        min_chunk_size: int = 500,
    ):
        """
        Initialize semantic chunker.
        
        Args:
            max_chunk_size: Maximum chunk size in characters
            min_chunk_size: Minimum chunk size in characters
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
    
    def chunk(self, text: str) -> List[str]:
        """Split text into semantic chunks based on sentences."""
        if not text.strip():
            return []
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            # If adding this sentence exceeds max size and we have content
            if current_size + sentence_size > self.max_chunk_size and current_chunk:
                # Save current chunk if it meets minimum size
                chunk_text = ' '.join(current_chunk).strip()
                if len(chunk_text) >= self.min_chunk_size:
                    chunks.append(chunk_text)
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk).strip()
            if chunk_text:
                chunks.append(chunk_text)
        
        logger.debug(f"Created {len(chunks)} semantic chunks")
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be enhanced with NLTK/spaCy)
        # Split on period, exclamation, question mark followed by space or newline
        pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(pattern, text)
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences


class RecursiveChunker(TextChunker):
    """Recursive chunking with hierarchy-aware splitting."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None,
    ):
        """
        Initialize recursive chunker.
        
        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            separators: List of separators in order of preference
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
    
    def chunk(self, text: str) -> List[str]:
        """Split text recursively using hierarchy of separators."""
        if not text.strip():
            return []
        
        return self._recursive_split(text, self.separators)
    
    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively split text using separators.
        
        Args:
            text: Text to split
            separators: Remaining separators to try
            
        Returns:
            List of chunks
        """
        if not separators:
            # No more separators, return as single chunk
            return [text] if text.strip() else []
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        # Split by current separator
        if separator:
            splits = text.split(separator)
        else:
            # Last resort: character-level split
            splits = list(text)
        
        # Merge splits into chunks
        chunks = []
        current_chunk = []
        current_size = 0
        
        for split in splits:
            split_size = len(split)
            
            if current_size + split_size <= self.chunk_size:
                current_chunk.append(split)
                current_size += split_size + len(separator)
            else:
                # Save current chunk
                if current_chunk:
                    chunk_text = separator.join(current_chunk)
                    if len(chunk_text) > self.chunk_size and remaining_separators:
                        # Chunk still too large, split recursively
                        chunks.extend(self._recursive_split(chunk_text, remaining_separators))
                    else:
                        chunks.append(chunk_text)
                
                # Start new chunk
                current_chunk = [split]
                current_size = split_size
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = separator.join(current_chunk)
            if len(chunk_text) > self.chunk_size and remaining_separators:
                chunks.extend(self._recursive_split(chunk_text, remaining_separators))
            else:
                chunks.append(chunk_text)
        
        logger.debug(f"Created {len(chunks)} recursive chunks")
        return [c.strip() for c in chunks if c.strip()]


def get_chunker(strategy: str = "semantic", **kwargs) -> TextChunker:
    """
    Factory function to get a chunker instance.
    
    Args:
        strategy: Chunking strategy ("fixed", "semantic", "recursive")
        **kwargs: Additional parameters for chunker
        
    Returns:
        TextChunker instance
    """
    if strategy == "fixed":
        return FixedSizeChunker(**kwargs)
    elif strategy == "semantic":
        return SemanticChunker(**kwargs)
    elif strategy == "recursive":
        return RecursiveChunker(**kwargs)
    else:
        logger.warning(f"Unknown chunking strategy: {strategy}, using semantic")
        return SemanticChunker(**kwargs)
