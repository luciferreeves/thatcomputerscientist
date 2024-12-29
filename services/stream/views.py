# views.py
import os
import random
import re
from urllib.parse import quote, urljoin, urlparse

from django.conf import settings
from services.stream.songs import MUSIC_FILES
import requests
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
    StreamingHttpResponse,
)

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


def anime_stream(request):
    url = request.GET.get("url")
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    if not str(url).endswith(".vtt"):
        referrer = request.META.get("HTTP_REFERER")
        if not referrer:
            return HttpResponseForbidden()

        parsed_uri = urlparse(referrer)
        referrer_host = parsed_uri.netloc.split(":")[0]

        if referrer_host not in settings.ALLOWED_HOSTS:
            return HttpResponseForbidden()

    if not url:
        return HttpResponse("No URL provided", status=400)

    try:
        # Make the request to the target server
        response = requests.get(
            url,
            stream=True,
            headers={
                "User-Agent": request.headers.get("User-Agent", ""),
                "Referer": request.headers.get("Referer", ""),
                "Origin": request.headers.get("Origin", ""),
            },
        )

        content_type = response.headers.get("content-type", "")

        # Handle M3U8 playlists
        if "m3u8" in content_type or url.endswith(".m3u8"):
            content = response.text
            base_url = url.rsplit("/", 1)[0] + "/"

            # Modify the playlist URLs to go through our proxy
            modified_content = []
            for line in content.splitlines():
                if line.startswith("#"):
                    modified_content.append(line)
                elif line.strip():  # Handle content lines (URLs)
                    # Handle both absolute and relative URLs
                    if not line.startswith("http"):
                        line = urljoin(base_url, line)
                    proxy_url = f"/services/stream/anime?url={quote(line)}"
                    modified_content.append(proxy_url)
                else:
                    modified_content.append(line)

            return HttpResponse(
                "\n".join(modified_content),
                content_type="application/vnd.apple.mpegurl",
            )

        # Handle VTT files
        elif url.endswith(".vtt"):
            content = response.text
            base_url = url.rsplit("/", 1)[0] + "/"

            # Pattern to match both full URLs and relative paths with optional #xywh fragment
            sprite_pattern = r'((?:https?://[^\s<>"]+?|[\w-]+\.(?:jpg|jpeg|png|webp))(?:#xywh=[\d,]+)?)'

            def replace_url(match):
                sprite_url = match.group(1)
                # If it's not a full URL, join it with the base URL
                if not sprite_url.startswith("http"):
                    sprite_url = urljoin(base_url, sprite_url)
                return f"/watch/stream?url={quote(sprite_url)}"

            # Replace all image URLs with proxied versions
            modified_content = re.sub(sprite_pattern, replace_url, content)

            return HttpResponse(modified_content, content_type="text/vtt")

        # Handle images (thumbnails)
        elif any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            return StreamingHttpResponse(
                response.iter_content(chunk_size=8192),
                content_type=response.headers.get("content-type"),
                status=response.status_code,
            )

        # For video segments and other content, stream directly
        return StreamingHttpResponse(
            response.iter_content(chunk_size=8192),
            content_type=response.headers.get("content-type"),
            status=response.status_code,
        )

    except requests.RequestException as e:
        return HttpResponse(f"Error proxying request: {str(e)}", status=500)
