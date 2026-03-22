from __future__ import annotations

import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

EMPTY_P = re.compile(
    r"<p>\s*(?:<span[^>]*>\s*(?:<br\s*/?>)?\s*</span>|&nbsp;|\u00a0|<br\s*/?>|\s)*\s*</p>",
    re.IGNORECASE,
)


@register.filter(is_safe=True)
def cleanview(html: str) -> str:
    html = EMPTY_P.sub("", html)
    return mark_safe(html)
