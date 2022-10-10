from django.conf import settings

class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.subdomain = None
        host = request.get_host()
        host = host.replace('www.', '').split('.')
        if len(host) > 2 and '127.0.0.1' not in request.get_host():
            request.subdomain = '.'.join(host[:-2])
        if len(host) == 2 and 'localhost' in request.get_host():
            request.subdomain = host[0]
        return self.get_response(request)

# Use different urlpatterns for each subdomain

class SubdomainURLRouting:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        configured_subdomains = getattr(settings, 'CONFIGURED_SUBDOMAINS', {})
        if request.subdomain:
            if request.subdomain in configured_subdomains:
                if request.META.get('HTTP_REFERER') is None:
                    request.META['HTTP_REFERER'] = 'https://{}{}'.format(request.subdomain, settings.HOSTS[0])

                request.urlconf = configured_subdomains[request.subdomain] + '.urls'
            else:
                if '*' in configured_subdomains:
                    request.urlconf = configured_subdomains['*'] + '.urls'
                else:
                    root_urlconf = getattr(settings, 'ROOT_URLCONF', None)
                    request.urlconf = root_urlconf
        return self.get_response(request)
