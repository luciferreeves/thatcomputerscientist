import os
import re

# import akismet
import dotenv
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.cache import cache

# from pygments import highlight
# from pygments.formatters import HtmlFormatter
# from pygments.lexers import get_lexer_by_name, guess_lexer
# import google.generativeai as genai

from .models import Category, Comment, Post

dotenv.load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# akismet_api = akismet.Akismet(
#     key=os.getenv("AKISMET_API_KEY"),
#     blog_url=(
#         "https://preview.thatcomputerscientist.com"
#         if settings.DEBUG
#         else "https://thatcomputerscientist.com"
#     ),
# )


def check_spam(comment, post):
    # spam = False
    # akismet_data = {
    #     "comment_type": "comment",
    #     "comment_author": author,
    #     "comment_content": comment,
    #     "is_test": settings.DEBUG,
    # }
    # spam = akismet_api.comment_check(user_ip, user_agent, **akismet_data)

    # if spam:
    #     return spam

    # Now we check with Google Generative AI
    # if gemini_api_key is None:
    #     return True
    # else:
    #     genai.configure(api_key=gemini_api_key)

    # model = genai.GenerativeModel("gemini-pro")
    # print(comment)

    # input_prompt = f"Comment Processing Checker. This is for a personal blog site. Output only Y or N for the included text. Y if the comment seems like spam, or random gibberish or a bunch of letters which make no sense or looks like a coupon code or something. Only block spam, nothing else. If a comment contains cuss words, personal attacks, profanity or any possible harrasment, it is NOT spam (unless it contains spammy gibberish or links). This is a strict spam only filter. N if the comment is not spam. Do not access links. Just mark Y or N for the text. Post Title: {post.title}. \n Comment: {comment}. \n Judge if the comment belongs on the post or not. Random texts, links, and gibberish are considered spam. Trying to phish or promote shady links are also considered spam. Output single character - either Y or N only."

    # bn = [
    #     {
    #         "category": "HARM_CATEGORY_DANGEROUS",
    #         "threshold": "BLOCK_NONE",
    #     },
    #     {
    #         "category": "HARM_CATEGORY_HARASSMENT",
    #         "threshold": "BLOCK_NONE",
    #     },
    #     {
    #         "category": "HARM_CATEGORY_HATE_SPEECH",
    #         "threshold": "BLOCK_NONE",
    #     },
    #     {
    #         "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    #         "threshold": "BLOCK_NONE",
    #     },
    #     {
    #         "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    #         "threshold": "BLOCK_NONE",
    #     },
    # ]

    # response = model.generate_content(input_prompt, safety_settings=bn)

    # r_text = response.text

    # r_text = r_text.strip()

    # print(r_text)

    # return r_text

    return False


def add_excerpt(post):
    soup = BeautifulSoup(post.body, "html.parser")

    # Create excerpt, count min 1000 characters and max upto next paragraph
    excerpt = ""
    for paragraph in soup.find_all("p"):
        paragraph = "<p>" + str(paragraph.text) + "</p>"
        excerpt += str(paragraph)

        if len(excerpt) >= 1000:
            break
    return excerpt


def add_num_comments(post):
    num_comments = Comment.objects.filter(post=post).count()
    return num_comments


def recent_posts():
    recent_posts = Post.objects.filter(is_public=True).order_by("-date")[:5]
    for post in recent_posts:
        post.excerpt = add_excerpt(post)
        post.num_comments = add_num_comments(post)
    return recent_posts


def categories(request):
    categories = Category.objects.all()[0:5]
    return {"categories": categories}


def archives(request):
    archives = Post.objects.filter(is_public=True).dates("date", "month", order="DESC")[
        0:5
    ]
    return {"archives": archives}


def avatar_list():
    avatar_list = {}
    directory = os.path.join(settings.BASE_DIR, "static", "images", "avatars")
    for directory in os.listdir(directory):
        # ignore hidden files
        if directory.startswith("."):
            continue
        avatar_list[directory] = os.listdir(
            os.path.join(settings.BASE_DIR, "static", "images", "avatars", directory)
        )
        # remove hidden files
        for file in avatar_list[directory]:
            if file.startswith("."):
                avatar_list[directory].remove(file)
    return avatar_list


def highlight_code_blocks(code_block, language=None):
    # replace &nbsp; with space
    try:
        cb = code_block.string
    except:
        cb = code_block
    cb = cb.replace("\xa0", " ")

    # guess the language as there is no data-lang attribute
    if language:
        try:
            lexer = get_lexer_by_name(language.strip())
        except:
            lexer = get_lexer_by_name("text")
    else:
        try:
            lexer = guess_lexer(cb)
        except:
            lexer = get_lexer_by_name("text")
    # highlight the code
    formatter = HtmlFormatter(noclasses=True, style="native", wrapcode=True)
    highlighted_code = highlight(cb, lexer, formatter)

    return highlighted_code


def check_link_safety(link):
    api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
    api_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    cache_key = f"link_safety:{link}"
    cache_timeout = 60 * 60 * 24 * 7  # 7 days

    # Check if the result is already cached
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    payload = {
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION",
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": link}],
        }
    }

    headers = {"Content-Type": "application/json"}

    params = {"key": api_key, "alt": "json"}

    response = requests.post(api_url, params=params, headers=headers, json=payload)
    if response.status_code == 200:
        # Successful API call
        matches = response.json().get("matches", [])
        # Cache the result
        cache.set(cache_key, len(matches) == 0, cache_timeout)
        return len(matches) == 0
    else:
        # Handle API error
        print(f"Safe Browsing API error: {response.content}")

    return False


def comment_processor(comment):
    # escape html tags
    comment = re.sub(r"<", "&lt;", comment)
    comment = re.sub(r">", "&gt;", comment)

    # any text between ``` and ``` must be highlighted as code
    code_blocks = re.findall(r"```(.+?)```", comment, re.DOTALL)
    for code_block in code_blocks:
        if code_block.startswith("lang-"):
            language = code_block.split("\n")[0].replace("lang-", "")
            code_block = code_block.replace("lang-" + language + "\n", "")
            # comment = highlight_code_blocks(code_block.replace('&lt;', '<').replace('&gt;', '>'), language)
            comment = comment.replace(
                "```lang-" + language + "\n" + code_block + "```",
                highlight_code_blocks(
                    code_block.replace("&lt;", "<").replace("&gt;", ">"), language
                ),
            )
        else:
            comment = comment.replace(
                "```" + code_block + "```",
                highlight_code_blocks(
                    code_block.replace("&lt;", "<").replace("&gt;", ">")
                ),
            )

    # any http or https links must be converted to anchor tags
    links = re.findall(r"(https?://[^\s]+)", comment)
    for link in links:
        # check if the link is safe
        if check_link_safety(link):
            comment = comment.replace(
                link, '<a href="' + link + '" target="_blank">' + link + "</a>"
            )
        else:
            # do not replace the link if it is not safe. Add a warning message after the link instead
            comment = comment.replace(
                link,
                link
                + '<span style="color: red"> (Seems unsafe! Proceed with caution)</span>',
            )

    # retain line breaks, for every newline character, add a <br> tag
    comment = comment.replace("\n", "<br>")

    # replace multiple <br> tags with a single <br> tag
    comment = re.sub(r"<br>(\s*<br>)+", "<br><br>", comment)

    comment = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", comment)
    comment = re.sub(r"__(.+?)__", r"<i>\1</i>", comment)
    comment = re.sub(r"~~(.+?)~~", r"<s>\1</s>", comment)

    # remove any br tags at the end of the comment
    comment = re.sub(r"<br>$", "", comment)

    return comment
