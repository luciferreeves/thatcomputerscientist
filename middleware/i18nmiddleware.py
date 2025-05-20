from django.utils.translation import activate
from django.utils.deprecation import MiddlewareMixin


class I18NMiddleware(MiddlewareMixin):
    def process_request(self, request):
        language = request.COOKIES.get("site_language")
        if language:
            activate(language)
        else:
            activate("en")
        request.LANGUAGE_CODE = language
        request.ALT_LANGUAGE = "ja" if language == "en" else "en"    
    

    def process_response(self, request, response):
        if not request.COOKIES.get("site_language"):
            response.set_cookie("site_language", "en")
        return response
