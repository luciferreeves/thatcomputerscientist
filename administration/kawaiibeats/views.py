import os
import re
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from administration.kawaiibeats.functions import (
    create_or_update_song_metadata,
    get_all_songs,
)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


@login_required
@user_passes_test(lambda u: u.is_superuser)
def home(request):
    request.meta.title = "KawaiiBeats Manager"
    template = "administration/kawaiibeats.html"
    context = {
        "songs": get_all_songs(),
    }

    if request.method == "POST":
        auto_spotify_url = request.POST.get("auto_spotify_url")
        song_data = {
            "title": request.POST.get("title"),
            "artists": request.POST.get("artists"),
            "album": request.POST.get("album"),
            "spotify_id": request.POST.get("spotify_id"),
            "spotify_uri": request.POST.get("spotify_uri", ""),
            "album_art_url": request.POST.get("album_art_url"),
            "custom_album_art": request.POST.get("custom_album_art"),
            "duration_ms": request.POST.get("duration_ms"),
            "explicit": request.POST.get("explicit") == "on",
            "release_date": request.POST.get("release_date"),
            "streaming_url": request.POST.get("streaming_url"),
        }
        context["auto_spotify_url"] = auto_spotify_url or song_data.get(
            "spotify_uri", ""
        )
        context["song"] = song_data

        if auto_spotify_url and not is_provided_song_data_valid(song_data):
            metadata = get_spotify_metadata(auto_spotify_url)
            if not metadata:
                context["error"] = "Failed to retrieve metadata."
                return render(request, template, context)

            song = process_spotify_metadata(metadata)
            if not song:
                context["error"] = "Failed to process metadata."
                return render(request, template, context)

            context["song"] = song
            context["song"]["spotify_uri"] = auto_spotify_url
            return render(request, template, context)
        elif is_provided_song_data_valid(song_data):
            s = create_or_update_song_metadata(song_data)
            if s:
                del context["auto_spotify_url"]
                del context["song"]
                context["success"] = "Song metadata saved successfully."
                return render(request, template, context)
            else:
                context["error"] = "Failed to save song metadata."
                return render(request, template, context)
        else:
            context["error"] = "Invalid song data provided."
            context["song"] = song_data
            return render(request, template, context)
    else:
        return render(request, template, context)


def is_provided_song_data_valid(song_data):
    if not song_data or not isinstance(song_data, dict):
        return False
    required_fields = [
        "title",
        "artists",
        "album",
        "spotify_id",
        "album_art_url",
        "duration_ms",
        "release_date",
        "streaming_url",
    ]
    for field in required_fields:
        if field not in song_data or not song_data[field]:
            return False
    return True


def process_spotify_metadata(metadata):
    try:
        artists = ", ".join([artist["name"] for artist in metadata["artists"]])
        release_date = metadata.get("album", {}).get("release_date")
        album_art_url = ""
        images = metadata.get("album", {}).get("images", [])
        if images:
            images.sort(
                key=lambda img: img.get("height", 0) * img.get("width", 0), reverse=True
            )
            album_art_url = images[0].get("url", "")

        processed_data = {
            "title": metadata.get("name", ""),
            "artists": artists,
            "album": metadata.get("album", {}).get("name", ""),
            "spotify_id": metadata.get("id", ""),
            "album_art_url": album_art_url,
            "duration_ms": metadata.get("duration_ms", None),
            "explicit": bool(metadata.get("explicit", False)),  # Ensure it's a boolean
            "release_date": release_date,
        }

        return processed_data
    except Exception as e:
        return None


def get_spotify_metadata(spotify_url):
    access_token = get_spotify_access_token()
    if not access_token:
        return None

    track_id = None
    if "track/" in spotify_url:
        track_id = spotify_url.split("track/")[1].split("?")[0]
    elif "track:" in spotify_url:
        track_id = spotify_url.split("track:")[1].split("?")[0]
    else:
        match = re.search(r"spotify\.com/track/([a-zA-Z0-9]+)", spotify_url)
        if match:
            track_id = match.group(1)

    if not track_id:
        print(f"Could not extract track ID from URL: {spotify_url}")
        return None

    api_url = f"https://api.spotify.com/v1/tracks/{track_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_spotify_access_token():
    auth_url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(auth_url, headers=headers, data=data)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        return None
