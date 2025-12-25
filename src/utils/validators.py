"""
Data validation utilities for documents, metadata, and quality checks.

Provides validators for ensuring data quality throughout the ingestion pipeline.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class DocumentMetadata(BaseModel):
    """Document metadata schema."""
    
    source: str = Field(..., description="Source file path")
    file_type: str = Field(..., description="File type (pdf, docx, txt, etc.)")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    processed_at: str = Field(..., description="Processing timestamp")
    chunk_index: int = Field(..., ge=0, description="Chunk index")
    total_chunks: int = Field(..., ge=1, description="Total number of chunks")
    
    # Optional extracted metadata
    document_type: Optional[str] = Field(None, description="Document type (treaty, policy, etc.)")
    sector: Optional[str] = Field(None, description="Sector (minerals, energy, agriculture)")
    organization: Optional[str] = Field(None, description="Issuing organization")
    date: Optional[str] = Field(None, description="Document date")
    language: Optional[str] = Field(None, description="Document language")
    
    @field_validator("file_type")
    @classmethod
    def validate_file_type(cls, v: str) -> str:
        """Validate file type."""
        allowed_types = ["pdf", "docx", "txt", "md"]
        if v.lower() not in allowed_types:
            raise ValueError(f"File type must be one of {allowed_types}")
        return v.lower()
    
    @field_validator("sector")
    @classmethod
    def validate_sector(cls, v: Optional[str]) -> Optional[str]:
        """Validate sector."""
        if v is None:
            return v
        allowed_sectors = ["minerals", "energy", "agriculture", "investment", "general"]
        if v.lower() not in allowed_sectors:
            raise ValueError(f"Sector must be one of {allowed_sectors}")
        return v.lower()


class ChunkData(BaseModel):
    """Text chunk schema."""
    
    content: str = Field(..., min_length=1, description="Chunk text content")
    metadata: DocumentMetadata = Field(..., description="Chunk metadata")
    embedding: Optional[List[float]] = Field(None, description="Embedding vector")
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Content cannot be empty or whitespace only")
        return v
    
    @field_validator("embedding")
    @classmethod
    def validate_embedding(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Validate embedding dimension."""
        if v is not None and len(v) != 768:  # nomic-embed-text dimension
            raise ValueError(f"Embedding must have 768 dimensions, got {len(v)}")
        return v


def validate_file_path(file_path: Path) -> bool:
    """
    Validate that a file path exists and is readable.
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not file_path.exists():
        return False
    if not file_path.is_file():
        return False
    if not file_path.stat().st_size > 0:
        return False
    return True


def validate_text_quality(
    text: str,
    min_length: int = 100,
    max_length: int = 10000,
    check_language: bool = True,
) -> Dict[str, Any]:
    """
    Validate text quality.
    
    Args:
        text: Text to validate
        min_length: Minimum text length
        max_length: Maximum text length
        check_language: Whether to check language
        
    Returns:
        Validation result with 'valid' boolean and 'issues' list
    """
    issues = []
    
    # Length check
    if len(text) < min_length:
        issues.append(f"Text too short: {len(text)} < {min_length}")
    if len(text) > max_length:
        issues.append(f"Text too long: {len(text)} > {max_length}")
    
    # Whitespace check
    if len(text.strip()) < len(text) * 0.5:
        issues.append("Text contains excessive whitespace")
    
    # Alphanumeric content check
    alphanumeric_ratio = sum(c.isalnum() for c in text) / len(text) if text else 0
    if alphanumeric_ratio < 0.5:
        issues.append(f"Low alphanumeric content: {alphanumeric_ratio:.2%}")
    
    # Repetition check (simple)
    words = text.split()
    if len(words) > 10:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.3:
            issues.append(f"High word repetition: {unique_ratio:.2%} unique")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "length": len(text),
        "alphanumeric_ratio": alphanumeric_ratio,
    }


def extract_metadata_from_filename(filename: str) -> Dict[str, Optional[str]]:
    """
    Extract metadata from filename using patterns.
    
    Args:
        filename: Filename to parse
        
    Returns:
        Extracted metadata dictionary
    """
    metadata = {
        "document_type": None,
        "sector": None,
        "date": None,
    }
    
    # Document type patterns
    if re.search(r"(treaty|agreement|convention)", filename, re.IGNORECASE):
        metadata["document_type"] = "treaty"
    elif re.search(r"(policy|strategy|framework)", filename, re.IGNORECASE):
        metadata["document_type"] = "policy"
    elif re.search(r"(feasibility|study|analysis)", filename, re.IGNORECASE):
        metadata["document_type"] = "study"
    
    # Sector patterns
    if re.search(r"(mineral|mining|extractive)", filename, re.IGNORECASE):
        metadata["sector"] = "minerals"
    elif re.search(r"(energy|power|electricity|renewable)", filename, re.IGNORECASE):
        metadata["sector"] = "energy"
    elif re.search(r"(agriculture|agri|farming)", filename, re.IGNORECASE):
        metadata["sector"] = "agriculture"
    
    # Date pattern (YYYY-MM-DD or YYYY)
    date_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", filename)
    if date_match:
        metadata["date"] = date_match.group(0)
    else:
        year_match = re.search(r"(\d{4})", filename)
        if year_match:
            metadata["date"] = year_match.group(0)
    
    return metadata


def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing excessive whitespace and control characters.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove control characters except newlines and tabs
    text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)
    
    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces/tabs to single space
    text = re.sub(r"\n{3,}", "\n\n", text)  # Multiple newlines to double newline
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    
    return text.strip()
