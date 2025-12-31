# Global Configuration for Zeo++ API
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13
# Updated: 2025-12-31 - Migrated to Pydantic Settings for type safety
# Version: 0.3.1

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    All settings can be overridden via environment variables or .env file.
    """
    
    # Application Info
    app_name: str = Field(
        default="Zeo++ Backend API",
        description="Application name"
    )
    version: str = Field(
        default="0.3.1",
        description="API version"
    )
    
    # Zeo++ Configuration
    zeo_exec_path: str = Field(
        default="./network",
        description="Path to the Zeo++ network executable"
    )
    
    # Workspace Configuration
    zeo_workspace: str = Field(
        default="workspace",
        description="Base directory for workspace"
    )
    
    # Cache Configuration
    enable_cache: bool = Field(
        default=True,
        description="Enable caching of Zeo++ computation results"
    )
    cache_max_age_hours: float = Field(
        default=168.0,  # 1 week
        description="Maximum age for cached results in hours"
    )
    
    # Security Configuration
    cors_origins: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins"
    )
    rate_limit_requests: int = Field(
        default=100,
        description="Maximum requests per minute per IP"
    )
    max_upload_size_mb: int = Field(
        default=50,
        description="Maximum file upload size in MB"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


# Create singleton settings instance
settings = Settings()

# Backward-compatible exports
WORKSPACE_ROOT = Path(settings.zeo_workspace)
TMP_DIR = WORKSPACE_ROOT / "tmp"
CACHE_DIR = WORKSPACE_ROOT / "cache"
ZEO_EXECUTABLE = settings.zeo_exec_path
ENABLE_CACHE = settings.enable_cache
LOG_LEVEL = settings.log_level
