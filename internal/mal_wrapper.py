import requests


def get_mal_recent_activity(username):
    url = f"https://api.jikan.moe/v4/users/{username}/userupdates"
    response = requests.get(url)
    if response.status_code == 200:
        anime = []
        manga = []

        for entry in response.json()["data"]["anime"]:
            anime.append(
                {
                    "id": entry["entry"]["mal_id"],
                    "url": entry["entry"]["url"],
                    "image_url": entry["entry"]["images"]["jpg"]["image_url"],
                    "title": entry["entry"]["title"],
                    "score": entry["score"],
                    "status": entry["status"],
                    "episodes_seen": entry["episodes_seen"] or 0,
                    "episodes_total": entry["episodes_total"] or 0,
                    "date": entry["date"],
                }
            )

        for entry in response.json()["data"]["manga"]:
            manga.append(
                {
                    "id": entry["entry"]["mal_id"],
                    "url": entry["entry"]["url"],
                    "image_url": entry["entry"]["images"]["jpg"]["image_url"],
                    "title": entry["entry"]["title"],
                    "score": entry["score"],
                    "status": entry["status"],
                    "chapters_read": entry["chapters_read"],
                    "chapters_total": entry["chapters_total"],
                    "volumes_read": entry["volumes_read"],
                    "volumes_total": entry["volumes_total"],
                    "date": entry["date"],
                }
            )

        return {"anime": anime, "manga": manga}
    else:
        return None
