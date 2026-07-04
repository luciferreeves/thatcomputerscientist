from __future__ import annotations

from typing import Any

from django.http import HttpRequest

ADMIN_CSS = {"all": ("admin/services/admin.css",)}


class HiddenFromIndexMixin:
    def get_model_perms(self, request: HttpRequest) -> dict[str, bool]:
        return {}


class LinkInline:
    extra = 0
    can_delete = False
    template = "admin/services/edit_inline/link_tabular.html"
    add_url_name = ""
    add_fk = ""
    add_label = ""

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False


import services.journals.admin  # noqa: E402,F401
import services.weblog.admin  # noqa: E402,F401
