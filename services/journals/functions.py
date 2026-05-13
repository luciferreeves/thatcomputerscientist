from __future__ import annotations

from datetime import date as date_type
from typing import Any

from django.contrib.auth.models import AbstractUser, User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Prefetch
from django.http import QueryDict
from django.utils import timezone
from django.utils.text import slugify

from services.journals.constants import (
    FORM_CHOICES,
    GENRE_CHOICES,
    MOOD_CHOICES,
    RESERVED_JOURNAL_NAMES,
    RESERVED_JOURNAL_SLUGS,
    TONE_CHOICES,
)
from services.journals.models import (
    Character,
    CharacterAppearance,
    CharacterRelationship,
    EntryTag,
    Journal,
    JournalEntry,
    JournalEntryTranslation,
    JournalTranslation,
    Volume,
)


def create_journal(
    user: AbstractUser,
    name: str,
    description: str = "",
    private: bool = False,
    slug: str | None = None,
    mode: str = "default",
    status: str = "",
    genre: str = "",
    cover_image: Any = None,
) -> tuple[bool, Journal | str]:
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
            mode=mode,
            status=status,
            genre=genre,
        )
        if cover_image:
            journal.cover_image = cover_image
            journal.save()

        return True, journal

    except Exception:
        return False, "Slug is not available."


def create_journal_entry(
    journal: Journal,
    title: str,
    content: str,
    slug: str | None = None,
    is_draft: bool = True,
    mood: str = "",
    tone: str = "",
    genre: str = "",
    form: str = "",
    summary: str = "",
    entry_date: date_type | None = None,
    volume_id: int | None = None,
    thumbnail: Any = None,
    character_ids: list[int] | None = None,
    new_character_names: list[str] | None = None,
    new_character_roles: list[str] | None = None,
    new_character_bios: list[str] | None = None,
    new_tag_names: list[str] | None = None,
) -> tuple[bool, JournalEntry | str]:
    try:
        title = title.strip()
        if not title and journal.mode != "diary":
            return False, "Entry title is required."

        if journal.mode == "diary":
            if not entry_date:
                entry_date = timezone.now().date()
            if not title:
                title = entry_date.strftime("%B %d, %Y")
            is_draft = False
            if journal.entries.filter(entry_date=entry_date).exists():
                return False, "A diary entry already exists for this date."

        if slug:
            slug = slug.strip()
        else:
            slug = slugify(title)

        if journal.entries.filter(slug=slug).exists():
            base_slug = slug
            counter = 1
            while journal.entries.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

        volume = None
        if volume_id:
            volume = journal.volumes.filter(pk=volume_id).first()

        last_entry = journal.entries.order_by("-order").first()
        order = (last_entry.order + 1) if last_entry else 1

        entry = journal.entries.create(
            title=title,
            content=content.strip(),
            slug=slug,
            order=order,
            is_draft=is_draft,
            mood=mood,
            tone=tone,
            genre=genre,
            form=form,
            summary=summary,
            entry_date=entry_date,
            volume=volume,
        )
        if thumbnail:
            entry.thumbnail = thumbnail
            entry.save()

        if character_ids:
            for char in journal.characters.filter(pk__in=character_ids):
                CharacterAppearance.objects.get_or_create(character=char, entry=entry)

        if new_character_names:
            roles = new_character_roles or []
            bios = new_character_bios or []
            for i, name in enumerate(new_character_names):
                name = name.strip()
                if not name:
                    continue
                role = roles[i].strip() if i < len(roles) else "Supporting"
                bio = bios[i].strip() if i < len(bios) else ""
                char, _ = Character.objects.get_or_create(
                    journal=journal, name=name, defaults={"role": role or "Supporting", "bio": bio}
                )
                CharacterAppearance.objects.get_or_create(character=char, entry=entry)

        if new_tag_names:
            for tag_name in new_tag_names:
                tag_name = tag_name.strip()
                if not tag_name:
                    continue
                tag_slug = slugify(tag_name)
                tag, _ = EntryTag.objects.get_or_create(
                    journal=journal, slug=tag_slug, defaults={"name": tag_name}
                )
                entry.tags.add(tag)

        return True, entry

    except Exception as e:
        return False, str(e)


def get_user_journals(
    user: AbstractUser, page: int = 1, per_page: int = 10, lang: str = "en"
) -> tuple[bool, Any]:
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


def get_single_user_journal(
    user: AbstractUser, slug: str, lang: str = "en"
) -> tuple[bool, Any]:
    try:
        journal = (
            Journal.objects.filter(owner=user, slug=slug)
            .select_related("owner")
            .prefetch_related(
                "entries", "translations", "shared_with",
                "volumes", "characters",
            )
            .annotate(entries_count=Count("entries"))
            .first()
        )

        if not journal:
            return False, "Journal not found."

        return True, journal.translate(lang)
    except Exception as e:
        return False, str(e)


def get_latest_journal_entry(
    user: AbstractUser, slug: str, lang: str = "en", count: int = 1
) -> tuple[bool, Any]:
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


def get_user_journal_stats(user: AbstractUser) -> tuple[bool, dict[str, int] | str]:
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


def update_journal_settings(
    user: AbstractUser, journal: Journal, post_data: QueryDict, files: Any = None
) -> tuple[bool, str]:
    try:
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

        status = post_data.get("status", "").strip()
        genre = post_data.get("genre", "").strip()
        journal.status = status
        journal.genre = genre

        if files and files.get("cover_image"):
            journal.cover_image = files["cover_image"]

        journal.save()
        shared_usernames = post_data.getlist("add_shared_user")
        journal.shared_with.clear()

        invalid_users: list[str] = []
        for username in shared_usernames:
            username = username.strip()
            if username:
                try:
                    shared_user = User.objects.get(username=username)
                    if shared_user != user:
                        journal.shared_with.add(shared_user)
                except User.DoesNotExist:
                    invalid_users.append(username)

        if invalid_users:
            return False, f"These users were not found: {', '.join(invalid_users)}"
        existing_translation_ids: set[int] = set()
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
        used_languages: set[str] = set(
            journal.translations.values_list("language", flat=True)
        )

        for key, value in post_data.items():
            if key.startswith("translation_language_new_") and value:
                if value in used_languages:
                    continue

                translation_id = key.replace("translation_language_new_", "")
                name_key = f"translation_name_new_{translation_id}"
                desc_key = f"translation_description_new_{translation_id}"

                JournalTranslation.objects.create(
                    journal=journal,
                    language=value,
                    name=post_data.get(name_key, "").strip(),
                    description=post_data.get(desc_key, "").strip(),
                )
                used_languages.add(str(value))

        return True, "Journal settings updated successfully."

    except Exception as e:
        return False, f"Error updating journal settings: {str(e)}"


def update_journal_entry(
    user: AbstractUser, journal: Journal, entry_slug: str, post_data: QueryDict, files: Any = None
) -> tuple[bool, str]:
    try:
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

        if "order" in post_data:
            try:
                entry.order = int(str(post_data["order"]))
            except (ValueError, TypeError):
                pass

        entry.is_draft = post_data.get("is_draft") == "on"
        entry.mood = post_data.get("mood", "").strip()
        entry.tone = post_data.get("tone", "").strip()
        entry.genre = post_data.get("genre", "").strip()
        entry.form = post_data.get("form", "").strip()
        entry.summary = post_data.get("summary", "").strip()

        entry_date_str = post_data.get("entry_date", "").strip()
        if entry_date_str:
            try:
                entry.entry_date = date_type.fromisoformat(entry_date_str)
            except ValueError:
                pass

        volume_id = post_data.get("volume", "").strip()
        if volume_id:
            entry.volume = journal.volumes.filter(pk=volume_id).first()
        else:
            entry.volume = None

        thumbnail = files.get("thumbnail") if files else None
        if thumbnail:
            entry.thumbnail = thumbnail
        if post_data.get("remove_thumbnail"):
            entry.thumbnail = ""

        if journal.mode == "diary":
            entry.is_draft = False

        entry.save()

        tag_ids = post_data.getlist("tags")
        new_tag_names = post_data.getlist("new_tag_names")
        new_tags = []
        for tag_name in new_tag_names:
            tag_name = tag_name.strip()
            if not tag_name:
                continue
            tag_slug = slugify(tag_name)
            tag, _ = EntryTag.objects.get_or_create(
                journal=journal, slug=tag_slug, defaults={"name": tag_name}
            )
            new_tags.append(tag)

        if tag_ids or new_tags:
            existing = list(journal.entry_tags.filter(pk__in=tag_ids))
            entry.tags.set(existing + new_tags)
        else:
            entry.tags.clear()

        new_character_names = post_data.getlist("new_character_names")
        new_character_roles = post_data.getlist("new_character_roles")
        new_character_bios = post_data.getlist("new_character_bios")
        new_chars = []
        for i, name in enumerate(new_character_names):
            name = name.strip()
            if not name:
                continue
            role = new_character_roles[i].strip() if i < len(new_character_roles) else "Supporting"
            bio = new_character_bios[i].strip() if i < len(new_character_bios) else ""
            char, _ = Character.objects.get_or_create(
                journal=journal, name=name, defaults={"role": role or "Supporting", "bio": bio}
            )
            new_chars.append(char)

        character_ids = post_data.getlist("character_ids")
        if character_ids or new_chars:
            existing = journal.characters.filter(pk__in=character_ids)
            all_chars = list(existing) + new_chars
            CharacterAppearance.objects.filter(entry=entry).exclude(character__in=all_chars).delete()
            for char in all_chars:
                CharacterAppearance.objects.get_or_create(character=char, entry=entry)
        elif journal.mode in ("book", "light_novel", "short_stories"):
            CharacterAppearance.objects.filter(entry=entry).delete()

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

        used_languages: set[str] = set(
            entry.translations.values_list("language", flat=True)
        )

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
                used_languages.add(str(value))

        return True, "Entry updated successfully."

    except Exception as e:
        return False, f"Error updating entry: {str(e)}"


def get_journal(
    slug: str,
    user: AbstractUser | None = None,
    page: int = 1,
    per_page: int = 5,
    lang: str = "en",
) -> tuple[bool, Any, Any]:
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

        if journal.private and (user is None or not journal.is_accessible_by(user)):
            return False, None, None

        journal = journal.translate(lang)

        entries_qs = JournalEntry.objects.filter(journal=journal).prefetch_related(
            "translations", "tags", "volume"
        )

        is_owner = user and user.is_authenticated and journal.owner == user
        if not is_owner:
            entries_qs = entries_qs.filter(is_draft=False)

        if journal.mode in ("book", "light_novel"):
            entries_qs = entries_qs.order_by("volume__order", "order")
        elif journal.mode == "diary":
            entries_qs = entries_qs.order_by("-entry_date")
        elif journal.mode == "poetry":
            entries_qs = entries_qs.order_by("order")
        else:
            entries_qs = entries_qs.order_by("-created_at")

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
    except Exception:
        return False, None, None


def delete_journal_entry(
    user: AbstractUser, journal: Journal, entry_slug: str
) -> tuple[bool, str]:
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


def delete_journal(user: AbstractUser, journal: Journal) -> tuple[bool, str]:
    try:
        if journal.owner != user:
            return False, "You don't have permission to delete this journal."

        journal_name = journal.name
        journal.delete()

        return True, f'Journal "{journal_name}" has been deleted.'

    except Exception as e:
        return False, f"Error deleting journal: {str(e)}"


def create_volume(
    user: AbstractUser,
    journal: Journal,
    title: str,
    description: str = "",
    cover_image: Any = None,
) -> tuple[bool, Any]:
    try:
        if journal.owner != user:
            return False, "You don't have permission to add volumes."
        title = title.strip()
        if not title:
            return False, "Volume title is required."
        last = journal.volumes.order_by("-order").first()
        order = (last.order + 1) if last else 1
        volume = journal.volumes.create(
            title=title, description=description.strip(), order=order,
        )
        if cover_image:
            volume.cover_image = cover_image
            volume.save()
        return True, volume
    except Exception as e:
        return False, str(e)


def update_volume(
    user: AbstractUser, journal: Journal, volume_id: int, post_data: QueryDict, files: Any = None
) -> tuple[bool, Any]:
    try:
        if journal.owner != user:
            return False, "You don't have permission to edit volumes."
        volume = journal.volumes.filter(pk=volume_id).first()
        if not volume:
            return False, "Volume not found."
        title = post_data.get("title", "").strip()
        if not title:
            return False, "Volume title is required."
        volume.title = title
        volume.description = post_data.get("description", "").strip()
        if files and files.get("cover_image"):
            volume.cover_image = files["cover_image"]
        volume.save()
        return True, volume
    except Exception as e:
        return False, str(e)


def delete_volume(
    user: AbstractUser, journal: Journal, volume_id: int
) -> tuple[bool, str]:
    try:
        if journal.owner != user:
            return False, "You don't have permission to delete volumes."
        volume = journal.volumes.filter(pk=volume_id).first()
        if not volume:
            return False, "Volume not found."
        volume.delete()
        return True, "Volume deleted."
    except Exception as e:
        return False, str(e)


def get_journal_volumes(journal: Journal) -> Any:
    return journal.volumes.annotate(entries_count=Count("entries")).order_by("order")


def reorder_volumes(
    user: AbstractUser, journal: Journal, volume_ids: list[int]
) -> tuple[bool, str]:
    try:
        if journal.owner != user:
            return False, "You don't have permission to reorder volumes."
        for order, volume_id in enumerate(volume_ids, start=1):
            journal.volumes.filter(pk=volume_id).update(order=order)
        return True, "Volumes reordered."
    except Exception as e:
        return False, str(e)


def reorder_characters(
    user: AbstractUser, journal: Journal, character_ids: list[int]
) -> tuple[bool, str]:
    try:
        if journal.owner != user:
            return False, "You don't have permission to reorder characters."
        for order, character_id in enumerate(character_ids, start=1):
            journal.characters.filter(pk=character_id).update(order=order)
        return True, "Characters reordered."
    except Exception as e:
        return False, str(e)


def reorder_entries(
    user: AbstractUser, journal: Journal, entry_ids: list[int]
) -> tuple[bool, str]:
    try:
        if journal.owner != user:
            return False, "You don't have permission to reorder entries."
        for order, entry_id in enumerate(entry_ids, start=1):
            journal.entries.filter(pk=entry_id).update(order=order)
        return True, "Entries reordered."
    except Exception as e:
        return False, str(e)


def create_character(
    user: AbstractUser,
    journal: Journal,
    name: str,
    bio: str = "",
    role: str = "Supporting",
    image: Any = None,
) -> tuple[bool, Any]:
    try:
        if journal.owner != user:
            return False, "You don't have permission to add characters."
        name = name.strip()
        if not name:
            return False, "Character name is required."
        last = journal.characters.order_by("-order").first()
        order = (last.order + 1) if last else 0
        character = journal.characters.create(
            name=name, bio=bio.strip(), role=role.strip(), order=order,
        )
        if image:
            character.image = image
            character.save()
        return True, character
    except Exception as e:
        return False, str(e)


def update_character(
    user: AbstractUser, journal: Journal, character_id: int, post_data: QueryDict, files: Any = None
) -> tuple[bool, Any]:
    try:
        if journal.owner != user:
            return False, "You don't have permission to edit characters."
        character = journal.characters.filter(pk=character_id).first()
        if not character:
            return False, "Character not found."
        name = post_data.get("name", "").strip()
        if not name:
            return False, "Character name is required."
        character.name = name
        character.bio = post_data.get("bio", "").strip()
        character.role = post_data.get("role", "").strip() or "Supporting"
        if "order" in post_data:
            try:
                character.order = int(str(post_data["order"]))
            except (ValueError, TypeError):
                pass
        image = files.get("image") if files else None
        if image:
            character.image = image
        if post_data.get("remove_image"):
            character.image = ""
        character.save()
        return True, character
    except Exception as e:
        return False, str(e)


def delete_character(
    user: AbstractUser, journal: Journal, character_id: int
) -> tuple[bool, str]:
    try:
        if journal.owner != user:
            return False, "You don't have permission to delete characters."
        character = journal.characters.filter(pk=character_id).first()
        if not character:
            return False, "Character not found."
        character.delete()
        return True, "Character deleted."
    except Exception as e:
        return False, str(e)


def get_journal_characters(journal: Journal) -> Any:
    return journal.characters.all().order_by("order")


def set_character_appearances(
    user: AbstractUser, journal: Journal, entry: JournalEntry, character_ids: list[int]
) -> tuple[bool, str]:
    try:
        if journal.owner != user:
            return False, "Permission denied."
        entry.character_appearances.all().delete()
        for cid in character_ids:
            character = journal.characters.filter(pk=cid).first()
            if character:
                CharacterAppearance.objects.create(character=character, entry=entry)
        return True, "Character appearances updated."
    except Exception as e:
        return False, str(e)


def set_character_relationship(
    user: AbstractUser, journal: Journal, from_id: int, to_id: int, label: str
) -> tuple[bool, Any]:
    try:
        if journal.owner != user:
            return False, "Permission denied."
        from_char = journal.characters.filter(pk=from_id).first()
        to_char = journal.characters.filter(pk=to_id).first()
        if not from_char or not to_char:
            return False, "Character not found."
        if from_char == to_char:
            return False, "Cannot create relationship with self."
        rel, _ = CharacterRelationship.objects.update_or_create(
            from_character=from_char, to_character=to_char,
            defaults={"label": label.strip()},
        )
        return True, rel
    except Exception as e:
        return False, str(e)


def delete_character_relationship(
    user: AbstractUser, journal: Journal, relationship_id: int
) -> tuple[bool, str]:
    try:
        if journal.owner != user:
            return False, "Permission denied."
        rel = CharacterRelationship.objects.filter(
            pk=relationship_id,
            from_character__journal=journal,
        ).first()
        if not rel:
            return False, "Relationship not found."
        rel.delete()
        return True, "Relationship deleted."
    except Exception as e:
        return False, str(e)


def create_entry_tag(
    user: AbstractUser, journal: Journal, name: str
) -> tuple[bool, Any]:
    try:
        if journal.owner != user:
            return False, "Permission denied."
        name = name.strip()
        if not name:
            return False, "Tag name is required."
        slug = slugify(name)
        if journal.entry_tags.filter(slug=slug).exists():
            return False, "Tag already exists."
        tag = EntryTag.objects.create(journal=journal, name=name, slug=slug)
        return True, tag
    except Exception as e:
        return False, str(e)


def delete_entry_tag(
    user: AbstractUser, journal: Journal, tag_id: int
) -> tuple[bool, str]:
    try:
        if journal.owner != user:
            return False, "Permission denied."
        tag = journal.entry_tags.filter(pk=tag_id).first()
        if not tag:
            return False, "Tag not found."
        tag.delete()
        return True, "Tag deleted."
    except Exception as e:
        return False, str(e)


def get_journal_tags(journal: Journal) -> Any:
    return journal.entry_tags.all().order_by("name")



def get_public_character(
    journal: Journal, character_id: int,
) -> tuple[bool, Character | None, list[CharacterRelationship], Any]:
    character = Character.objects.filter(journal=journal, id=character_id).first()
    if not character:
        return False, None, [], []
    relationships = list(
        CharacterRelationship.objects.filter(
            from_character=character
        ).select_related("to_character")
    ) + list(
        CharacterRelationship.objects.filter(
            to_character=character
        ).select_related("from_character")
    )
    appearances = character.appearances.select_related("entry").order_by("entry__order")
    return True, character, relationships, appearances


def get_public_entry(
    journal: Journal, entry_slug: str, is_owner: bool = False, lang: str = "en",
) -> tuple[bool, JournalEntry | None, JournalEntry | None, JournalEntry | None, int]:
    entry = JournalEntry.objects.filter(journal=journal, slug=entry_slug).first()
    if not entry:
        return False, None, None, None, 0
    if entry.is_draft and not is_owner:
        return False, None, None, None, 0
    entry.translate(lang)
    prev_entry, next_entry = get_entry_navigation(journal, entry)
    chapter_number = 0
    if journal.mode in ("book", "light_novel") and entry.volume:
        chapter_number = JournalEntry.objects.filter(
            journal=journal, volume=entry.volume, order__lte=entry.order,
        ).count()
    return True, entry, prev_entry, next_entry, chapter_number


def get_entry_navigation(
    journal: Journal, entry: JournalEntry
) -> tuple[JournalEntry | None, JournalEntry | None]:
    qs = JournalEntry.objects.filter(journal=journal, is_draft=False)
    if journal.mode in ("book", "light_novel", "short_stories"):
        prev_entry = qs.filter(order__lt=entry.order).order_by("-order").first()
        next_entry = qs.filter(order__gt=entry.order).order_by("order").first()
    elif journal.mode == "diary":
        prev_entry = (
            qs.filter(entry_date__lt=entry.entry_date).order_by("-entry_date").first()
            if entry.entry_date else None
        )
        next_entry = (
            qs.filter(entry_date__gt=entry.entry_date).order_by("entry_date").first()
            if entry.entry_date else None
        )
    elif journal.mode == "poetry":
        prev_entry = qs.filter(order__lt=entry.order).order_by("-order").first()
        next_entry = qs.filter(order__gt=entry.order).order_by("order").first()
    else:
        prev_entry = qs.filter(created_at__gt=entry.created_at).order_by("created_at").first()
        next_entry = qs.filter(created_at__lt=entry.created_at).order_by("-created_at").first()
    return prev_entry, next_entry


def get_entry_chapter_list(journal: Journal) -> tuple[list, list]:
    published_qs = JournalEntry.objects.filter(journal=journal, is_draft=False).order_by("order")
    volumes_with_entries = list(
        Volume.objects.filter(journal=journal).prefetch_related(
            Prefetch("entries", queryset=published_qs)
        ).order_by("order")
    )
    unassigned_entries = list(published_qs.filter(volume__isnull=True))
    return volumes_with_entries, unassigned_entries


def get_book_stats(journal: Journal, is_owner: bool = False) -> dict[str, Any]:
    from django.db.models import Sum

    all_entries = JournalEntry.objects.filter(journal=journal).order_by("order")
    if not is_owner:
        all_entries = all_entries.filter(is_draft=False)
    total_words = all_entries.aggregate(total=Sum("word_count"))["total"] or 0
    published = JournalEntry.objects.filter(journal=journal, is_draft=False)
    drafts = JournalEntry.objects.filter(journal=journal, is_draft=True)
    first_entry = published.order_by("volume__order", "order").first()
    return {
        "total_word_count": total_words,
        "published_count": published.count(),
        "draft_count": drafts.count() if is_owner else 0,
        "first_entry": first_entry,
        "volume_count": Volume.objects.filter(journal=journal).count(),
        "character_count": Character.objects.filter(journal=journal).count(),
    }


def get_book_view_data(journal: Journal, is_owner: bool = False) -> dict[str, Any]:
    entry_qs = JournalEntry.objects.filter(journal=journal).order_by("order")
    if not is_owner:
        entry_qs = entry_qs.filter(is_draft=False)

    volumes_with_entries = (
        Volume.objects.filter(journal=journal).prefetch_related(
            Prefetch("entries", queryset=entry_qs)
        )
        .annotate(entries_count=Count("entries"))
        .order_by("order")
    )
    unassigned = entry_qs.filter(volume__isnull=True)
    characters = Character.objects.filter(journal=journal).order_by("order")
    tags = journal.entry_tags.all()
    stats = get_book_stats(journal, is_owner=is_owner)

    return {
        "volumes_with_entries": volumes_with_entries,
        "unassigned_entries": unassigned,
        "characters": characters,
        "tags": tags,
        "book_stats": stats,
    }


def get_short_stories_view_data(
    journal: Journal, is_owner: bool = False, genre: str = "", tone: str = "",
) -> dict[str, Any]:
    from django.db.models import Sum

    entry_qs = JournalEntry.objects.filter(journal=journal).order_by("order")
    if not is_owner:
        entry_qs = entry_qs.filter(is_draft=False)

    total_words = entry_qs.aggregate(total=Sum("word_count"))["total"] or 0
    characters = Character.objects.filter(journal=journal).order_by("order")
    tags = journal.entry_tags.all()

    genre_counts: dict[str, int] = {}
    for g in entry_qs.exclude(genre="").values_list("genre", flat=True):
        genre_counts[g] = genre_counts.get(g, 0) + 1

    genre_labels = dict(GENRE_CHOICES)
    available_genres = [
        {"value": g, "label": genre_labels.get(g, g), "count": c}
        for g, c in genre_counts.items()
    ]

    tone_counts: dict[str, int] = {}
    for t in entry_qs.exclude(tone="").values_list("tone", flat=True):
        tone_counts[t] = tone_counts.get(t, 0) + 1

    tone_labels = dict(TONE_CHOICES)
    available_tones = [
        {"value": t, "label": tone_labels.get(t, t), "count": c}
        for t, c in tone_counts.items()
    ]

    filtered_entries = entry_qs
    if genre and genre in genre_counts:
        filtered_entries = filtered_entries.filter(genre=genre)
    if tone and tone in tone_counts:
        filtered_entries = filtered_entries.filter(tone=tone)

    return {
        "characters": characters,
        "tags": tags,
        "ss_entries": filtered_entries,
        "available_genres": available_genres,
        "active_genre": genre if genre in genre_counts else "",
        "available_tones": available_tones,
        "active_tone": tone if tone in tone_counts else "",
        "ss_stats": {
            "published_count": entry_qs.filter(is_draft=False).count() if is_owner else entry_qs.count(),
            "total_word_count": total_words,
            "character_count": characters.count(),
        },
    }


def get_poetry_view_data(
    journal: Journal, is_owner: bool = False, form: str = "", mood: str = "", page: int = 1, per_page: int = 5,
) -> dict[str, Any]:
    entry_qs = JournalEntry.objects.filter(journal=journal).order_by("order")
    if not is_owner:
        entry_qs = entry_qs.filter(is_draft=False)

    form_counts: dict[str, int] = {}
    for f in entry_qs.exclude(form="").values_list("form", flat=True):
        form_counts[f] = form_counts.get(f, 0) + 1

    form_labels = dict(FORM_CHOICES)
    available_forms = [
        {"value": f, "label": form_labels.get(f, f), "count": c}
        for f, c in form_counts.items()
    ]

    mood_counts: dict[str, int] = {}
    for m in entry_qs.exclude(mood="").values_list("mood", flat=True):
        mood_counts[m] = mood_counts.get(m, 0) + 1

    mood_labels = dict(MOOD_CHOICES)
    available_moods = [
        {"value": m, "label": mood_labels.get(m, m), "count": c}
        for m, c in mood_counts.items()
    ]

    filtered_entries = entry_qs
    if form and form in form_counts:
        filtered_entries = filtered_entries.filter(form=form)
    if mood and mood in mood_counts:
        filtered_entries = filtered_entries.filter(mood=mood)

    paginator = Paginator(filtered_entries, per_page)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    total_count = entry_qs.filter(is_draft=False).count() if is_owner else entry_qs.count()

    return {
        "pe_entries": page_obj.object_list,
        "pe_jump_entries": filtered_entries,
        "pe_page": page_obj,
        "available_forms": available_forms,
        "active_form": form if form in form_counts else "",
        "available_moods": available_moods,
        "active_mood": mood if mood in mood_counts else "",
        "pe_stats": {
            "published_count": total_count,
        },
    }


def get_poetry_entry_data(journal: Journal, entry: JournalEntry, is_owner: bool = False) -> dict[str, Any]:
    all_entries = JournalEntry.objects.filter(journal=journal).order_by("order")
    if not is_owner:
        all_entries = all_entries.filter(is_draft=False)

    return {
        "all_entries": all_entries,
    }


def get_short_stories_entry_data(journal: Journal, entry: JournalEntry, is_owner: bool = False) -> dict[str, Any]:
    all_entries = JournalEntry.objects.filter(journal=journal).order_by("order")
    if not is_owner:
        all_entries = all_entries.filter(is_draft=False)

    entry_characters = Character.objects.filter(
        appearances__entry=entry,
    ).order_by("order")

    return {
        "all_entries": all_entries,
        "entry_characters": entry_characters,
    }


def get_journal_toc(journal: Journal) -> tuple[Any, Any]:
    volumes = (
        journal.volumes.prefetch_related(
            Prefetch("entries", queryset=journal.entries.order_by("order"))
        )
        .annotate(entries_count=Count("entries"))
        .order_by("order")
    )
    unassigned = journal.entries.filter(volume__isnull=True).order_by("order")
    return volumes, unassigned


def get_diary_calendar(journal: Journal, year: int, month: int) -> dict[str, Any]:
    import calendar

    entries = journal.entries.filter(
        entry_date__year=year, entry_date__month=month,
    ).values_list("entry_date", "title", "slug", "mood")
    cal = calendar.Calendar(firstweekday=0)
    days = list(cal.itermonthdays2(year, month))
    entries_by_day: dict[int, dict[str, Any]] = {}
    for entry_date, title, slug, mood in entries:
        entries_by_day[entry_date.day] = {
            "title": title, "slug": slug, "mood": mood, "date": entry_date,
        }
    return {
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "days": days,
        "entries": entries_by_day,
    }
