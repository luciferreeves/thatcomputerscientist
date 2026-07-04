from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MinioStorage(S3Boto3Storage):
    def __init__(self, **kwargs):
        scheme = "https" if settings.CDN_USE_SSL else "http"
        kwargs.setdefault("access_key", settings.CDN_ACCESS_KEY)
        kwargs.setdefault("secret_key", settings.CDN_SECRET_KEY)
        kwargs.setdefault("bucket_name", settings.CDN_BUCKET)
        kwargs.setdefault("endpoint_url", f"{scheme}://{settings.CDN_UPLOAD_ENDPOINT}")
        domain = settings.CDN_ACCESS_ENDPOINT.replace("https://", "").replace("http://", "")
        kwargs.setdefault("custom_domain", f"{domain}/{settings.CDN_BUCKET}")
        kwargs.setdefault("file_overwrite", False)
        kwargs.setdefault("default_acl", None)
        kwargs.setdefault("querystring_auth", False)
        super().__init__(**kwargs)
