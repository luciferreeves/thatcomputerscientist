# views.py
import os
import random
from hashlib import md5
from services.stream.songs import MUSIC_FILES
import requests
from django.http import HttpResponse, JsonResponse

CDN_URL = os.getenv("CDN_URL")
MUSIC_FILES_COUNT = len(MUSIC_FILES)


def get_stream_url(filename: str) -> str:
    return f"{CDN_URL}/music/{filename}"


def random_song(request) -> JsonResponse:
    next_song_id = request.GET.get("next")
    if next_song_id:
        song = MUSIC_FILES[int(next_song_id) % MUSIC_FILES_COUNT]
    else:
        song = random.choice(MUSIC_FILES)
    return JsonResponse(song)


def stream_song(request, song_id: int) -> HttpResponse:
    song = MUSIC_FILES[song_id - 1]
    stream_url = get_stream_url(song["songName"])
    response = requests.get(stream_url, stream=True)

    return HttpResponse(
        response.raw.read(),
        content_type=response.headers.get("Content-Type", "audio/mpeg"),
    )
