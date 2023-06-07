import os
from django.http import HttpResponse
import redis


r = redis.Redis(host='localhost', port=6379, db=0)

from django.conf import settings
from google.cloud import translate_v2 as translate

cred_path = os.path.join(settings.BASE_DIR, 'credentials-translate.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_path

class TranslationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.CACHE_TTL = 60 * 60

    def __call__(self, request):
        # translate only if lang cookie is set to ja
        response = self.get_response(request)
        lang_cookie = request.COOKIES.get('lang', '')
        
        if lang_cookie != 'ja':
            return response

        content_type = response.get('Content-Type', '').lower()
        if 'text' not in content_type:
            return response
        
        # Try to get cached response
        path = request.get_full_path()
        cache_key = cache_key = f'{lang_cookie}:{path}'
        print(f'Japanese translation for {path} requested')

        cache_response = r.get(cache_key)
        if cache_response:
            print('cached', cache_key)
            # r.delete(cache_key)
            response = HttpResponse(cache_response)
            return response

        print('Cache not found, translating... for key: ', cache_key)
        HTML_content =response.content.decode('utf-8')
        
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

        r.set(cache_key, translated_content)
        r.expire(cache_key, self.CACHE_TTL)

        response.content = translated_content.encode('utf-8')
        return response
