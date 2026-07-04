from administration.annoucements.models import Announcement


def get_announcements(lang="en"):
    queryset = (
        Announcement.objects.filter(is_public=True)
        .prefetch_related("translations")
        .order_by("-created_at")
    )

    return Announcement.translate_queryset(queryset, lang)


def update_announcement(announcement_id, content, is_new, is_public):
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        announcement.content = content
        announcement.is_new = is_new
        announcement.is_public = is_public
        announcement.save()
        return True
    except Announcement.DoesNotExist:
        return False


def create_announcement(content, is_new, is_public, author=None):
    announcement = Announcement(content=content, is_new=is_new, is_public=is_public, author=author)
    announcement.save()
    return True
