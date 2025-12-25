#!/usr/bin/env python
"""
Batch document ingestion script.

Processes all documents in data/raw/ and ingests them into the knowledge base.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from tqdm import tqdm

from src.config.settings import get_settings
from src.knowledge.knowledge_base import KnowledgeBase


def get_documents(data_dir: Path, extensions: list = None) -> list[Path]:
    """
    Get all documents from directory.
    
    Args:
        data_dir: Directory to search
        extensions: List of file extensions to include
        
    Returns:
        List of document paths
    """
    if extensions is None:
        extensions = ['.pdf', '.docx', '.txt', '.md']
    
    documents = []
    for ext in extensions:
        documents.extend(data_dir.glob(f'**/*{ext}'))
    
    return sorted(documents)


def main():
    """Main batch ingestion function."""
    logger.info("=" * 60)
    logger.info("Martin SMAS - Batch Document Ingestion")
    logger.info("=" * 60)
    
    # Initialize knowledge base
    kb = KnowledgeBase()
    kb.initialize()
    
    # Get settings
    settings = get_settings()
    raw_data_dir = settings.paths.raw_data_dir
    
    logger.info(f"Scanning directory: {raw_data_dir}")
    
    # Get all documents
    documents = get_documents(raw_data_dir)
    
    if not documents:
        logger.warning(f"No documents found in {raw_data_dir}")
        logger.info("Please place documents in data/raw/ and try again")
        return
    
    logger.info(f"Found {len(documents)} documents to process")
    logger.info("")
    
    # Process documents
    results = {
        'success': 0,
        'failed': 0,
        'total_chunks': 0,
    }
    
    failed_files = []
    
    for doc_path in tqdm(documents, desc="Ingesting documents"):
        try:
            result = kb.ingest_document(doc_path)
            
            if result['success']:
                results['success'] += 1
                results['total_chunks'] += result['chunks']
                logger.info(f"✓ {doc_path.name}: {result['chunks']} chunks")
            else:
                results['failed'] += 1
                failed_files.append((doc_path.name, result.get('error', 'Unknown error')))
                logger.error(f"✗ {doc_path.name}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            results['failed'] += 1
            failed_files.append((doc_path.name, str(e)))
            logger.error(f"✗ {doc_path.name}: {e}")
    
    # Print summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Ingestion Summary")
    logger.info("=" * 60)
    logger.info(f"Total documents: {len(documents)}")
    logger.info(f"Successfully ingested: {results['success']}")
    logger.info(f"Failed: {results['failed']}")
    logger.info(f"Total chunks created: {results['total_chunks']}")
    
    if failed_files:
        logger.info("")
        logger.info("Failed files:")
        for filename, error in failed_files:
            logger.info(f"  - {filename}: {error}")
    
    # Get knowledge base stats
    logger.info("")
    stats = kb.get_stats()
    logger.info(f"Knowledge base stats: {stats}")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✓ Batch ingestion complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
