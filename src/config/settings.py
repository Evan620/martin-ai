"""
Configuration management for Martin SMAS.

Centralized settings using Pydantic for type safety and validation.
Loads configuration from environment variables and YAML files.
"""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    """Ollama LLM configuration."""
    
    base_url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    api_key: str = Field(default="sk-ollama", description="Ollama API key")
    default_model: str = Field(default="qwen2.5:14b", description="Default LLM model")
    embedding_model: str = Field(default="nomic-embed-text", description="Embedding model")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=2048, ge=1, description="Maximum tokens to generate")
    timeout: int = Field(default=120, ge=1, description="Request timeout in seconds")
    
    model_config = SettingsConfigDict(env_prefix="OLLAMA_")


class PineconeSettings(BaseSettings):
    """Pinecone vector database settings."""
    
    api_key: str = Field(
        default="",
        description="Pinecone API key"
    )
    environment: str = Field(
        default="us-west1-gcp",
        description="Pinecone environment"
    )
    index_name: str = Field(
        default="ecowas-summit-kb",
        description="Pinecone index name"
    )
    dimension: int = Field(
        default=768,
        description="Vector dimension (must match embedding model)"
    )
    metric: str = Field(
        default="cosine",
        description="Distance metric"
    )
    cloud: str = Field(
        default="aws",
        description="Cloud provider"
    )
    region: str = Field(
        default="us-east-1",
        description="Cloud region"
    )
    
    model_config = SettingsConfigDict(
        env_prefix="PINECONE_",
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class IngestionSettings(BaseSettings):
    """Document ingestion configuration."""
    
    chunk_size: int = Field(default=1000, ge=100, description="Text chunk size in characters")
    chunk_overlap: int = Field(default=200, ge=0, description="Overlap between chunks")
    batch_size: int = Field(default=100, ge=1, description="Batch size for processing")
    max_workers: int = Field(default=4, ge=1, description="Number of parallel workers")
    enable_ocr: bool = Field(default=True, description="Enable OCR for scanned documents")
    supported_formats: list[str] = Field(
        default=["pdf", "docx", "txt", "md"],
        description="Supported document formats"
    )
    
    model_config = SettingsConfigDict(env_prefix="INGESTION_")


class PathSettings(BaseSettings):
    """Project path configuration."""
    
    project_root: Path = Field(default_factory=lambda: Path("/home/evan/Desktop/Ecowas"))
    
    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"
    
    @property
    def raw_data_dir(self) -> Path:
        return self.data_dir / "raw"
    
    @property
    def processed_data_dir(self) -> Path:
        return self.data_dir / "processed"
    
    @property
    def metadata_dir(self) -> Path:
        return self.data_dir / "metadata"
    
    @property
    def config_dir(self) -> Path:
        return self.project_root / "config"
    
    @property
    def logs_dir(self) -> Path:
        return self.project_root / "logs"


class Settings(BaseSettings):
    """Main application settings."""
    
    # API Keys
    google_api_key: Optional[str] = Field(default=None, description="Google API key")
    
    # Sub-configurations
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    pinecone: PineconeSettings = Field(default_factory=lambda: PineconeSettings())
    ingestion: IngestionSettings = Field(default_factory=IngestionSettings)
    paths: PathSettings = Field(default_factory=PathSettings)
    
    # General settings
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Debug mode")
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global settings
    settings = Settings()
    return settings
