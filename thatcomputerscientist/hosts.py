from django_hosts import host, patterns

host_patterns = patterns(
    '',
    host(r'', 'thatcomputerscientist.urls', name='default'),
    host(r'solitude', 'solitude.urls', name='solitude')
)
