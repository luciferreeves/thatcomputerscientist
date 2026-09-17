from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from administration.emojis.functions import get_all_emojis, create_emoji, delete_emoji


@login_required
@user_passes_test(lambda u: u.is_superuser)
def home(request):
    title_map = {
        "en": "Emoji Manager",
        "ja": "絵文字マネージャー",
    }
    request.meta.title = title_map.get(request.LANGUAGE_CODE)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            name = request.POST.get("name", "")
            image = request.FILES.get("image")
            if not name or not image:
                messages.error(request, "Name and image are required.")
            else:
                success, result = create_emoji(name, image)
                if success:
                    messages.success(request, f"Emoji :{result.name}: created.")
                else:
                    messages.error(request, result)

        elif action == "delete":
            emoji_id = request.POST.get("emoji_id")
            if delete_emoji(emoji_id):
                messages.success(request, "Emoji deleted.")
            else:
                messages.error(request, "Emoji not found.")

        return redirect("administration:emojis")

    context = {
        "emojis": get_all_emojis(),
    }
    return render(request, "administration/emojis.html", context)
