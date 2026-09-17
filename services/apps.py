from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services'
    verbose_name = _("Services")

    def ready(self):
        import services.journals.signals  # noqa: F401
        import services.weblog.models  # noqa: F401
