from django.db import models
from django.conf import settings


# Create your models here.
class PagodaSites(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    url = models.URLField()
    verified = models.BooleanField(default=False)
    siteUniqueIdentifier = models.TextField(unique=True)
    verificationMethod = models.CharField(
        max_length=4, choices=((x, x) for x in ["DNS", "Meta"]), default="DNS"
    )
    verficationRecordName = models.CharField(max_length=50, blank=True)
    verificationRecordValue = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_sites_created_by_user(user):
        return PagodaSites.objects.filter(owner=user)

    class Meta:
        verbose_name_plural = "Pagoda Sites"
        ordering = ["-created_at"]
