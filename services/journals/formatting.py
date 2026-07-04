_SMALL_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "if", "in", "nor",
    "of", "on", "or", "per", "so", "the", "to", "up", "via", "vs", "with", "yet",
}


def to_title_case(value: str) -> str:
    words = value.split()
    if not words:
        return value
    last = len(words) - 1
    titled: list[str] = []
    for index, word in enumerate(words):
        lowered = word.lower()
        if 0 < index < last and lowered in _SMALL_WORDS:
            titled.append(lowered)
        else:
            titled.append(lowered[0].upper() + lowered[1:])
    return " ".join(titled)
