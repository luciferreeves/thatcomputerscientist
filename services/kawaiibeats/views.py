from administration.kawaiibeats.functions import get_random_song
from django.http import JsonResponse


def random_song(request):
    next_song = request.GET.get("next")
    if next_song:
        song = get_random_song(next_song)
    else:
        song = get_random_song()

    return JsonResponse(
        {
            "title": song.title,
            "artist": song.artists,
            "album": song.album,
            "spotify_id": song.spotify_id,
            "spotify_uri": song.spotify_uri,
            "album_art_url": song.album_art_url,
            "custom_album_art": song.custom_album_art,
            "duration_ms": song.duration_ms,
            "explicit": song.explicit,
            "release_date": song.release_date,
            "streaming_url": song.streaming_url,
        }
    )
