from django.urls import path

from components.chip_upload.chip_upload import ChipUpload

urlpatterns = [
    path(
        "upload",
        ChipUpload.as_view(),
        name="chip_upload",
    ),
]
