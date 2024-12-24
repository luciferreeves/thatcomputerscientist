import os
from uuid import uuid4

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from internal.admin_utilities import MinioFileManager
from django.shortcuts import render


# Create your views here.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_storage_buckets(request):
    file_manager = MinioFileManager()
    buckets = file_manager.list_buckets()

    context = {
        "buckets": buckets,
    }

    return render(
        request, "en/administration/manage_storage_buckets_home.html", context
    )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def view_single_bucket(request, bucket_name):
    file_manager = MinioFileManager()
    objects = file_manager.list_objects(bucket_name)
    for obj in objects:
        file_type = obj["path"].split(".")[-1]
        obj["file_type"] = file_type.lower()

    context = {
        "bucket_name": bucket_name,
        "objects": objects,
    }

    return render(
        request, "en/administration/manage_storage_buckets_bucket.html", context
    )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def view_object_path(request, bucket_name, object_path):
    file_manager = MinioFileManager()
    objects = file_manager.list_objects(bucket_name, object_path)
    for obj in objects:
        file_type = obj["path"].split(".")[-1]
        obj["file_type"] = file_type.lower()

    object_path_s = ""
    if "/" in object_path:
        object_path_s = object_path.split("/")[-2]
    else:
        object_path = f"{object_path}/"

    up_url = f"/admin/storage-buckets/{bucket_name}/{object_path_s}"
    context = {
        "bucket_name": bucket_name,
        "object_path": object_path,
        "objects": objects,
        "up_url": up_url,
    }

    return render(
        request, "en/administration/manage_storage_buckets_bucket.html", context
    )


@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def create_folder(request):
    """
    Create a folder in a specified bucket.
    Requires staff permissions.
    """
    try:
        # For Django, parse POST data differently
        bucket_name = request.POST.get("bucket")
        folder_path = request.POST.get("folder_path", "").strip("/")

        # Additional debug logging
        print(f"Bucket: {bucket_name}")
        print(f"Folder Path: {folder_path}")
        print(f"Request POST: {request.POST}")
        print(f"Request body: {request.body}")

        # Validate inputs
        if not bucket_name or not folder_path:
            return JsonResponse(
                {"status": "error", "message": "Bucket and folder path are required"},
                status=400,
            )

        # Initialize file manager without user context
        file_manager = MinioFileManager()

        # Ensure folder path ends with a slash for Minio
        full_folder_path = f"{folder_path}/"

        # Attempt to create folder
        success = file_manager.create_folder(
            bucket=bucket_name, folder_path=full_folder_path
        )

        if success:
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Folder created successfully",
                    "folder_path": folder_path,
                }
            )
        else:
            return JsonResponse(
                {"status": "error", "message": "Failed to create folder"}, status=500
            )

    except Exception as e:
        # Log the full error for debugging
        import traceback

        traceback.print_exc()
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def upload_file(request):
    """
    Upload a file to a specified bucket.
    Requires user to be logged in.
    """
    try:
        # Get uploaded file
        uploaded_file = request.FILES.get("file")
        bucket_name = request.POST.get("bucket")
        current_path = request.POST.get("current_path", "")

        # Validate inputs
        if not uploaded_file or not bucket_name:
            return JsonResponse(
                {"status": "error", "message": "File and bucket are required"},
                status=400,
            )

        # Generate unique filename
        file_ext = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{uuid4()}{file_ext}"

        # Construct full path
        full_path = (
            os.path.join(current_path, unique_filename)
            if current_path
            else unique_filename
        )

        # Temporarily save file to local storage
        temp_file_path = default_storage.save(f"temp/{unique_filename}", uploaded_file)

        # Initialize file manager without user context
        file_manager = MinioFileManager()

        # Upload file
        success = file_manager.upload_file(
            bucket=bucket_name, file_path=temp_file_path, object_name=full_path
        )

        # Clean up temporary file
        default_storage.delete(temp_file_path)

        if success:
            return JsonResponse(
                {
                    "status": "success",
                    "message": "File uploaded successfully",
                    "filename": unique_filename,
                }
            )
        else:
            return JsonResponse(
                {"status": "error", "message": "Failed to upload file"}, status=500
            )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
