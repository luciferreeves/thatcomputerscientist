"""
    Shifoo's Solitude by Bobby
    --------------------------
    Shifoo's Solitude is a Web Dungeon located beyond the Dark Hollows of the Endless Information SuperHighway — a dark yet tranquil place where all questions end, curiosity begins, the mind awakens, and one's journey begins anew in the solitude of a serene mind!
    --------------------------

    File: welcome_playlist.py
    Description: Contains Metadata for tracks in the Welcome Page
    Date: Jul 11, 2023
    Last Modified: Jul 11, 2023
"""
BASE_MUSIC_DIR = "/static/@solitude/music/welcome"
BASE_COVER_ART_DIR = "/static/@solitude/music/welcome/cover_art"

WELCOME_TRACKS = {
    "SleepyRain": {
        "title": "Sleepy Rain",
        "artist": "lorenzobuczek",
        "location": f"{BASE_MUSIC_DIR}/sleepy_rain.mp3",
        "cover_art": f"{BASE_COVER_ART_DIR}/sleepy_rain.webp",
    },
    "RainAndNostalgia": {
        "title": "Rain and Nostalgia v60s",
        "artist": "lesfm",
        "location": f"{BASE_MUSIC_DIR}/rain_and_nostalgia_v60s.mp3",
        "cover_art": f"{BASE_COVER_ART_DIR}/default.jpeg",
    },
    "WishYouWereHere": {
        "title": "Wish You Were Here",
        "artist": "Lofi_hour",
        "location": f"{BASE_MUSIC_DIR}/wish_you_were_here.mp3",
        "cover_art": f"{BASE_COVER_ART_DIR}/wish_you_were_here.webp",
    },
    "Dripping": {
        "title": "Dripping",
        "artist": "Lofi_hour",
        "location": f"{BASE_MUSIC_DIR}/dripping.mp3",
        "cover_art": f"{BASE_COVER_ART_DIR}/dripping.webp",
    },
}
