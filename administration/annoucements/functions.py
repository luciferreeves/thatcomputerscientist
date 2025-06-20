from administration.annoucements.models import Announcement


def get_announcements(lang="en"):
    queryset = (
        Announcement.objects.filter(is_public=True)
        .prefetch_related("translations")
        .order_by("-created_at")
    )

    return Announcement.translate_queryset(queryset, lang)
