"""
High-level knowledge base operations with semantic search and citation tracking.

Provides unified interface for document ingestion, search, and retrieval.
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from src.ingestion.chunker import get_chunker
from src.ingestion.document_processor import DocumentProcessorFactory
from src.models.embeddings import get_embeddings
from src.utils.validators import ChunkData, DocumentMetadata, extract_metadata_from_filename
from .vector_store import get_vector_store


class KnowledgeBase:
    """High-level knowledge base management."""
    
    def __init__(self):
        """Initialize knowledge base."""
        self.vector_store = get_vector_store()
        self.embeddings = get_embeddings()
        self.processor_factory = DocumentProcessorFactory()
        self.chunker = get_chunker(strategy="semantic")
        
        logger.info("Initialized KnowledgeBase")
    
    def initialize(self) -> None:
        """Initialize the knowledge base (create index if needed)."""
        self.vector_store.create_index()
        logger.info("Knowledge base initialized")
    
    def ingest_document(
        self,
        file_path: Path,
        metadata_override: Optional[Dict[str, Any]] = None,
        namespace: str = "",
    ) -> Dict[str, Any]:
        """
        Ingest a single document into the knowledge base.
        
        Args:
            file_path: Path to document
            metadata_override: Optional metadata to override extracted metadata
            namespace: Optional namespace for organization
            
        Returns:
            Ingestion statistics
        """
        logger.info(f"Ingesting document: {file_path.name}")
        
        # Process document
        processed = self.processor_factory.process_document(file_path)
        if not processed:
            logger.error(f"Failed to process {file_path.name}")
            return {"success": False, "error": "Processing failed"}
        
        content = processed['content']
        doc_metadata = processed['metadata']
        
        # Extract metadata from filename
        filename_metadata = extract_metadata_from_filename(file_path.name)
        
        # Merge metadata
        base_metadata = {
            'source': str(file_path),
            'file_type': file_path.suffix.lstrip('.'),
            'file_size': file_path.stat().st_size,
            'processed_at': datetime.now().isoformat(),
        }
        base_metadata.update(doc_metadata)
        base_metadata.update(filename_metadata)
        
        if metadata_override:
            base_metadata.update(metadata_override)
        
        # Chunk text
        chunks = self.chunker.chunk(content)
        if not chunks:
            logger.warning(f"No chunks created from {file_path.name}")
            return {"success": False, "error": "No chunks created"}
        
        logger.info(f"Created {len(chunks)} chunks from {file_path.name}")
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = self.embeddings.embed_batch(chunks, show_progress=False)
        
        # Prepare data for vector store
        chunk_ids = []
        chunk_metadata = []
        
        # Prepare metadata for each chunk
        for i, chunk in enumerate(chunks):
            # Generate unique ID
            chunk_id = self._generate_chunk_id(file_path, i)
            chunk_ids.append(chunk_id)

            meta = {
                "source": str(file_path),
                "chunk_index": i,
                "total_chunks": len(chunks),
                "content": chunk[:500],  # Store preview
                **base_metadata,
            }
            # Clean metadata: remove None values (Pinecone doesn't accept null)
            cleaned_meta = {k: v for k, v in meta.items() if v is not None}
            chunk_metadata.append(cleaned_meta)
        
        # Upsert to vector store
        result = self.vector_store.upsert_batch(
            vectors=embeddings,
            ids=chunk_ids,
            metadata=chunk_metadata,
            namespace=namespace,
        )
        
        logger.info(f"Successfully ingested {file_path.name}: {result['upserted_count']} chunks")
        
        return {
            "success": True,
            "file": str(file_path),
            "chunks": len(chunks),
            "upserted": result['upserted_count'],
        }
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        namespace: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter: Metadata filter
            namespace: Optional namespace
            
        Returns:
            List of search results with content and metadata
        """
        logger.info(f"Searching knowledge base: '{query}'")
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Query vector store
        matches = self.vector_store.query(
            query_vector=query_embedding,
            top_k=top_k,
            filter=filter,
            namespace=namespace,
        )
        
        # Format results
        results = []
        for match in matches:
            results.append({
                'id': match['id'],
                'score': match['score'],
                'content': match['metadata'].get('content', ''),
                'metadata': {
                    'source': match['metadata'].get('source', ''),
                    'file_type': match['metadata'].get('file_type', ''),
                    'document_type': match['metadata'].get('document_type', ''),
                    'sector': match['metadata'].get('sector', ''),
                    'chunk_index': match['metadata'].get('chunk_index', 0),
                    'total_chunks': match['metadata'].get('total_chunks', 0),
                }
            })
        
        logger.info(f"Found {len(results)} results")
        return results
    
    def get_stats(self, namespace: str = "") -> Dict[str, Any]:
        """
        Get knowledge base statistics.
        
        Args:
            namespace: Optional namespace
            
        Returns:
            Statistics dictionary
        """
        return self.vector_store.get_stats(namespace)
    
    def delete_document(
        self,
        file_path: Path,
        namespace: str = "",
    ) -> None:
        """
        Delete all chunks from a document.
        
        Args:
            file_path: Path to document
            namespace: Optional namespace
        """
        # Delete by filter (source matches file path)
        filter = {'source': str(file_path)}
        self.vector_store.delete(filter=filter, namespace=namespace)
        logger.info(f"Deleted document: {file_path.name}")
    
    def _generate_chunk_id(self, file_path: Path, chunk_index: int) -> str:
        """
        Generate unique ID for a chunk.
        
        Args:
            file_path: Source file path
            chunk_index: Chunk index
            
        Returns:
            Unique chunk ID
        """
        # Use hash of file path + chunk index
        content = f"{file_path}_{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()
