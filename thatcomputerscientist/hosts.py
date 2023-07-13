from django_hosts import host, patterns
from django.conf import settings

host_patterns = patterns(
    '',
    host(r'', settings.ROOT_URLCONF, name='default'),
    host(r'www', settings.ROOT_URLCONF, name='www'),
    host(r'solitude', 'solitude.urls', name='solitude'),
    host(r'solitude.shi.foo', 'solitude.urls', name='solitude'),
)
