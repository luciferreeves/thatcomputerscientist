import re
class OldBrowserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        old_browser = False
        onclick = True
        browser_patterns = [
            'msie [1-8]',
            'firefox/[1-3]\.',
            'chrome/[1-9]\.',
            'safari/[1-5]\.',
            'opera/[1-9]\.',
            'classilla'
        ]
        onclick_patterns = [
            'classilla'
        ]
        for pattern in browser_patterns:
            if re.search(pattern, user_agent):
                old_browser = True
                break
        
        for pattern in onclick_patterns:
            if re.search(pattern, user_agent):
                onclick = False
                break
        
        request.old_browser = old_browser
        request.onclick = onclick
        response = self.get_response(request)
        return response
        