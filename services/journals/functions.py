from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from services.journals.models import Journal
from services.journals.constants import RESERVED_JOURNAL_SLUGS, RESERVED_JOURNAL_NAMES


def create_journal(user, name, description="", private=False, slug=None):
    try:
        name = name.strip()
        if not name:
            return False, "Journal name is required."

        if slug:
            slug = slug.strip()
        else:
            slug = slugify(name)

        if slug.lower() in [s.lower() for s in RESERVED_JOURNAL_SLUGS]:
            if not user.is_superuser:
                return False, "Slug is not available."

        if name.lower() in [n.lower() for n in RESERVED_JOURNAL_NAMES]:
            if not user.is_superuser:
                return False, "Slug is not available."

        if Journal.objects.filter(owner=user, slug=slug).exists():
            return False, "Slug is not available."

        if Journal.objects.filter(slug=slug).exists():
            return False, "Slug is not available."

        journal = Journal.objects.create(
            name=name,
            slug=slug,
            description=description.strip(),
            private=private,
            owner=user,
        )
        return True, journal

    except Exception as e:
        return False, "Slug is not available."


def get_user_journals(user, page=1, per_page=10, lang="en"):
    try:
        journals = (
            Journal.objects.filter(owner=user)
            .select_related("owner")
            .prefetch_related("entries", "translations")
            .annotate(entries_count=Count("entries"))
            .order_by("created_at")
        )

        translated_journals = Journal.translate_queryset(journals, lang)

        paginator = Paginator(translated_journals, per_page)

        try:
            journals_page = paginator.page(page)
        except PageNotAnInteger:
            journals_page = paginator.page(1)
        except EmptyPage:
            journals_page = paginator.page(paginator.num_pages)

        return True, journals_page
    except Exception as e:
        return False, str(e)


def get_user_journal_stats(user):
    try:
        private_count = Journal.objects.filter(owner=user, private=True).count()
        total_entries = (
            Journal.objects.filter(owner=user).aggregate(total=Count("entries"))[
                "total"
            ]
            or 0
        )

        return True, {
            "private_journals_count": private_count,
            "total_entries_count": total_entries,
        }
    except Exception as e:
        return False, str(e)
