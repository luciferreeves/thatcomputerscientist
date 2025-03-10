from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.blog"

    # def ready(self):
    #     from jobs import updater

    #     updater.start()
