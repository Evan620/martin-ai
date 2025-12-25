#!/usr/bin/env python
"""
Project initialization script.

Sets up directories, validates environment, and initializes Pinecone index.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

from src.config.settings import get_settings
from src.knowledge.vector_store import get_vector_store
from src.models.embeddings import get_embeddings
from src.models.llm_interface import get_llm


def create_directories():
    """Create necessary project directories."""
    logger.info("Creating project directories...")
    
    settings = get_settings()
    paths = settings.paths
    
    directories = [
        paths.raw_data_dir,
        paths.processed_data_dir,
        paths.metadata_dir,
        paths.logs_dir,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Created: {directory}")


def validate_environment():
    """Validate environment variables and dependencies."""
    logger.info("Validating environment...")
    
    settings = get_settings()
    
    # Check API keys
    if not settings.pinecone.api_key:
        logger.error("✗ PINECONE_API_KEY not set")
        return False
    logger.info("✓ Pinecone API key configured")
    
    # Check Ollama connectivity
    try:
        llm = get_llm()
        if llm.check_health():
            logger.info("✓ Ollama service is accessible")
            
            # List available models
            models = llm.list_models()
            logger.info(f"✓ Available models: {', '.join(models)}")
        else:
            logger.error("✗ Ollama service is not accessible")
            return False
    except Exception as e:
        logger.error(f"✗ Failed to connect to Ollama: {e}")
        return False
    
    # Check embedding model
    try:
        embeddings = get_embeddings()
        if embeddings.check_health():
            logger.info("✓ Embedding model is accessible")
        else:
            logger.error("✗ Embedding model is not accessible")
            return False
    except Exception as e:
        logger.error(f"✗ Failed to check embedding model: {e}")
        return False
    
    return True


def initialize_pinecone():
    """Initialize Pinecone index."""
    logger.info("Initializing Pinecone index...")
    
    try:
        vector_store = get_vector_store()
        vector_store.create_index()
        
        # Get stats
        stats = vector_store.get_stats()
        logger.info(f"✓ Pinecone index initialized: {stats}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Failed to initialize Pinecone: {e}")
        return False


def main():
    """Main initialization function."""
    logger.info("=" * 60)
    logger.info("Martin SMAS - Project Initialization")
    logger.info("=" * 60)
    
    # Step 1: Create directories
    create_directories()
    logger.info("")
    
    # Step 2: Validate environment
    if not validate_environment():
        logger.error("Environment validation failed. Please check your configuration.")
        sys.exit(1)
    logger.info("")
    
    # Step 3: Initialize Pinecone
    if not initialize_pinecone():
        logger.error("Pinecone initialization failed. Please check your API key and settings.")
        sys.exit(1)
    logger.info("")
    
    logger.info("=" * 60)
    logger.info("✓ Project initialization complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Place documents in: data/raw/")
    logger.info("2. Run: python scripts/ingest/batch_ingest.py")
    logger.info("3. Query the knowledge base using src.knowledge.KnowledgeBase")


if __name__ == "__main__":
    main()
