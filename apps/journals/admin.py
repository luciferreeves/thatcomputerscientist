from django.contrib import admin

# Register your models here.
from apps.journals.models import Journal, JournalEntry

admin.site.register(Journal)
admin.site.register(JournalEntry)
