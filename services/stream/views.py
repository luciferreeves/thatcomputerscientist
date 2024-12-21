# views.py
import os
import random
from urllib.parse import urlparse

from django.conf import settings
from services.stream.songs import MUSIC_FILES
import requests
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse

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
    if not request.COOKIES.get("csrftoken"):
        return HttpResponseForbidden("Invalid request")

    referrer = request.META.get("HTTP_REFERER")
    if not referrer:
        return HttpResponseForbidden("Direct access not allowed")

    parsed_uri = urlparse(referrer)
    referrer_host = parsed_uri.netloc.split(":")[0]

    if referrer_host not in settings.ALLOWED_HOSTS:
        return HttpResponseForbidden("Access not allowed")

    try:
        song = MUSIC_FILES[song_id - 1]
        stream_url = get_stream_url(song["songName"])
        response = requests.get(stream_url, stream=True)

        if response.status_code != 200:
            return HttpResponse(status=response.status_code)

        return HttpResponse(
            response.raw.read(),
            content_type=response.headers.get("Content-Type", "audio/mpeg"),
            headers={
                "Content-Disposition": f"attachment; filename={song['songName']}.mp3",
                "X-Frame-Options": "DENY",
                "X-Content-Type-Options": "nosniff",
            },
        )
    except (IndexError, KeyError):
        return HttpResponse(status=404)
    except Exception:
        return HttpResponse(status=500)
