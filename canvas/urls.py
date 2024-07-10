from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "institution_search",
        views.InstitutionSearch.as_view(),
        name="institution_search",
    ),
    path("chip_search", views.ChipSearch.as_view(), name="chip_search"),
    path("sample_search", views.SampleSearch.as_view(), name="sample_search"),
    path("omni_search", views.OmniSearch.as_view(), name="omni_search"),
    path("chip_upload", views.ChipUpload.as_view(), name="chip_upload"),
]
