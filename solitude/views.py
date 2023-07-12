from django.shortcuts import render
from .constants.welcome_playlist import WELCOME_TRACKS

import json

# Create your views here.
TEMPLATE_BASE_PATH = '@solitude'

def welcome(request):
    return render(request, f'{TEMPLATE_BASE_PATH}/welcome.html', {
        'playlist_tracks': str(json.dumps(WELCOME_TRACKS))
    })
