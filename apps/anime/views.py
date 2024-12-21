import os
from django.urls import reverse
import requests
from django.shortcuts import redirect, render

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


def get_anime(anime_id, dub=False):
    if anime_id in ANIME_PROVIDER_MAP:
        provider = ANIME_PROVIDER_MAP[anime_id]
    else:
        provider = "zoro"

    dub = "true" if dub else "false"
    base_url = f"{os.getenv('CONSUMET_URL')}/meta/anilist/info/{anime_id}"
    params = {"provider": provider, "dub": dub}

    response = requests.get(base_url, params=params)
    data = response.json()
    if (
        (not data.get("episodes") or len(data.get("episodes")) == 0)
        and provider == "zoro"
        and data.get("status") != "Not yet aired"
    ):
        ANIME_PROVIDER_MAP[anime_id] = "gogoanime"
        return get_anime(anime_id)
    else:
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

    sort_value = sort_mappings[sort_by]
    order_suffix = "" if order == "asc" else "_DESC"

    return f"{sort_value}{order_suffix}"


def bracketed_string(string):
    return f'["{string}"]'


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

    if status and status not in supported_status:
        status = ""

    base_url = f"{os.getenv('CONSUMET_URL')}/meta/anilist/advanced-search"
    params = {"page": page, "perPage": per_page, "type": "ANIME"}

    if query:
        params["query"] = query

    if sort and order:
        sort_value = sort_mapper(sort, order)
        if sort_value:
            params["sort"] = bracketed_string(sort_value)

    if genre:
        params["genres"] = bracketed_string(genre)

    if status:
        params["status"] = status.upper()

    response = requests.get(base_url, params=params)
    return response.json()


def home(request):
    META = {
        "title": "Anime: Home",
    }
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update(META)

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
    # Get search parameters
    query = request.GET.get("q", "")
    genre = request.GET.get("genre", "")
    sort = request.GET.get("sort", "popularity")
    order = request.GET.get("order", "desc")
    page = int(request.GET.get("page", 1))

    META = {
        "title": f"Anime: Search",
    }
    if query:
        META["title"] = f"Anime: Search Results for {query}"
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update(META)

    # Get search results
    search_results = anime_results(
        query=query, genre=genre, sort=sort, order=order, page=page, per_page=32
    )

    context = {
        "genres": genres,
        "sortings": sortings,
        "search_results": search_results,
        "current_page": page,
        "total_pages": search_results.get("totalPages", 1),
        "total_results": search_results.get("totalResults", 0),
    }

    return render(request, f"{LANGUAGE_CODE}/anime/search.html", context)


def anime(request, anime_id, e=None):
    dub = request.COOKIES.get("anime_dub", False)
    anime_data = get_anime(anime_id, dub)

    if len(anime_data.get("episodes")) > 0:
        episode_numbers = [
            int(episode.get("number")) for episode in anime_data.get("episodes")
        ]

        if not e:
            e = episode_numbers[0]
            return redirect(
                reverse("anime:anime", kwargs={"anime_id": anime_id, "e": e})
            )

        e = int(e)
        if e not in episode_numbers:
            return redirect(
                reverse("anime:anime", kwargs={"anime_id": anime_id, "e": 1})
            )

    META = {
        "title": f"Anime: {anime_data.get('title').get('romaji')}",
    }
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update(META)

    context = {
        "anime": anime_data,
    }

    return render(request, f"{LANGUAGE_CODE}/anime/anime.html", context)
