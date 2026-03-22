import django_stubs_ext

django_stubs_ext.monkeypatch()

from .celery import app as celery_app

__all__ = ("celery_app",)
