from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from core.letters.functions import (
    find_user_by_username,
    get_or_create_conversation,
    upload_attachment,
    remove_attachment,
)


@login_required
@require_POST
def upload(request, username):
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file provided."}, status=400)

    success, user = find_user_by_username(username)
    if not success:
        return JsonResponse({"error": user}, status=404)

    conv_success, conv = get_or_create_conversation(request.user, user)
    if not conv_success:
        return JsonResponse({"error": conv}, status=400)

    success, result = upload_attachment(request.user, conv, file)
    if not success:
        return JsonResponse({"error": result}, status=400)

    return JsonResponse({
        "id": result.pk,
        "name": result.original_name,
        "size": result.file_size,
        "url": result.file.url,
    })


@login_required
@require_POST
def remove(request, attachment_id):
    success, result = remove_attachment(request.user, attachment_id)
    if not success:
        return JsonResponse({"error": result}, status=404)

    return JsonResponse({"ok": True})
