import re


def calculate_polynomial_hash(string, base=31):
    hash_value = 0
    p_base = len(string) + base
    for i, char in enumerate(string):
        char_value = ord(char)
        position_factor = i + 1
        hash_value += char_value * position_factor * p_base + char_value
        hash_value = (hash_value << 5) + hash_value + char_value
    return hash_value


def build_redirect_url(request):
    query_params = request.GET.urlencode()
    redirect_url = f"{request.path}"
    if query_params:
        redirect_url += f"?{query_params}"
    return redirect_url


def format_for_language(time_str, language):
    if language == "ja":
        time_str = re.sub(r"\s*(年|ヶ月|週間|日|時間|分)\s*", r"\1", time_str)
        time_str = re.sub(r",\s*", "", time_str)
    return time_str
