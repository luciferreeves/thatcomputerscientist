# views.py
import os
import random
from hashlib import md5
from apps.stream.songs import MUSIC_FILES
import requests
from django.http import HttpResponse, JsonResponse

CDN_URL = os.getenv("CDN_URL")


def get_stream_url(filename: str) -> str:
    return f"{CDN_URL}/music/{filename}"


def random_song(request) -> JsonResponse:
    """Get a random song from the API."""
    song = random.choice(MUSIC_FILES)
    return JsonResponse(song)


def stream_song(request, song_id: str) -> HttpResponse:
    """Stream a specific song by filename."""
    stream_url = get_stream_url(song_id)
    response = requests.get(stream_url, stream=True)

    return HttpResponse(
        response.raw.read(),
        content_type=response.headers.get("Content-Type", "audio/mpeg"),
    )


# Constants from environment variables
# API_CONFIG = {
#     "BASE_URL": os.getenv("MUSIC_API_BASE_URL", "http://music.shi.foo/rest"),
#     "USERNAME": os.getenv("MUSIC_API_USERNAME"),
#     "PASSWORD": os.getenv("MUSIC_API_PASSWORD"),
#     "VERSION": os.getenv("MUSIC_API_VERSION", "1.16.1"),
#     "CLIENT": os.getenv("MUSIC_API_CLIENT", "Shifoo"),
# }


# def get_auth_params() -> Dict[str, str]:
#     """Generate authentication parameters for API requests."""
#     salt = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=6))
#     token = md5((API_CONFIG["PASSWORD"] + salt).encode()).hexdigest()

#     return {
#         "u": API_CONFIG["USERNAME"],
#         "t": token,
#         "s": salt,
#         "v": API_CONFIG["VERSION"],
#         "c": API_CONFIG["CLIENT"],
#     }


# def make_api_request(
#     endpoint: str, params: Dict = None, stream: bool = False
# ) -> Union[requests.Response, Dict]:
#     """Make an API request with error handling."""
#     auth_params = get_auth_params()
#     if params:
#         auth_params.update(params)

#     url = f"{API_CONFIG['BASE_URL']}/{endpoint}"

#     try:
#         response = requests.get(url, params=auth_params, stream=stream)
#         response.raise_for_status()
#         return response if stream else response.json()
#     except requests.RequestException as e:
#         # Log error here if you have logging configured
#         return {"error": str(e)}


# def random_song(request) -> JsonResponse:
#     """Get a random song from the API."""
#     # Try to get cached response first
#     cache_key = "random_song_response"
#     cached_response = cache.get(cache_key)
#     if cached_response:
#         return JsonResponse(cached_response)

#     response = make_api_request("getRandomSongs", {"size": 1, "f": "json"})

#     if "error" in response:
#         return JsonResponse({"error": response["error"]}, status=500)

#     try:
#         subsonic_response = response.get("subsonic-response", {})
#         song = subsonic_response.get("randomSongs", {}).get("song", [{}])[0]

#         if not song:
#             return JsonResponse({"error": "No song found"}, status=404)

#         # Construct response data
#         response_data = {
#             "song": song,
#             "coverURL": f"{API_CONFIG['BASE_URL']}/getCoverArt",
#             "coverParams": {"id": song.get("coverArt"), **get_auth_params()},
#         }

#         # Cache the response for a short period
#         cache.set(cache_key, response_data, 30)  # Cache for 30 seconds

#         return JsonResponse(response_data)
#     except Exception as e:
#         # Log error here if you have logging configured
#         return JsonResponse({"error": str(e)}, status=500)


# def stream_song(request, song_id: str) -> HttpResponse:
#     """Stream a specific song by ID."""
#     response = make_api_request("stream", {"id": song_id}, stream=True)

#     if isinstance(response, dict) and "error" in response:
#         return JsonResponse({"error": response["error"]}, status=500)

#     return HttpResponse(
#         response.raw.read(),
#         content_type=response.headers.get("Content-Type", "audio/mpeg"),
#     )
