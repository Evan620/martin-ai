#!/usr/bin/env python
"""
Example script demonstrating knowledge base usage.

Shows how to ingest documents and perform semantic search.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

from src.knowledge.knowledge_base import KnowledgeBase


def example_search():
    """Example: Search the knowledge base."""
    logger.info("=" * 60)
    logger.info("Example: Semantic Search")
    logger.info("=" * 60)
    
    # Initialize knowledge base
    kb = KnowledgeBase()
    kb.initialize()
    
    # Example queries
    queries = [
        "ECOWAS Vision 2050",
        "mineral resources in West Africa",
        "renewable energy policy",
        "agricultural development strategies",
    ]
    
    for query in queries:
        logger.info(f"\nQuery: '{query}'")
        logger.info("-" * 60)
        
        results = kb.search(query, top_k=3)
        
        if not results:
            logger.info("No results found")
            continue
        
        for i, result in enumerate(results, 1):
            logger.info(f"\nResult {i} (Score: {result['score']:.4f})")
            logger.info(f"Source: {Path(result['metadata']['source']).name}")
            logger.info(f"Sector: {result['metadata'].get('sector', 'N/A')}")
            logger.info(f"Content preview: {result['content'][:200]}...")


def example_filtered_search():
    """Example: Search with metadata filters."""
    logger.info("\n" + "=" * 60)
    logger.info("Example: Filtered Search")
    logger.info("=" * 60)
    
    kb = KnowledgeBase()
    kb.initialize()
    
    # Search only in energy sector
    logger.info("\nSearching in energy sector only...")
    results = kb.search(
        query="renewable energy projects",
        top_k=3,
        filter={"sector": "energy"}
    )
    
    for i, result in enumerate(results, 1):
        logger.info(f"\nResult {i}: {Path(result['metadata']['source']).name}")
        logger.info(f"Content: {result['content'][:150]}...")


def example_stats():
    """Example: Get knowledge base statistics."""
    logger.info("\n" + "=" * 60)
    logger.info("Example: Knowledge Base Statistics")
    logger.info("=" * 60)
    
    kb = KnowledgeBase()
    kb.initialize()
    
    stats = kb.get_stats()
    logger.info(f"\nKnowledge Base Stats:")
    logger.info(f"Total vectors: {stats.get('total_vector_count', 0)}")
    logger.info(f"Dimension: {stats.get('dimension', 0)}")


def main():
    """Run all examples."""
    try:
        example_search()
        example_filtered_search()
        example_stats()
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Examples complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
