from django.http import HttpResponse
import redis


r = redis.Redis(host='localhost', port=6379, db=0)

class ContentCachingMiddleware(object):
    # We will cache all text/html responses for 1 hour
    CACHE_TTL = 60 * 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang_cookie = request.COOKIES.get('lang', '')
        path = request.get_full_path()

        # Don't cache POST requests or path contains 'blog-admin'
        if request.method == 'POST' or lang_cookie == 'ja' or 'blog-admin' in path:
            return self.get_response(request)

        # Try to get cached response
        cache_key = f'path_cache_{lang_cookie}:{path}'

        cached_response = r.get(cache_key)
        if cached_response:
            return HttpResponse(cached_response)
        
        # Get response from view
        response = self.get_response(request)

        # Cache response if content-type is text/html
        if response.status_code == 200 and 'text/html' in response.get('Content-Type', ''):
            print(cache_key, 'cached')
            r.set(cache_key, response.content.decode('utf-8'))
            r.expire(cache_key, self.CACHE_TTL)

        return response