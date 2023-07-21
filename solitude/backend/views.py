import json

from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from .constants.welcome_playlist import WELCOME_TRACKS
from django.views.decorators.csrf import ensure_csrf_cookie

# Create your views here.

index_view = never_cache(TemplateView.as_view(template_name='@solitude_frontend/index.html'))

@ensure_csrf_cookie
def home(request):
    visited = request.COOKIES.get('visited', False)
    if not visited or visited == 'False':
        response = render(request, '@solitude/welcome.html', {
            'playlist_tracks': str(json.dumps(WELCOME_TRACKS))
        })
        response.set_cookie('visited', True)
        return response
    return index_view(request)
