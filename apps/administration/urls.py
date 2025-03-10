from django.urls import path

from . import views

app_name = "administration"
urlpatterns = [
    path(
        "storage-buckets/", views.manage_storage_buckets, name="manage_storage_buckets"
    ),
    path(
        "storage-buckets/create-folder/",
        views.create_folder,
        name="manage_storage_bucket_create_folder",
    ),
    path(
        "storage-buckets/upload-file/",
        views.upload_file,
        name="manage_storage_bucket_upload_file",
    ),
    path(
        "storage-buckets/<str:bucket_name>/",
        views.view_single_bucket,
        name="view_single_bucket",
    ),
    path(
        "storage-buckets/<str:bucket_name>/<path:object_path>/",
        views.view_object_path,
        name="view_object_path",
    ),
]
