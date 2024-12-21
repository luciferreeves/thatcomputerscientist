import os
from django.urls import reverse
import requests
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page
from functools import wraps
from django.core.cache import cache
from thatcomputerscientist.utils import i18npatterns

genres = [
    "Action",
    "Adventure",
    "Cars",
    "Comedy",
    "Drama",
    "Fantasy",
    "Horror",
    "Mahou Shoujo",
    "Mecha",
    "Music",
    "Mystery",
    "Psychological",
    "Romance",
    "Sci-Fi",
    "Slice of Life",
    "Sports",
    "Supernatural",
    "Thriller",
]

sortings = [
    {"name": "Popularity", "value": "popularity"},
    {"name": "Trending", "value": "trending"},
    {"name": "Start Date", "value": "start_date"},
    {"name": "End Date", "value": "end_date"},
    {"name": "Score", "value": "score"},
    {"name": "Favourites", "value": "favourites"},
    {"name": "Title", "value": "title"},
]

ANIME_PROVIDER_MAP = {}
CONSUMET_BASE_URL = os.getenv("CONSUMET_URL")


def get_anime(anime_id, dub=False):
    provider = ANIME_PROVIDER_MAP.get(anime_id, "zoro")
    params = {"dub": "true"} if dub else {}
    params.update({"provider": provider} if provider == "zoro" else {})

    response = requests.get(
        f"{CONSUMET_BASE_URL}/meta/anilist/info/{anime_id}", params=params
    )
    data = response.json()

    if (
        not data.get("episodes")
        and provider == "zoro"
        and data.get("status") != "Not yet aired"
    ):
        ANIME_PROVIDER_MAP[anime_id] = "gogoanime"
        return get_anime(anime_id, dub)

    ANIME_PROVIDER_MAP[anime_id] = provider
    return data


def sort_mapper(sort_by, order):
    sort_mappings = {
        "popularity": "POPULARITY",
        "trending": "TRENDING",
        "start_date": "START_DATE",
        "end_date": "END_DATE",
        "score": "SCORE",
        "favourites": "FAVOURITES",
        "title": "TITLE_ROMAJI",
    }

    if sort_by not in sort_mappings or order not in ["asc", "desc"]:
        return None

    return f"{sort_mappings[sort_by]}{'_DESC' if order == 'desc' else ''}"


def anime_results(
    sort="trending", order="desc", genre="", query="", page=1, per_page=12, status=""
):
    supported_status = [
        "releasing",
        "not_yet_released",
        "cancelled",
        "finished",
        "hiatus",
    ]
    params = {
        "page": page,
        "perPage": per_page,
        "type": "ANIME",
        **({"query": query} if query else {}),
        **({"sort": f'["{sort_mapper(sort, order)}"]'} if sort and order else {}),
        **({"genres": f'["{genre}"]'} if genre else {}),
        **({"status": status.upper()} if status in supported_status else {}),
    }

    response = requests.get(
        f"{CONSUMET_BASE_URL}/meta/anilist/advanced-search", params=params
    )
    return response.json()


def cache_anime_page(timeout=60 * 15):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, anime_id, e=None, *args, **kwargs):
            cache_key = f"anime_page:{anime_id}:ep{e}:dub{request.COOKIES.get('anime_dub', False)}"
            cached_response = cache.get(cache_key)

            if cached_response:
                return cached_response

            response = view_func(request, anime_id, e, *args, **kwargs)
            if response.status_code == 200:
                cache.set(cache_key, response, timeout)
            return response

        return _wrapped_view

    return decorator


@cache_page(60 * 15)
def home(request):
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update({"title": "Anime: Home"})

    context = {
        "genres": genres,
        "sortings": sortings,
        "trending_anime": anime_results(sort="trending", per_page=8),
        "popular_anime": anime_results(sort="popularity", per_page=8),
        "top_anime": anime_results(sort="score", per_page=8),
        "top_airing_anime": anime_results(
            sort="popularity", status="releasing", per_page=8
        ),
    }
    return render(request, f"{LANGUAGE_CODE}/anime/home.html", context)


def search(request):
    query = request.GET.get("q", "")
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update(
        {"title": f"Anime: Search Results for {query}" if query else "Anime: Search"}
    )

    search_results = anime_results(
        query=query,
        genre=request.GET.get("genre", ""),
        sort=request.GET.get("sort", "popularity"),
        order=request.GET.get("order", "desc"),
        page=int(request.GET.get("page", 1)),
        per_page=32,
    )

    context = {
        "genres": genres,
        "sortings": sortings,
        "search_results": search_results,
        "current_page": int(request.GET.get("page", 1)),
        "total_pages": search_results.get("totalPages", 1),
        "total_results": search_results.get("totalResults", 0),
    }
    return render(request, f"{LANGUAGE_CODE}/anime/search.html", context)


@cache_anime_page(timeout=60 * 15)
def anime(request, anime_id, e=None):
    anime_data = get_anime(anime_id, request.COOKIES.get("anime_dub", False))
    episode_numbers = [
        int(episode.get("number")) for episode in anime_data.get("episodes", [])
    ]

    if episode_numbers:
        if not e:
            return redirect(
                reverse(
                    "anime:anime",
                    kwargs={"anime_id": anime_id, "e": episode_numbers[0]},
                )
            )
        if int(e) not in episode_numbers:
            return redirect(
                reverse("anime:anime", kwargs={"anime_id": anime_id, "e": 1})
            )

    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update(
        {"title": f"Anime: {anime_data.get('title', {}).get('romaji')}"}
    )
    return render(request, f"{LANGUAGE_CODE}/anime/anime.html", {"anime": anime_data})
