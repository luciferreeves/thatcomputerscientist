import re
from administration.emojis.models import Emoji

EMOJI_NAME_PATTERN = re.compile(r"^[a-z0-9_]+$")


def get_all_emojis():
    return Emoji.objects.all()


def get_emoji_data():
    return [{"name": e.name, "url": e.image.url} for e in Emoji.objects.all()]


def create_emoji(name, image):
    name = name.strip().lower()
    if not EMOJI_NAME_PATTERN.match(name):
        return False, "Emoji names can only contain lowercase letters, numbers, and underscores."
    if Emoji.objects.filter(name=name).exists():
        return False, "An emoji with that name already exists."
    emoji = Emoji.objects.create(name=name, image=image)
    return True, emoji


def delete_emoji(emoji_id):
    try:
        emoji = Emoji.objects.get(id=emoji_id)
        emoji.delete()
        return True
    except Emoji.DoesNotExist:
        return False
