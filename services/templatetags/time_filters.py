from django import template
from django.template.defaultfilters import timesince
from django.utils.translation import gettext_lazy as _, get_language
from django.utils.timezone import localtime
import re

from internal.utils import format_for_language

register = template.Library()


@register.filter
def translated_timesince(value):
    local_time = localtime(value)
    time_str = timesince(local_time)

    translations = {
        "minute": str(_("minute")),
        "minutes": str(_("minutes")),
        "hour": str(_("hour")),
        "hours": str(_("hours")),
        "day": str(_("day")),
        "days": str(_("days")),
        "week": str(_("week")),
        "weeks": str(_("weeks")),
        "month": str(_("month")),
        "months": str(_("months")),
        "year": str(_("year")),
        "years": str(_("years")),
    }

    for english, translated in translations.items():
        time_str = re.sub(r"\b" + english + r"\b", translated, time_str)

    return format_for_language(time_str, get_language())
