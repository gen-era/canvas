from django_components import component

from django.conf import settings
import minio
from datetime import timedelta


def get_presigned_url(bucket_name, file_name, expiration=600):

    client = minio.Minio(
        settings.MINIO_STORAGE_ENDPOINT,
        settings.MINIO_STORAGE_ACCESS_KEY,
        settings.MINIO_STORAGE_SECRET_KEY,
        secure=False,
    )

    return client.presigned_put_object(
        bucket_name, file_name, expires=timedelta(hours=2)
    )


@component.register("chip_upload")
class ChipUpload(component.Component):
    """
    We render the page with or without data for a presigned post upload.
    """

    template_name = "uploader.html"

    def post(self, *args, **kwargs):
        file = self.request.FILES["file"]
        name = file.name
        # content_type = file.content_type

        # Add any Django form validation here to check the file is valid, correct size, type, etc.

        bucket_name = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
        presigned_url = get_presigned_url(bucket_name, name)

        context = {
            "url": presigned_url,
            "path": f"to {bucket_name}/{name}",
        }

        return self.render_to_response(context)
