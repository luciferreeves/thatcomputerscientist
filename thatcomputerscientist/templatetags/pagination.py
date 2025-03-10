from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def set_page_param(querydict, page_number):
    """
    Update page parameter while preserving all other query parameters
    Usage: {{ request.GET|set_page_param:2 }}
    """
    params = querydict.copy()
    params["page"] = str(page_number)
    return params.urlencode()


@register.filter
def get_page_range(total_pages, current_page):
    """Generate pagination range with ellipsis"""
    current_page = int(current_page)
    total_pages = int(total_pages)

    if total_pages <= 7:
        return range(1, total_pages + 1)

    pages = []
    if current_page <= 4:
        pages.extend(range(1, 6))
        pages.append("...")
        pages.append(total_pages)
    elif current_page >= total_pages - 3:
        pages.append(1)
        pages.append("...")
        pages.extend(range(total_pages - 4, total_pages + 1))
    else:
        pages.append(1)
        pages.append("...")
        pages.extend(range(current_page - 1, current_page + 2))
        pages.append("...")
        pages.append(total_pages)

    return pages
