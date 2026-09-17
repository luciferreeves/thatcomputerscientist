from django.db import models


class SongMetadata(models.Model):
    title = models.CharField(max_length=255)
    artists = models.CharField(max_length=255)
    album = models.CharField(max_length=255)
    spotify_id = models.CharField(max_length=255, unique=True)
    spotify_uri = models.CharField(max_length=255, unique=True)
    album_art_url = models.URLField(max_length=255)
    custom_album_art = models.URLField(max_length=255, blank=True, null=True)
    duration_ms = models.IntegerField(blank=True, null=True)
    explicit = models.BooleanField(default=False)
    release_date = models.DateField(blank=True, null=True)
    streaming_url = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.artists}"

    class Meta:
        verbose_name = "Song Metadata"
        verbose_name_plural = "Song Metadata"
