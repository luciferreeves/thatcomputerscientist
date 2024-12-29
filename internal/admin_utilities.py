from typing import List, Dict, Union
from io import BytesIO
from uuid import uuid4
from django.conf import settings
from minio import Minio
from minio.error import S3Error


class MinioFileManager:
    def __init__(self):
        """Initialize MinIO client with settings credentials."""
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=getattr(settings, "MINIO_SECURE", True),
        )

    def list_buckets(self) -> List[Dict[str, str]]:
        """List all buckets with creation dates."""
        try:
            buckets = self.client.list_buckets()
            return [
                {
                    "name": bucket.name,
                    "created": (
                        bucket.creation_date.isoformat()
                        if bucket.creation_date
                        else None
                    ),
                }
                for bucket in buckets
            ]
        except S3Error:
            return []

    def list_objects(
        self, bucket: str, prefix: str = ""
    ) -> List[Dict[str, Union[str, bool]]]:
        """List objects in a directory within bucket."""
        try:
            if not self.client.bucket_exists(bucket):
                return []

            # Ensure prefix ends with slash for directory listing
            prefix = prefix.rstrip("/") + "/" if prefix else ""
            objects = self.client.list_objects(bucket, prefix=prefix, recursive=False)

            result = []
            seen_prefixes = set()

            for obj in objects:
                # Skip the directory object itself
                if obj.object_name == prefix:
                    continue

                # Get relative path from prefix
                name = obj.object_name[len(prefix) :]
                if not name:
                    continue

                # Handle nested directories
                if "/" in name:
                    dir_name = name.split("/")[0] + "/"
                    if dir_name not in seen_prefixes:
                        seen_prefixes.add(dir_name)
                        result.append(
                            {
                                "name": dir_name.rstrip("/"),
                                "path": (prefix + dir_name).rstrip("/"),
                                "type": "folder",
                                "size": 0,
                                "last_modified": None,
                            }
                        )
                else:
                    result.append(
                        {
                            "name": name,
                            "path": obj.object_name,
                            "type": "file",
                            "size": obj.size,
                            "last_modified": (
                                obj.last_modified.isoformat()
                                if obj.last_modified
                                else None
                            ),
                        }
                    )

            return result
        except S3Error as e:
            print(f"MinIO Error: {e}")
            return []

    def create_folder(self, bucket: str, folder_path: str) -> bool:
        """Create a folder in the specified bucket."""
        try:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)

            folder_path = folder_path.rstrip("/") + "/"
            self.client.put_object(bucket, folder_path, BytesIO(b""), 0)
            return True
        except S3Error:
            return False

    def upload_file(self, bucket: str, file_path: str, object_name: str = None) -> bool:
        """Upload a file to MinIO."""
        try:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)

            object_name = object_name or str(uuid4())
            self.client.fput_object(bucket, object_name, file_path)
            return True
        except S3Error:
            return False

    def delete_object(
        self, bucket: str, object_path: str, recursive: bool = False
    ) -> bool:
        """Delete a file or folder from bucket."""
        try:
            if recursive and not object_path.endswith("/"):
                object_path += "/"
                objects = self.client.list_objects(
                    bucket, prefix=object_path, recursive=True
                )
                for obj in objects:
                    self.client.remove_object(bucket, obj.object_name)

            self.client.remove_object(bucket, object_path)
            return True
        except S3Error:
            return False

    def generate_presigned_url(
        self, bucket: str, object_name: str, expiry: int = 3600
    ) -> str:
        """Generate a presigned URL for file access."""
        try:
            return self.client.presigned_get_object(bucket, object_name, expiry)
        except S3Error:
            return ""
