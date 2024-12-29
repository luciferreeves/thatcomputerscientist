from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def color_to_rgb(value):
    """Convert hex color to RGB values"""
    # Remove hash if present
    value = value.lstrip("#")
    # Handle both 3 and 6 character hex
    if len(value) == 3:
        value = "".join(c + c for c in value)
    if len(value) == 6:
        r = int(value[:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
        return f"{r}, {g}, {b}"
    return "141, 141, 255"  # Default fallback
