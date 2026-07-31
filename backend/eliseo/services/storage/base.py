"""Storage service abstraction for media assets."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, BinaryIO
from pydantic import BaseModel
from enum import Enum
import os
import uuid
from pathlib import Path


class StorageProviderType(str, Enum):
    """Storage provider types."""
    LOCAL = "local"
    MINIO = "minio"
    S3 = "s3"
    GCS = "gcs"
    CLOUDFLARE_R2 = "cloudflare_r2"
    BACKBLAZE_B2 = "backblaze_b2"


class StorageConfig(BaseModel):
    """Storage configuration."""
    provider_type: StorageProviderType
    bucket_name: Optional[str] = None
    region: Optional[str] = None
    endpoint_url: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    project_id: Optional[str] = None  # For GCS
    credentials_path: Optional[str] = None  # For GCS
    base_path: Optional[str] = "./storage"  # For local
    public_base_url: Optional[str] = None
    max_file_size_mb: int = 100
    allowed_extensions: list = ["png", "jpg", "jpeg", "gif", "mp4", "webm", "webp"]


class StoredFile(BaseModel):
    """Represents a stored file."""
    file_id: str
    filename: str
    url: str
    thumbnail_url: Optional[str] = None
    size_bytes: int
    content_type: str
    storage_path: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None


class BaseStorageProvider(ABC):
    """Abstract base class for storage providers."""

    def __init__(self, config: StorageConfig):
        self.config = config
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize storage connection."""
        pass

    @abstractmethod
    async def upload_file(
        self,
        file_content: BinaryIO,
        filename: str,
        content_type: str,
        folder: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StoredFile:
        """Upload a file to storage."""
        pass

    @abstractmethod
    async def download_file(self, file_id: str) -> BinaryIO:
        """Download a file from storage."""
        pass

    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from storage."""
        pass

    @abstractmethod
    async def get_file_url(self, file_id: str, expires_in_seconds: Optional[int] = None) -> str:
        """Get URL for a file."""
        pass

    @abstractmethod
    async def list_files(
        self,
        folder: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredFile]:
        """List files in storage."""
        pass

    @abstractmethod
    async def file_exists(self, file_id: str) -> bool:
        """Check if file exists."""
        pass

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on storage."""
        return {
            "provider": self.config.provider_type.value,
            "initialized": self._initialized,
            "bucket": self.config.bucket_name,
        }

    def _generate_file_id(self) -> str:
        """Generate unique file ID."""
        return str(uuid.uuid4())

    def _validate_extension(self, filename: str) -> bool:
        """Validate file extension."""
        ext = filename.split(".")[-1].lower()
        return ext in self.config.allowed_extensions

    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename."""
        ext = filename.split(".")[-1].lower()
        content_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
            "mp4": "video/mp4",
            "webm": "video/webm",
        }
        return content_types.get(ext, "application/octet-stream")
