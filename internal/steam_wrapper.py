from __future__ import annotations

import os

import requests

from internal.cache import cache


STEAM_API_KEY = os.getenv("STEAM_API_KEY", "")
SCREENSHOT_TTL = 6 * 60 * 60
VANITY_TTL = 30 * 24 * 60 * 60


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


def get_steam_screenshots(username: str) -> list[dict]:
    """Return every screenshot as a flat list in Steam's native order (newest
    first across all games — no per-game grouping)."""
    if not username:
        return []
    cache_key = f"steam_screenshots_flat:{username}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    steam_id = _resolve_vanity(username)
    if not steam_id or not STEAM_API_KEY:
        return []

    shots: list[dict] = []
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
            r = requests.get(
                "https://api.steampowered.com/IPublishedFileService/GetUserFiles/v1/",
                params=params,
                timeout=15,
            )
            data = r.json().get("response", {})
        except (requests.RequestException, ValueError):
            break
        files = data.get("publishedfiledetails", []) or []
        if not files:
            break
        for f in files:
            full = f.get("file_url") or f.get("preview_url") or ""
            if not full:
                continue
            shots.append({
                "id": str(f.get("publishedfileid", "")),
                "url": full,
            })
        if len(files) < per_page:
            break
        page += 1

    cache.set(cache_key, shots, ex=SCREENSHOT_TTL)
    return shots
