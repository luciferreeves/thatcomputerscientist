from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MinioStorage(S3Boto3Storage):
    def __init__(self, **kwargs):
        scheme = "https" if settings.MINIO_USE_SSL else "http"
        kwargs.setdefault("access_key", settings.MINIO_ACCESS_KEY)
        kwargs.setdefault("secret_key", settings.MINIO_SECRET_KEY)
        kwargs.setdefault("bucket_name", settings.MINIO_BUCKET)
        kwargs.setdefault("endpoint_url", f"{scheme}://{settings.MINIO_UPLOAD_ENDPOINT}")
        domain = settings.MINIO_ACCESS_ENDPOINT.replace("https://", "").replace("http://", "")
        kwargs.setdefault("custom_domain", f"{domain}/{settings.MINIO_BUCKET}")
        kwargs.setdefault("file_overwrite", False)
        kwargs.setdefault("default_acl", None)
        kwargs.setdefault("querystring_auth", False)
        super().__init__(**kwargs)
