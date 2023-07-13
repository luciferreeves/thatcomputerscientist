import json

from django.shortcuts import render

from .constants.welcome_playlist import WELCOME_TRACKS

# Create your views here.
TEMPLATE_BASE_PATH = '@solitude'

def home(request):
    visited = request.COOKIES.get('visited', False)
    if not visited or visited == 'False':
        response = render(request, f'{TEMPLATE_BASE_PATH}/welcome.html', {
            'playlist_tracks': str(json.dumps(WELCOME_TRACKS))
        })
        response.set_cookie('visited', True)
        return response
    return render(request, f'{TEMPLATE_BASE_PATH}/home.html')
