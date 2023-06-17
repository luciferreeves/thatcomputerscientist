import os

from bs4 import BeautifulSoup
from django.conf import settings
from django.http import HttpResponse
from google.cloud import translate_v2 as translate

cred_path = os.path.join(settings.BASE_DIR, 'credentials-translate.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_path

class TranslationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.CACHE_TTL = 60 * 60

    def __call__(self, request):
        response = self.get_response(request)
        lang_cookie = request.COOKIES.get('lang', '')
        
        if lang_cookie != 'ja':
            return response

        content_type = response.get('Content-Type', '').lower()
        if 'text' not in content_type:
            return response

        HTML_content =response.content.decode('utf-8')

        # add no translate class to the 'highlight' class
        soup = BeautifulSoup(HTML_content, 'html.parser')
        for tag in soup.find_all(class_='highlight'):
            tag['class'].append('notranslate')
        HTML_content = str(soup)
        
        HTML_content = HTML_content.replace(
            "That Computer Scientist",
            "ザットコンピュータサイエンティスト"
        )

        translate_client = translate.Client()
        target_language = 'ja'
        translated_content = translate_client.translate(
            HTML_content,
            target_language=target_language,
        )['translatedText']

        return HttpResponse(translated_content)
