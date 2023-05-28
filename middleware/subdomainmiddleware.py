from django.conf import settings
from django.shortcuts import redirect


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
        # check if ip address
        if len(host) == 4 and all([x.isdigit() for x in host]):
            # redirect to thatcomputerscientist.com
            is_ssl = request.is_secure()
            protocol = 'https' if is_ssl else 'http'
            return redirect(f'{protocol}://thatcomputerscientist.com')
        return self.get_response(request)

# Use different urlpatterns for each subdomain

class SubdomainURLRouting:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        configured_subdomains = getattr(settings, 'CONFIGURED_SUBDOMAINS', {})
        if request.subdomain:
            if request.subdomain in configured_subdomains:
                request.urlconf = configured_subdomains[request.subdomain] + '.urls'
            else:
                if '*' in configured_subdomains:
                    request.urlconf = configured_subdomains['*'] + '.urls'
                else:
                    root_urlconf = getattr(settings, 'ROOT_URLCONF', None)
                    request.urlconf = root_urlconf
        return self.get_response(request)
