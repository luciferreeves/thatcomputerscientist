# Middleware to add global meta tags to the HTML head


class GlobalMetaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.meta = {
            # Default General Meta Tags
            "title": "Shifoo",
            "description": "Welcome to the home of Shifoo. This is my personal website where I share all of my thoughts, ideas, and experiences.",
            "image": "https://shi.foo/static/images/favicons/android-chrome-512x512.png",
            "url": "{}://{}{}".format(request.scheme, request.get_host(), request.path),
            # Robots Meta Tags
            "robots": "index, follow",
        }

        response = self.get_response(request)

        return response
