# Middleware to add global meta tags to the HTML head

class GlobalMetaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.meta = {
            # Default General Meta Tags
            'title': 'That Computer Scientist',
            'description': 'Welcome to the home of That Computer Scientist. I am Kumar Priyansh. This is my personal website where I share all of my thoughts, ideas, and experiences.',
            'image': 'https://thatcomputerscientist.com/static/images/logo/logo.png',
            'url': '{}://{}{}'.format(request.scheme, request.get_host(), request.path),
            
            # Robots Meta Tags
            'robots': 'index, follow',
        }

        response = self.get_response(request)

        return response