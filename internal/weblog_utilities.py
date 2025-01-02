from apps.blog.models import Post, Comment
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup
import html

AUTHOR_USERNAME = "bobby"


def add_excerpt(post, lang="en"):
    if lang == "ja":
        soup = BeautifulSoup(post.body_ja, "html.parser")
    else:
        soup = BeautifulSoup(post.body, "html.parser")
    excerpt = ""
    for paragraph in soup.find_all("p"):
        paragraph = "<p>" + str(paragraph.text) + "</p>"
        excerpt += str(paragraph)

        if len(excerpt) >= 1000:
            break
    return excerpt


def recent_weblogs(lang="en", amount=3):
    recent_posts = Post.objects.filter(
        is_public=True, author__username=AUTHOR_USERNAME
    ).order_by("-date")[:amount]
    for post in recent_posts:
        post.excerpt = add_excerpt(post, lang)
    return recent_posts


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
            style="native",
            wrapcode=True,
            cssstyles="background: none; padding: 8px 0;",
        )

        highlighted = highlight(code, lexer, formatter)
        pre.clear()
        pre.append(BeautifulSoup(highlighted, "html.parser"))

    return str(soup)
