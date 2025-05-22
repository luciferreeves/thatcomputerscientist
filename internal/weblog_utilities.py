import html
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.styles.vim import VimStyle
from pygments.style import Style
from pygments.token import Comment


class ShifooHighlight(Style):
    """Custom Vim style with modified comment colors"""

    # Inherit all styles from VimStyle
    styles = dict(VimStyle.styles)

    # Override comment styles using proper token types
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
