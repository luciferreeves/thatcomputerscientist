from __future__ import annotations

import os

import requests

from internal.cache import cache


STEAM_API_KEY = os.getenv("STEAM_API_KEY", "")
SCREENSHOT_TTL = 12 * 60 * 60
SCREENSHOT_REFRESH_EXTENSION = 6 * 60 * 60
VANITY_TTL = 30 * 24 * 60 * 60


def _screenshot_cache_key(username: str) -> str:
    return f"steam_screenshots_flat:{username}"


def _resolve_vanity(username: str) -> str | None:
    if not username:
        return None
    if username.isdigit():
        return username
    cache_key = f"steam_vanity:{username}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    if not STEAM_API_KEY:
        return None
    url = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
    try:
        r = requests.get(url, params={"key": STEAM_API_KEY, "vanityurl": username}, timeout=10)
        payload = r.json().get("response", {})
    except (requests.RequestException, ValueError):
        return None
    if payload.get("success") != 1:
        return None
    sid = str(payload.get("steamid", ""))
    if sid:
        cache.set(cache_key, sid, ex=VANITY_TTL)
    return sid or None


def _fetch_screenshots(username: str) -> list[dict[str, str]] | None:
    steam_id = _resolve_vanity(username)
    if not steam_id or not STEAM_API_KEY:
        return None

    shots: list[dict[str, str]] = []
    page = 1
    per_page = 100
    while page <= 4:
        params = {
            "key": STEAM_API_KEY,
            "steamid": steam_id,
            "page": page,
            "numperpage": per_page,
            "filetype": 4,
            "return_metadata": 1,
        }
        try:
            response = requests.get(
                "https://api.steampowered.com/IPublishedFileService/GetUserFiles/v1/",
                params=params,
                timeout=15,
            )
            files = response.json().get("response", {}).get("publishedfiledetails", []) or []
        except (requests.RequestException, ValueError):
            return None
        if not files:
            break
        for entry in files:
            url = entry.get("file_url") or entry.get("preview_url") or ""
            if url:
                shots.append({"id": str(entry.get("publishedfileid", "")), "url": url})
        if len(files) < per_page:
            break
        page += 1

    return shots


def get_steam_screenshots(username: str) -> list[dict[str, str]]:
    if not username:
        return []
    cached = cache.get(_screenshot_cache_key(username))
    if cached is not None:
        return cached
    shots = _fetch_screenshots(username)
    if shots is None:
        return []
    cache.set(_screenshot_cache_key(username), shots, ex=SCREENSHOT_TTL)
    return shots


def refresh_screenshot_cache(username: str) -> None:
    if not username:
        return
    key = _screenshot_cache_key(username)
    remaining = cache.ttl(key)
    if remaining > 0:
        cache.expire(key, remaining + SCREENSHOT_REFRESH_EXTENSION)
    shots = _fetch_screenshots(username)
    if shots is not None:
        cache.set(key, shots, ex=SCREENSHOT_TTL)
