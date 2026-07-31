"""Local filesystem storage provider."""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime
import aiofiles

from eliseo.services.storage.base import (
    BaseStorageProvider,
    StorageConfig,
    StoredFile,
    StorageProviderType,
)


class LocalStorageProvider(BaseStorageProvider):
    """Local filesystem storage provider for VPS-first deployment."""

    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.base_path = Path(config.base_path or "./storage")
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize local storage."""
        try:
            # Create base directory if it doesn't exist
            self.base_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories for organization
            (self.base_path / "images").mkdir(exist_ok=True)
            (self.base_path / "videos").mkdir(exist_ok=True)
            (self.base_path / "thumbnails").mkdir(exist_ok=True)
            (self.base_path / "temp").mkdir(exist_ok=True)
            
            self._initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize local storage: {e}")
            return False

    async def upload_file(
        self,
        file_content: BinaryIO,
        filename: str,
        content_type: str,
        folder: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StoredFile:
        """Upload file to local storage."""
        if not self._initialized:
            raise RuntimeError("Storage not initialized")

        if not self._validate_extension(filename):
            raise ValueError(f"Invalid file extension: {filename}")

        file_id = self._generate_file_id()
        ext = filename.split(".")[-1].lower()
        
        # Determine folder based on content type or explicit folder
        if not folder:
            if "image" in content_type:
                folder = "images"
            elif "video" in content_type:
                folder = "videos"
            else:
                folder = "files"

        # Create folder path
        folder_path = self.base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        # Save file
        storage_filename = f"{file_id}.{ext}"
        file_path = folder_path / storage_filename

        # Write file asynchronously
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content.read())

        # Get file size
        file_size = file_path.stat().st_size

        # Generate URL
        relative_path = f"{folder}/{storage_filename}"
        url = self._generate_url(relative_path)

        return StoredFile(
            file_id=file_id,
            filename=filename,
            url=url,
            size_bytes=file_size,
            content_type=content_type,
            storage_path=str(file_path),
            metadata=metadata,
            created_at=datetime.utcnow().isoformat(),
        )

    async def download_file(self, file_id: str) -> BinaryIO:
        """Download file from local storage."""
        # Search for file in all folders
        for folder in ["images", "videos", "files", "thumbnails"]:
            folder_path = self.base_path / folder
            for file in folder_path.glob(f"{file_id}.*"):
                return open(file, 'rb')
        
        raise FileNotFoundError(f"File not found: {file_id}")

    async def delete_file(self, file_id: str) -> bool:
        """Delete file from local storage."""
        for folder in ["images", "videos", "files", "thumbnails"]:
            folder_path = self.base_path / folder
            for file in folder_path.glob(f"{file_id}.*"):
                file.unlink()
                return True
        return False

    async def get_file_url(self, file_id: str, expires_in_seconds: Optional[int] = None) -> str:
        """Get URL for file (local files don't expire)."""
        for folder in ["images", "videos", "files", "thumbnails"]:
            folder_path = self.base_path / folder
            for file in folder_path.glob(f"{file_id}.*"):
                relative_path = f"{folder}/{file.name}"
                return self._generate_url(relative_path)
        
        raise FileNotFoundError(f"File not found: {file_id}")

    async def list_files(
        self,
        folder: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredFile]:
        """List files in local storage."""
        files = []
        search_folders = [folder] if folder else ["images", "videos", "files"]

        for search_folder in search_folders:
            folder_path = self.base_path / search_folder
            if not folder_path.exists():
                continue

            for file_path in folder_path.glob("*"):
                if file_path.is_file():
                    file_id = file_path.stem
                    files.append(StoredFile(
                        file_id=file_id,
                        filename=file_path.name,
                        url=self._generate_url(f"{search_folder}/{file_path.name}"),
                        size_bytes=file_path.stat().st_size,
                        content_type=self._get_content_type(file_path.name),
                        storage_path=str(file_path),
                        created_at=datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                    ))

                    if len(files) >= limit:
                        break
            
            if len(files) >= limit:
                break

        return files[offset:offset + limit]

    async def file_exists(self, file_id: str) -> bool:
        """Check if file exists in local storage."""
        for folder in ["images", "videos", "files", "thumbnails"]:
            folder_path = self.base_path / folder
            if any(folder_path.glob(f"{file_id}.*")):
                return True
        return False

    def _generate_url(self, relative_path: str) -> str:
        """Generate URL for local file."""
        if self.config.public_base_url:
            return f"{self.config.public_base_url}/{relative_path}"
        else:
            # Return local path for development
            return f"/storage/{relative_path}"

    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Clean up temporary files older than specified age."""
        temp_path = self.base_path / "temp"
        if not temp_path.exists():
            return 0

        deleted_count = 0
        now = datetime.utcnow()

        for file_path in temp_path.glob("*"):
            if file_path.is_file():
                file_age = now - datetime.fromtimestamp(file_path.stat().st_ctime)
                if file_age.total_seconds() > max_age_hours * 3600:
                    file_path.unlink()
                    deleted_count += 1

        return deleted_count
