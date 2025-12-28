import html
import os
import requests
from google import genai
from bs4 import BeautifulSoup
from django.core.cache import cache
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.styles.vim import VimStyle
from pygments.style import Style
from pygments.token import Comment
from internal.utils import calculate_polynomial_hash

LINK_SAFETY_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class ShifooHighlight(Style):
    """Custom Vim style with modified comment colors"""

    styles = dict(VimStyle.styles)

    styles.update(
        {Comment: "#666666", Comment.Preproc: "#666666", Comment.Special: "#666666"}
    )


def highlight_code(html_content):
    if not html_content:
        return html_content

    soup = BeautifulSoup(html_content, "html.parser")
    pre_blocks = soup.find_all("pre")

    for pre in pre_blocks:
        code = html.unescape(pre.string or pre.text)
        code = code.replace("\xa0", " ")

        language = pre.get("data-language")

        try:
            if language:
                lexer = get_lexer_by_name(language.strip())
            else:
                lexer = guess_lexer(code)
        except:
            lexer = get_lexer_by_name("text")

        formatter = HtmlFormatter(
            noclasses=True,
            style=ShifooHighlight,
            wrapcode=True,
            cssstyles="background: none; padding: 8px 0;",
        )

        highlighted = highlight(code, lexer, formatter)
        pre.clear()
        pre.append(BeautifulSoup(highlighted, "html.parser"))

    return str(soup)


def get_post_color(post):
    colors = [
        "#FF8B8B",  # salmon
        "#75D151",  # lime green
        "#AD8CFF",  # lavender
        "#FFAA5E",  # peach
        "#87CEFA",  # light sky blue
        "#FFB3BA",  # pastel red
        "#42D6A4",  # mint green
        "#C774E8",  # purple
        "#FFDE59",  # yellow
        "#94D0FF",  # baby blue
        "#FF9AA2",  # salmon pink
        "#CAFFBF",  # light lime
        "#BDB2FF",  # pastel purple
        "#F7EA00",  # bright yellow
        "#FFD1DC",  # bubble gum pink
        "#54F2F2",  # cyan
        "#FFA8B8",  # coral pink
        "#90EE90",  # light green
        "#FF6AD5",  # bright pink
        "#C1E7E3",  # pastel teal
        "#8795E8",  # periwinkle
        "#FFDFBA",  # pastel orange
        "#4ADEDE",  # teal
        "#FB91D1",  # hot pink
        "#AFF8D8",  # mint
        "#FFF9B0",  # pastel yellow
        "#B5D8FF",  # pastel blue
        "#FCF6BD",  # light yellow
        "#D5AAFF",  # light purple
        "#9EE7FF",  # baby blue
        "#DCBEFF",  # light lavender
        "#E0BBE4",  # lavender
    ]

    slug = post.slug

    hash_value = calculate_polynomial_hash(slug)
    color_index = hash_value % len(colors)
    return colors[color_index]


def check_link_safety(link):
    if not LINK_SAFETY_API_KEY:
        return True

    cached = cache.get(f"link_safety:{link}")
    if cached is not None:
        return cached

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
    params = {"key": LINK_SAFETY_API_KEY, "alt": "json"}
    api_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    response = requests.post(api_url, params=params, headers=headers, json=payload)
    if response.status_code == 200:
        matches = response.json().get("matches", [])
        return len(matches) == 0
    else:
        return True


def strip_html_tags(html_content):
    if not html_content:
        return html_content
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def check_comment_spam(post, comment):
    if not GEMINI_API_KEY:
        return False

    client = genai.Client(api_key=GEMINI_API_KEY)
    model = "gemini-flash-latest"

    prompt = f"""
    Comment Spam Detection for shi.foo: Our personal site.
    You are an AI trained to detect spam comments specifically for the shi.foo site.
    shi.foo allows for multiple Weblogs, each can have multiple posts.
    Each post can have multiple comments. This is one of those comments which is about
    to be posted.
    There are certain rules for comments on shi.foo. All rules are to be followed strictly.
    1. Output only Y or N for spam or not spam.
    2. If the comments seems like spam, or random gibberish, or a bunch of letters or words
       which make no sense, or looks like a bot generated comment, or is promoting a product or service, or has a coupon code or something similar, output Y.
    3. Only block spam comments, and nothing else. If a comment has cuss words, personal attacks, profanity, or any possible offensive content, or any possible hate speech, or any
    harrasment, bullying, or abusive content, or anything similar, it does NOT count as spam,
    unless it contains any of the above mentioned spam content like coupon codes, gibberish, bot generated content, etc. Output N in such cases.
    4. This is a strict spam only filter, you are not to do any other filtering or moderation.
    5. You are not to access any external links which may be present in the comment. A separate link safety check will be done later.
    6. Trying to phish or scam users, or trying to get them to click on a shady link, or trying to get them to buy something, or trying to get them to sign up for something, or trying to get them to do anything which is not related to the post, is also considered spam, hence output Y.
    7. Additional context about the post is also attached below for better decision making.
    8. Output single character - either Y or N only.
    ------------
    Post Title: {post.title}
    Post Excerpt (First few lines): {strip_html_tags(post.excerpt)}
    Comment: {comment}
    """

    safety_settings = [
        {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            safety_settings=safety_settings
        )
    )
    result = response.text.strip()

    return result.upper() == "Y"  # Return True if spam, False otherwise
