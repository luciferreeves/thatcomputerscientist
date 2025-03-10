import os
from django.urls import reverse
import requests
from django.shortcuts import redirect, render
from internal.crypto_utilities import encode_url
from thatcomputerscientist.utils import i18npatterns
from internal.cache_utils import cache_data

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
ZORO_URL = os.getenv("ZORO_URL")


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


@cache_data(timeout=60 * 60, prefix="anime_data")
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

    # filter out relations/recommendations which are not anime: TV, OVA, MOVIE, SPECIAL, ONA
    data["relations"] = [
        relation
        for relation in data.get("relations", [])
        if relation.get("type") in ["TV", "OVA", "MOVIE", "SPECIAL", "ONA"]
    ]

    data["recommendations"] = [
        recommendation
        for recommendation in data.get("recommendations", [])
        if recommendation.get("type") in ["TV", "OVA", "MOVIE", "SPECIAL", "ONA"]
    ]

    return data


def find_optimal_server(episode_id, dub):
    params = {"animeEpisodeId": episode_id}
    response = requests.get(f"{ZORO_URL}/api/v2/hianime/episode/servers", params=params)
    response = response.json()
    if "message" in response:
        return None

    response = response["data"]
    if dub and "dub" in response and len(response["dub"]) > 0:
        return response["dub"][0]["serverName"]
    elif len(response["sub"]) > 0 and "sub" in response:
        return response["sub"][0]["serverName"]
    elif len(response["raw"]) > 0:
        return response["raw"][0]["serverName"]
    else:
        return None


@cache_data(timeout=60 * 60 * 24 * 7, prefix="streaming_data")
def get_anime_streaming_data(anime_id, current_episode, dub=False):
    provider = ANIME_PROVIDER_MAP.get(anime_id, "zoro")
    current_episode_id = current_episode.get("id")
    if provider == "zoro":
        episode_id = (
            current_episode_id.replace("$episode$", "?ep=")
            .replace("$dub", "")
            .replace("$sub", "")
        )
        params = {"animeEpisodeId": episode_id, "category": "dub" if dub else "sub"}
        response = requests.get(
            f"{ZORO_URL}/api/v2/hianime/episode/sources", params=params
        )
        if response.status_code == 200:
            return response.json()
        else:
            server = find_optimal_server(episode_id, dub)
            params["server"] = server
            response = requests.get(
                f"{ZORO_URL}/api/v2/hianime/episode/sources", params=params
            )
            if response.status_code == 200:
                return response.json()
            else:
                ANIME_PROVIDER_MAP[anime_id] = "gogoanime"
                return get_anime_streaming_data(anime_id, current_episode, dub)
    else:
        response = requests.get(
            f"{CONSUMET_BASE_URL}/meta/anilist/watch/{current_episode_id}",
        )

        data = {
            "tracks": [],
            "intro": {"start": 0, "end": 0},
            "outro": {"start": 0, "end": 0},
            "sources": [],
            "anilistID": 0,
            "malID": 0,
        }

        if not "message" in response.json():
            default_source = next(
                (s for s in response.json()["sources"] if s["quality"] == "default"),
                None,
            )
            data["sources"].append({"url": default_source["url"], "type": "hls"})
        else:
            data["sources"].append(
                {
                    "url": "",
                    "type": "",
                }
            )

        return {"data": data}


@cache_data(timeout=60 * 60, prefix="anime_results")
def anime_results(**kwargs):
    supported_status = [
        "releasing",
        "not_yet_released",
        "cancelled",
        "finished",
        "hiatus",
    ]

    sort = kwargs.get("sort", "trending")
    order = kwargs.get("order", "desc")
    genre = kwargs.get("genre", "")
    query = kwargs.get("query", "")
    page = kwargs.get("page", 1)
    per_page = kwargs.get("per_page", 12)
    status = kwargs.get("status", "")

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


def home(request):
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update({"title": "Anime: Home"})

    context = {
        "genres": genres,
        "sortings": sortings,
        "trending_anime": anime_results(sort="trending", per_page=8).get("results", []),
        "popular_anime": anime_results(sort="popularity", per_page=8).get(
            "results", []
        ),
        "top_anime": anime_results(sort="score", per_page=8).get("results", []),
        "top_airing_anime": anime_results(
            sort="popularity", status="releasing", per_page=16
        ).get("results", []),
    }
    return render(request, f"shared/anime/home.html", context)


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
    return render(request, f"shared/anime/search.html", context)


def anime(request, anime_id, e=None):
    dub = request.COOKIES.get("anime_dub", False)
    anime_data = get_anime(anime_id, dub)
    episode_numbers = [
        int(episode.get("number")) for episode in anime_data.get("episodes", [])
    ]
    try:
        e = int(e)
    except (TypeError, ValueError):
        e = None

    if episode_numbers:
        if not e:
            return redirect(
                reverse(
                    "anime:anime",
                    kwargs={"anime_id": anime_id, "e": episode_numbers[0]},
                )
            )
        max_episode = max(episode_numbers)
        if e > max_episode:
            return redirect(
                reverse(
                    "anime:anime",
                    kwargs={"anime_id": anime_id, "e": max_episode},
                )
            )
        if e not in episode_numbers:
            return redirect(
                reverse("anime:anime", kwargs={"anime_id": anime_id, "e": 1})
            )
        anime_data["current_episode"] = (
            anime_data.get("episodes", [])[e - 1] if e else None
        )

    anime_data["totalEpisodes"] = (
        len(episode_numbers)
        if not anime_data["totalEpisodes"]
        else anime_data["totalEpisodes"]
    )
    if "current_episode" in anime_data:
        streaming_data = get_anime_streaming_data(
            anime_id, anime_data["current_episode"], dub
        )

        streaming_data["data"]["sources"] = streaming_data["data"]["sources"][0]
        streaming_data["data"]["sources"]["url"] = encode_url(
            streaming_data["data"]["sources"]["url"]
        )

        for track in streaming_data["data"]["tracks"]:
            track["file"] = encode_url(track["file"])
    else:
        streaming_data = {}

    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update(
        {"title": f"Anime: {anime_data.get('title', {}).get('romaji')}"}
    )

    context = {
        "anime": anime_data,
        "streaming_data": streaming_data,
    }

    return render(
        request,
        f"shared/anime/anime.html",
        context,
    )
