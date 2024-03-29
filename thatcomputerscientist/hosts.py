from django_hosts import host, patterns
from django.conf import settings

host_patterns = patterns(
    '',
    host(r'', settings.ROOT_URLCONF, name='default'),
    host(r'www', settings.ROOT_URLCONF, name='www'),
    host(r'solitude', 'solitude.backend.urls', name='solitude'),
    host(r'api', 'solitude.api.urls', name='api'),
)
