"""
Configuration settings for Martin SMAS.

This module provides access to the centralized settings from src/config/settings.py
for backward compatibility and convenience.
"""

from src.config.settings import Settings, get_settings, reload_settings

__all__ = ["Settings", "get_settings", "reload_settings"]
