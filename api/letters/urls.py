from django.urls import path

from api.letters import attachments

app_name = "letters"

urlpatterns = [
    path("attachments/upload/@<str:username>", attachments.upload, name="attachment_upload"),
    path("attachments/remove/<int:attachment_id>", attachments.remove, name="attachment_remove"),
]
