from django.utils.deprecation import MiddlewareMixin


class I18NMiddleware(MiddlewareMixin):
    def process_request(self, request):
        language = request.COOKIES.get("site_language")
        if language:
            request.LANGUAGE_CODE = language
        else:
            request.LANGUAGE_CODE = "en"
        request.LANGUAGE_CODE = language

    def process_response(self, request, response):
        if not request.COOKIES.get("site_language"):
            response.set_cookie("site_language", "en")
        return response
