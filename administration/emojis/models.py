from django.db import models
from thatcomputerscientist.storage import MinioStorage


class Emoji(models.Model):
    name = models.CharField(max_length=64, unique=True)
    image = models.ImageField(upload_to="emojis/", storage=MinioStorage)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "emojis"

    def __str__(self):
        return f":{self.name}:"

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)
