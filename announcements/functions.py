from announcements.models import Announcement


def get_announcements():
    return Announcement.objects.filter(is_public=True).order_by("-created_at")
