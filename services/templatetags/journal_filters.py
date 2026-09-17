from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


@register.filter
def dictget(d: dict[Any, Any], key: Any) -> Any:
    if isinstance(d, dict):
        return d.get(key)
    return None
