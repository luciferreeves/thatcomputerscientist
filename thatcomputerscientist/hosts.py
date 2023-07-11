from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'', 'thatcomputerscientist.urls', name='default'),
    host(r'solitude', 'solitude.urls', name='solitude')
)
