from datetime import datetime
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.lexers.special import TextLexer
from pygments.formatters import HtmlFormatter


def text_lines(text):
    # return the number of lines in a text
    return len(text.split("\n")) - 1


def text_loc(text):
    text = text.strip()

    # return the number of lines of code in a text
    return len([line for line in text.split("\n") if line.strip()])


def size_format(size_bytes):
    if size_bytes == 0:
        return "0B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

    i = int(size_bytes // 1024)
    for size in size_name:
        if i == 0:
            return "{:.1f} {}".format(size_bytes, size)
        size_bytes /= 1024
        i = int(size_bytes // 1024)


def relative_date(entry):
    committedDate = datetime.strptime(
        entry["commit"]["committedDate"], "%Y-%m-%dT%H:%M:%SZ"
    )
    now = datetime.now()
    diff = now - committedDate
    if diff.days > 365:
        entry["commit"]["committedDate"] = (
            str(diff.days // 365)
            + " year"
            + ("s" if diff.days // 365 > 1 else "")
            + " ago"
        )
    elif diff.days > 30:
        entry["commit"]["committedDate"] = (
            str(diff.days // 30)
            + " month"
            + ("s" if diff.days // 30 > 1 else "")
            + " ago"
        )
    elif diff.days > 7:
        entry["commit"]["committedDate"] = (
            str(diff.days // 7) + " week" + ("s" if diff.days // 7 > 1 else "") + " ago"
        )
    elif diff.days > 0:
        entry["commit"]["committedDate"] = (
            str(diff.days) + " day" + ("s" if diff.days > 1 else "") + " ago"
        )
    elif diff.seconds > 3600:
        entry["commit"]["committedDate"] = (
            str(diff.seconds // 3600)
            + " hour"
            + ("s" if diff.seconds // 3600 > 1 else "")
            + " ago"
        )
    elif diff.seconds > 60:
        entry["commit"]["committedDate"] = (
            str(diff.seconds // 60)
            + " minute"
            + ("s" if diff.seconds // 60 > 1 else "")
            + " ago"
        )
    else:
        entry["commit"]["committedDate"] = "just now"

    return entry


def highlight_code(text, filename):
    print(filename)
    print(text)
    try:
        lexer = get_lexer_for_filename(filename, stripall=True)
    except:
        lexer = None

    formatter = HtmlFormatter(
        noclasses=True,
        style="native",
        wrapcode=True,
        linenos="inline",
        nobackground=True,
    )
    if lexer:
        return highlight(text, lexer, formatter)
    else:
        return highlight(text, TextLexer(), formatter)
