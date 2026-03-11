from core.letters.functions import get_total_unread_count


def unread_letter_count(request):
    if request.user.is_authenticated:
        return {"unread_letter_count": get_total_unread_count(request.user)}
    return {"unread_letter_count": 0}
