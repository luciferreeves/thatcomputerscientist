from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import activate


class I18NMiddleware(MiddlewareMixin):
    def process_request(self, request):
        language = request.COOKIES.get("site_language", "en")
        request.LANGUAGE_CODE = language
        activate(language)

    def process_response(self, request, response):
        if not request.COOKIES.get("site_language"):
            response.set_cookie("site_language", "en")
        return response
