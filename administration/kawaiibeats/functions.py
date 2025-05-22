from administration.kawaiibeats.models import SongMetadata


def get_all_songs():
    try:
        songs = SongMetadata.objects.all()
        return songs
    except Exception as e:
        return None


def create_or_update_song_metadata(song_data):
    try:
        song, created = SongMetadata.objects.update_or_create(
            spotify_id=song_data["spotify_id"],
            defaults={
                "title": song_data["title"],
                "artists": song_data["artists"],
                "album": song_data["album"],
                "spotify_uri": song_data["spotify_uri"],
                "album_art_url": song_data["album_art_url"],
                "custom_album_art": song_data.get("custom_album_art"),
                "duration_ms": song_data.get("duration_ms"),
                "explicit": bool(song_data.get("explicit")),
                "release_date": song_data.get("release_date"),
                "streaming_url": song_data.get("streaming_url"),
            },
        )
        return song
    except Exception as e:
        return None
