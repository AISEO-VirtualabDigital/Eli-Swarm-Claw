"""Storage service abstraction for media assets."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path
import os
import uuid
from datetime import datetime


class StorageProvider(ABC):
    """Abstract base class for storage providers."""

    @abstractmethod
    async def upload(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        organization_id: int,
        project_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Upload a file and return metadata."""
        pass

    @abstractmethod
    async def download(self, file_path: str) -> BinaryIO:
        """Download a file."""
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """Delete a file."""
        pass

    @abstractmethod
    async def get_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get a URL for accessing the file."""
        pass

    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        pass


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider (VPS-first approach)."""

    def __init__(self, base_path: str = "/app/storage/media"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_file_path(
        self,
        filename: str,
        organization_id: int,
        project_id: Optional[int] = None,
        job_id: Optional[str] = None,
    ) -> Path:
        """Generate structured file path."""
        # Create directory structure: org/{org_id}/project/{project_id}/media/{job_id}/filename
        path = self.base_path / "organizations" / str(organization_id)
        
        if project_id:
            path = path / "projects" / str(project_id)
        
        path = path / "media"
        
        if job_id:
            path = path / job_id
        
        path.mkdir(parents=True, exist_ok=True)
        return path / filename

    async def upload(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        organization_id: int,
        project_id: Optional[int] = None,
        job_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Upload file to local storage."""
        import shutil
        
        file_path = self._get_file_path(filename, organization_id, project_id, job_id)
        
        # Save file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file, f)
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Generate public URL (in production, this would be behind nginx or CDN)
        public_url = f"/storage/{file_path.relative_to(self.base_path)}"
        
        return {
            "file_path": str(file_path),
            "public_url": public_url,
            "content_type": content_type,
            "size_bytes": file_size,
            "storage_type": "local",
            "uploaded_at": datetime.utcnow().isoformat(),
        }

    async def download(self, file_path: str) -> BinaryIO:
        """Download file from local storage."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return open(path, "rb")

    async def delete(self, file_path: str) -> bool:
        """Delete file from local storage."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False

    async def get_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get URL for local file."""
        path = Path(file_path)
        if path.exists():
            return f"/storage/{path.relative_to(self.base_path)}"
        raise FileNotFoundError(f"File not found: {file_path}")

    async def exists(self, file_path: str) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()


class MinIOStorageProvider(StorageProvider):
    """MinIO/S3-compatible storage provider."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str = "eliclaw-media",
        secure: bool = False,
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.secure = secure
        self._client = None

    def _get_client(self):
        """Lazy initialize MinIO client."""
        if self._client is None:
            try:
                from minio import Minio
                self._client = Minio(
                    self.endpoint,
                    access_key=self.access_key,
                    secret_key=self.secret_key,
                    secure=self.secure,
                )
                # Ensure bucket exists
                if not self._client.bucket_exists(self.bucket):
                    self._client.make_bucket(self.bucket)
            except ImportError:
                raise ImportError("minio package required: pip install minio")
        return self._client

    def _get_object_path(
        self,
        filename: str,
        organization_id: int,
        project_id: Optional[int] = None,
        job_id: Optional[str] = None,
    ) -> str:
        """Generate S3 object key."""
        path = f"organizations/{organization_id}"
        
        if project_id:
            path += f"/projects/{project_id}"
        
        path += "/media"
        
        if job_id:
            path += f"/{job_id}"
        
        path += f"/{filename}"
        return path

    async def upload(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        organization_id: int,
        project_id: Optional[int] = None,
        job_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Upload file to MinIO."""
        import io
        
        client = self._get_client()
        object_name = self._get_object_path(filename, organization_id, project_id, job_id)
        
        # Read file content
        file_content = file.read()
        file_size = len(file_content)
        
        # Upload
        client.put_object(
            self.bucket,
            object_name,
            io.BytesIO(file_content),
            length=file_size,
            content_type=content_type,
        )
        
        # Generate presigned URL (expires in 7 days by default)
        url = client.presigned_get_object(
            self.bucket,
            object_name,
            expires=timedelta(days=7),
        )
        
        return {
            "file_path": object_name,
            "public_url": url,
            "content_type": content_type,
            "size_bytes": file_size,
            "storage_type": "minio",
            "bucket": self.bucket,
            "uploaded_at": datetime.utcnow().isoformat(),
        }

    async def download(self, file_path: str) -> BinaryIO:
        """Download file from MinIO."""
        import io
        
        client = self._get_client()
        response = client.get_object(self.bucket, file_path)
        return io.BytesIO(response.read())

    async def delete(self, file_path: str) -> bool:
        """Delete file from MinIO."""
        try:
            client = self._get_client()
            client.remove_object(self.bucket, file_path)
            return True
        except Exception:
            return False

    async def get_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get presigned URL for MinIO object."""
        from datetime import timedelta
        
        client = self._get_client()
        return client.presigned_get_object(
            self.bucket,
            file_path,
            expires=timedelta(seconds=expires_in),
        )

    async def exists(self, file_path: str) -> bool:
        """Check if object exists in MinIO."""
        try:
            client = self._get_client()
            client.stat_object(self.bucket, file_path)
            return True
        except Exception:
            return False


# Import for MinIO provider
from datetime import timedelta
