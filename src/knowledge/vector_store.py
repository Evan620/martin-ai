"""
Pinecone vector store interface for knowledge base management.

Provides CRUD operations and batch upsert for document embeddings.
"""

from typing import Any, Dict, List, Optional

from loguru import logger
from pinecone import Pinecone, ServerlessSpec

from src.config.settings import get_settings


class PineconeVectorStore:
    """Interface for Pinecone vector database."""
    
    def __init__(self):
        """Initialize Pinecone vector store."""
        self.settings = get_settings()
        self.pc_settings = self.settings.pinecone
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.pc_settings.api_key)
        
        # Get or create index
        self.index_name = self.pc_settings.index_name
        self.index = None
        
        logger.info(f"Initialized PineconeVectorStore for index: {self.index_name}")
    
    def create_index(self, dimension: Optional[int] = None) -> None:
        """
        Create Pinecone index if it doesn't exist.
        
        Args:
            dimension: Vector dimension (defaults to settings)
        """
        dim = dimension or self.pc_settings.dimension
        
        # Check if index exists
        existing_indexes = self.pc.list_indexes()
        index_names = [idx['name'] for idx in existing_indexes]
        
        if self.index_name in index_names:
            logger.info(f"Index {self.index_name} already exists")
        else:
            logger.info(f"Creating index {self.index_name} with dimension {dim}")
            
            self.pc.create_index(
                name=self.index_name,
                dimension=dim,
                metric=self.pc_settings.metric,
                spec=ServerlessSpec(
                    cloud=self.pc_settings.cloud,
                    region=self.pc_settings.region
                )
            )
            
            logger.info(f"Successfully created index {self.index_name}")
        
        # Connect to index
        self.index = self.pc.Index(self.index_name)
    
    def upsert(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: List[Dict[str, Any]],
        namespace: str = "",
    ) -> Dict[str, int]:
        """
        Upsert vectors to Pinecone.
        
        Args:
            vectors: List of embedding vectors
            ids: List of unique IDs for vectors
            metadata: List of metadata dictionaries
            namespace: Optional namespace for organization
            
        Returns:
            Upsert statistics
        """
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")
        
        if len(vectors) != len(ids) or len(vectors) != len(metadata):
            raise ValueError("vectors, ids, and metadata must have same length")
        
        # Prepare data for upsert
        data = [
            {
                "id": id_,
                "values": vector,
                "metadata": meta,
            }
            for id_, vector, meta in zip(ids, vectors, metadata)
        ]
        
        try:
            response = self.index.upsert(
                vectors=data,
                namespace=namespace,
            )
            
            logger.info(f"Upserted {response['upserted_count']} vectors to {self.index_name}")
            return {"upserted_count": response['upserted_count']}
            
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {e}")
            raise
    
    def upsert_batch(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: List[Dict[str, Any]],
        batch_size: int = 100,
        namespace: str = "",
    ) -> Dict[str, int]:
        """
        Upsert vectors in batches.
        
        Args:
            vectors: List of embedding vectors
            ids: List of unique IDs
            metadata: List of metadata dictionaries
            batch_size: Batch size for upsert
            namespace: Optional namespace
            
        Returns:
            Total upsert statistics
        """
        total_upserted = 0
        total = len(vectors)
        
        for i in range(0, total, batch_size):
            batch_vectors = vectors[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            batch_metadata = metadata[i:i + batch_size]
            
            result = self.upsert(batch_vectors, batch_ids, batch_metadata, namespace)
            total_upserted += result['upserted_count']
            
            logger.debug(f"Batch {i // batch_size + 1}: Upserted {result['upserted_count']} vectors")
        
        logger.info(f"Total upserted: {total_upserted}/{total} vectors")
        return {"upserted_count": total_upserted}
    
    def query(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        namespace: str = "",
        include_metadata: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Query similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter: Metadata filter
            namespace: Optional namespace
            include_metadata: Include metadata in results
            
        Returns:
            List of matches with scores and metadata
        """
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")
        
        try:
            response = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter,
                namespace=namespace,
                include_metadata=include_metadata,
            )
            
            matches = []
            for match in response['matches']:
                matches.append({
                    'id': match['id'],
                    'score': match['score'],
                    'metadata': match.get('metadata', {}),
                })
            
            logger.debug(f"Query returned {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None,
        namespace: str = "",
        delete_all: bool = False,
    ) -> None:
        """
        Delete vectors from index.
        
        Args:
            ids: List of IDs to delete
            filter: Metadata filter for deletion
            namespace: Optional namespace
            delete_all: Delete all vectors in namespace
        """
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")
        
        try:
            if delete_all:
                self.index.delete(delete_all=True, namespace=namespace)
                logger.info(f"Deleted all vectors from namespace: {namespace}")
            elif ids:
                self.index.delete(ids=ids, namespace=namespace)
                logger.info(f"Deleted {len(ids)} vectors")
            elif filter:
                self.index.delete(filter=filter, namespace=namespace)
                logger.info(f"Deleted vectors matching filter")
            else:
                logger.warning("No deletion criteria specified")
                
        except Exception as e:
            logger.error(f"Deletion failed: {e}")
            raise
    
    def get_stats(self, namespace: str = "") -> Dict[str, Any]:
        """
        Get index statistics.
        
        Args:
            namespace: Optional namespace
            
        Returns:
            Index statistics
        """
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")
        
        try:
            stats = self.index.describe_index_stats()
            logger.info(f"Index stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise


def get_vector_store() -> PineconeVectorStore:
    """
    Factory function to get a vector store instance.
    
    Returns:
        PineconeVectorStore instance
    """
    return PineconeVectorStore()
