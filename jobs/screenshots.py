import os

from celery import shared_task

from internal.steam_wrapper import refresh_screenshot_cache


@shared_task
def refresh_steam_screenshots() -> None:
    refresh_screenshot_cache(os.getenv("STEAM_USERNAME", ""))
