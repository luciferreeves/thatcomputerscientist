from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Max, Count

from core.letters.models import Conversation, Letter


def get_or_create_conversation(user_a, user_b):
    if user_a == user_b:
        return False, "You cannot start a conversation with yourself."

    p1, p2 = (user_a, user_b) if user_a.pk < user_b.pk else (user_b, user_a)

    conversation, created = Conversation.objects.get_or_create(
        participant_one=p1,
        participant_two=p2,
    )
    return True, conversation


def send_letter(sender, conversation, content):
    content = content.strip()
    if not content:
        return False, "Letter content is required."

    if sender not in (conversation.participant_one, conversation.participant_two):
        return False, "You are not a participant in this conversation."

    letter = Letter.objects.create(
        conversation=conversation,
        sender=sender,
        content=content,
    )

    conversation.save(update_fields=["updated_at"])

    return True, letter


def get_user_inbox(user, page=1):
    per_page = settings.LETTERS_INBOX_PER_PAGE

    conversations = (
        Conversation.objects.filter(
            Q(participant_one=user) | Q(participant_two=user)
        )
        .select_related("participant_one", "participant_two")
        .prefetch_related(
            "participant_one__userprofile_set",
            "participant_two__userprofile_set",
        )
        .annotate(
            last_letter_time=Max("letters__created_at"),
            unread_count=Count(
                "letters",
                filter=Q(letters__is_read=False) & ~Q(letters__sender=user),
            ),
        )
        .order_by("-updated_at")
    )

    paginator = Paginator(conversations, per_page)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    for conv in page_obj:
        conv.last_letter = (
            conv.letters.select_related("sender").order_by("-created_at").first()
        )
        conv.other_user = conv.get_other_participant(user)

    return True, page_obj


def get_conversation_letters(user, other_username, before_id=None):
    batch_size = settings.LETTERS_BATCH_SIZE

    other_user = User.objects.filter(username__iexact=other_username).first()
    if not other_user:
        return False, "User not found.", None

    p1, p2 = (user, other_user) if user.pk < other_user.pk else (other_user, user)

    conversation = (
        Conversation.objects.filter(participant_one=p1, participant_two=p2)
        .select_related("participant_one", "participant_two")
        .first()
    )

    if not conversation:
        return False, "Conversation not found.", None

    Letter.objects.filter(
        conversation=conversation,
        is_read=False,
    ).exclude(sender=user).update(is_read=True)

    letters_qs = conversation.letters.select_related("sender")

    if before_id:
        letters_qs = letters_qs.filter(pk__lt=before_id)

    letters = list(letters_qs.order_by("-created_at")[: batch_size + 1])
    has_more = len(letters) > batch_size
    letters = letters[:batch_size]

    # Reverse so they display oldest-first
    letters.reverse()

    conversation.other_user = conversation.get_other_participant(user)

    return True, conversation, {"letters": letters, "has_more": has_more}


def get_total_unread_count(user):
    return Letter.objects.filter(
        conversation__in=Conversation.objects.filter(
            Q(participant_one=user) | Q(participant_two=user)
        ),
        is_read=False,
    ).exclude(sender=user).count()


def find_user_by_username(username):
    user = User.objects.filter(username__iexact=username.strip()).first()
    if not user:
        return False, "User not found."
    return True, user
