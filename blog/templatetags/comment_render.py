import re
from django import template
from internal.weblog_utilities import highlight_code, check_link_safety

register = template.Library()


@register.filter
def render_comment(comment):
    comment = comment.replace("<", "&lt;").replace(">", "&gt;")

    code_placeholders = []

    def extract_code_block(match):
        code_block = match.group(1).strip()
        if code_block.startswith("lang-"):
            parts = code_block.split("\n", 1)
            if len(parts) == 2:
                lang_line, code = parts
                language = lang_line.replace("lang-", "").strip()
                placeholder = (
                    f'<pre data-language="{language}"><code>{code.strip()}</code></pre>'
                )
            else:
                placeholder = f"<pre><code>{code_block}</code></pre>"
        else:
            placeholder = f"<pre><code>{code_block}</code></pre>"
        code_placeholders.append(placeholder)
        return f"[[[CODE_BLOCK_{len(code_placeholders) - 1}]]]"

    comment = re.sub(r"```(.+?)```", extract_code_block, comment, flags=re.DOTALL)

    def replace_link(match):
        url = match.group(1)
        if check_link_safety(url):
            return f'<a href="{url}" target="_blank">{url}</a>'
        return f'{url}<span style="color: red"> (Seems unsafe! Proceed with caution)</span>'

    comment = re.sub(r"(https?://[^\s]+)", replace_link, comment)

    formatting = [
        (r"\*\*(.+?)\*\*", r"<b>\1</b>"),
        (r"__(.+?)__", r"<i>\1</i>"),
        (r"~~(.+?)~~", r"<s>\1</s>"),
    ]
    for pattern, repl in formatting:
        comment = re.sub(pattern, repl, comment)

    lines = comment.splitlines()
    blocks = []
    buffer = []
    for line in lines:
        if line.strip():
            buffer.append(line.strip())
        else:
            if buffer:
                blocks.append("<p>" + " ".join(buffer) + "</p>")
                buffer = []
    if buffer:
        blocks.append("<p>" + " ".join(buffer) + "</p>")

    comment = "".join(blocks)

    for i, block in enumerate(code_placeholders):
        comment = comment.replace(f"[[[CODE_BLOCK_{i}]]]", block)

    return highlight_code(comment)
