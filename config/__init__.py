"""
Configuration module for Martin SMAS.

Provides centralized access to settings and configuration management.
"""

from pathlib import Path

# Project root
PROJECT_ROOT = Path("/home/evan/Desktop/Ecowas")

# Directory paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, METADATA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "METADATA_DIR",
    "CONFIG_DIR",
    "LOGS_DIR",
]
