from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.Search.as_view(), name="search"),
    path("chip_upload", views.ChipUpload.as_view(), name="chip_upload"),
]
