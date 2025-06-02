import html
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.styles.vim import VimStyle
from pygments.style import Style
from pygments.token import Comment
from internal.utils import calculate_polynomial_hash


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
