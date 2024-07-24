# Ignis Middleware
# Scans all 'img' links
# if they start with '/ignis/<rest of the path>' > replaces them with env 'ignis.IGNIS_CACHE_ENDPOINT/<rest of the path>'
# if they start with '/static/<rest of the path>' > replaces them with env 'static.INGIS_STATIC_ENDPOINT/<rest of the path>'

import os
import re
from django.utils.deprecation import MiddlewareMixin
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

IGNIS_CACHE_ENDPOINT = os.getenv("IGNIS_CACHE_ENDPOINT")
IGNIS_CACHE_PROTOCOL = os.getenv("IGNIS_CACHE_PROTOCOL")

DYNAMIC_ENDPOINT = f"{IGNIS_CACHE_PROTOCOL}://ignis.{IGNIS_CACHE_ENDPOINT}"
STATIC_ENDPOINT = f"{IGNIS_CACHE_PROTOCOL}://static.{IGNIS_CACHE_ENDPOINT}"


class IgnisMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # id request is from localhost or 127.0.0.1, do not process
        if re.match(r"^localhost", request.get_host()) or re.match(r"^127.0.0.1", request.get_host()):
            return response

        # Do not process non-HTML responses
        if not response["Content-Type"].startswith("text/html"):
            return response

        response.content = self.process_response(response)
        return response

    def process_response(self, response):
        content = response.content.decode("utf-8")
        soup = BeautifulSoup(content, "html.parser")

        for image in soup.find_all("img"):
            src = image.get("src")
            if src.startswith("/ignis/"):
                image["src"] = f"{DYNAMIC_ENDPOINT}{src[6:]}"
            elif src.startswith("/static/"):
                image["src"] = f"{STATIC_ENDPOINT}{src[7:]}"

        return str(soup)
