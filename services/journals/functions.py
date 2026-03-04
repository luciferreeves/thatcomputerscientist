from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Prefetch
from services.journals.models import Journal, JournalEntry
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
                return False, "Journal Name is not available."

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


def create_journal_entry(journal, title, content, slug=None):
    try:
        title = title.strip()
        if not title:
            return False, "Entry title is required."

        if slug:
            slug = slug.strip()
        else:
            slug = slugify(title)

        if journal.entries.filter(slug=slug).exists():
            return False, "Slug is not available."

        entry = journal.entries.create(
            title=title,
            content=content.strip(),
            slug=slug,
        )
        return True, entry

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


def get_single_user_journal(user, slug, lang="en"):
    try:
        journal = (
            Journal.objects.filter(owner=user, slug=slug)
            .select_related("owner")
            .prefetch_related("entries", "translations", "shared_with")
            .annotate(entries_count=Count("entries"))
            .first()
        )

        if not journal:
            return False, "Journal not found."

        return True, journal.translate(lang)
    except Exception as e:
        return False, str(e)


def get_latest_journal_entry(user, slug, lang="en", count=1):
    try:
        journal = (
            Journal.objects.filter(owner=user, slug=slug)
            .select_related("owner")
            .prefetch_related("translations", "shared_with")
            .annotate(entries_count=Count("entries"))
            .first()
        )

        if not journal:
            return False, "Journal not found."

        journal = journal.translate(lang)
        entries = list(
            JournalEntry.objects.filter(journal=journal)
            .prefetch_related("translations")
            .order_by("-created_at")[:count]
        )

        for entry in entries:
            entry.translate(lang)

        journal._prefetched_objects_cache["entries"] = entries

        return True, journal
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


def update_journal_settings(user, journal, post_data):
    try:
        from django.contrib.auth.models import User
        from services.journals.models import JournalTranslation

        if journal.owner != user:
            return False, "You don't have permission to edit this journal."
        name = post_data.get("name", "").strip()
        slug = post_data.get("slug", "").strip()
        description = post_data.get("description", "").strip()
        private = post_data.get("private") == "on"
        custom_css = post_data.get("custom_css", "").strip()

        if not name:
            return False, "Journal name is required."

        if not slug:
            slug = slugify(name)
        if slug != journal.slug:
            if slug.lower() in [s.lower() for s in RESERVED_JOURNAL_SLUGS]:
                if not user.is_superuser:
                    return False, "Slug is not available."

            if Journal.objects.filter(slug=slug).exclude(id=journal.id).exists():
                return False, "Slug is not available."
        journal.name = name
        journal.slug = slug
        journal.description = description
        journal.private = private
        journal.custom_css = custom_css
        journal.save()
        shared_usernames = post_data.getlist("add_shared_user")
        journal.shared_with.clear()

        invalid_users = []
        for username in shared_usernames:
            username = username.strip()
            if username:
                try:
                    shared_user = User.objects.get(username=username)
                    if shared_user != user:  # Don't add the owner
                        journal.shared_with.add(shared_user)
                except User.DoesNotExist:
                    invalid_users.append(username)

        if invalid_users:
            return False, f"These users were not found: {', '.join(invalid_users)}"
        existing_translation_ids = set()
        for translation in journal.translations.all():
            lang_key = f"translation_language_{translation.id}"
            name_key = f"translation_name_{translation.id}"
            desc_key = f"translation_description_{translation.id}"
            delete_key = f"delete_translation_{translation.id}"

            if delete_key in post_data:
                translation.delete()
                continue

            if lang_key in post_data and post_data[lang_key]:
                translation.language = post_data[lang_key]
                translation.name = post_data.get(name_key, "").strip()
                translation.description = post_data.get(desc_key, "").strip()
                translation.save()
                existing_translation_ids.add(translation.id)
        used_languages = set(journal.translations.values_list("language", flat=True))

        for key, value in post_data.items():
            if key.startswith("translation_language_new_") and value:
                if value in used_languages:
                    continue  # Skip duplicates

                translation_id = key.replace("translation_language_new_", "")
                name_key = f"translation_name_new_{translation_id}"
                desc_key = f"translation_description_new_{translation_id}"

                JournalTranslation.objects.create(
                    journal=journal,
                    language=value,
                    name=post_data.get(name_key, "").strip(),
                    description=post_data.get(desc_key, "").strip(),
                )
                used_languages.add(value)

        return True, "Journal settings updated successfully."

    except Exception as e:
        return False, f"Error updating journal settings: {str(e)}"


def update_journal_entry(user, journal, entry_slug, post_data):
    try:
        from services.journals.models import JournalEntryTranslation

        if journal.owner != user:
            return False, "You don't have permission to edit this entry."

        entry = journal.entries.filter(slug=entry_slug).first()
        if not entry:
            return False, "Entry not found."

        title = post_data.get("title", "").strip()
        content = post_data.get("content", "").strip()

        if not title:
            return False, "Entry title is required."

        if not content:
            return False, "Entry content is required."

        entry.title = title
        entry.content = content

        new_slug = post_data.get("slug", "").strip()
        if new_slug and new_slug != entry.slug:
            if journal.entries.filter(slug=new_slug).exclude(id=entry.id).exists():
                return False, "Slug is not available."
            entry.slug = new_slug

        entry.save()

        # Handle translation deletions and updates
        for translation in entry.translations.all():
            lang_key = f"translation_language_{translation.id}"
            title_key = f"translation_title_{translation.id}"
            content_key = f"translation_content_{translation.id}"
            delete_key = f"delete_translation_{translation.id}"

            if delete_key in post_data:
                translation.delete()
                continue

            if lang_key in post_data and post_data[lang_key]:
                translation.language = post_data[lang_key]
                translation.title = post_data.get(title_key, "").strip()
                translation.content = post_data.get(content_key, "").strip()
                translation.save()

        # Handle new translations
        used_languages = set(entry.translations.values_list("language", flat=True))

        for key, value in post_data.items():
            if key.startswith("translation_language_new_") and value:
                if value in used_languages:
                    continue

                translation_id = key.replace("translation_language_new_", "")
                title_key = f"translation_title_new_{translation_id}"
                content_key = f"translation_content_new_{translation_id}"

                JournalEntryTranslation.objects.create(
                    journal_entry=entry,
                    language=value,
                    title=post_data.get(title_key, "").strip(),
                    content=post_data.get(content_key, "").strip(),
                )
                used_languages.add(value)

        return True, "Entry updated successfully."

    except Exception as e:
        return False, f"Error updating entry: {str(e)}"


def get_journal(slug, user=None, page=1, per_page=5, lang="en"):
    try:
        journal = (
            Journal.objects.filter(slug=slug)
            .select_related("owner")
            .prefetch_related("translations", "shared_with", "owner__userprofile_set")
            .annotate(entries_count=Count("entries"))
            .first()
        )

        if not journal:
            return False, None, None

        if not journal.is_accessible_by(user):
            return False, None, None

        journal = journal.translate(lang)

        entries_qs = (
            JournalEntry.objects.filter(journal=journal)
            .prefetch_related("translations")
            .order_by("-created_at")
        )

        paginator = Paginator(entries_qs, per_page)

        try:
            entries_page = paginator.page(page)
        except PageNotAnInteger:
            entries_page = paginator.page(1)
        except EmptyPage:
            entries_page = paginator.page(paginator.num_pages)

        for entry in entries_page:
            entry.translate(lang)

        journal._prefetched_objects_cache["entries"] = list(entries_page)

        return True, journal, entries_page
    except Exception as e:
        return False, None, None


def delete_journal_entry(user, journal, entry_slug):
    try:
        if journal.owner != user:
            return False, "You don't have permission to delete this entry."

        entry = journal.entries.filter(slug=entry_slug).first()
        if not entry:
            return False, "Entry not found."

        entry_title = entry.title
        entry.delete()

        return True, f'Entry "{entry_title}" has been deleted.'

    except Exception as e:
        return False, f"Error deleting entry: {str(e)}"


def delete_journal(user, journal):
    try:
        if journal.owner != user:
            return False, "You don't have permission to delete this journal."

        journal_name = journal.name
        journal.delete()

        return True, f'Journal "{journal_name}" has been deleted.'

    except Exception as e:
        return False, f"Error deleting journal: {str(e)}"
