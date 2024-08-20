from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sample_search", views.sample_search, name="sample_search"),
    path(
        "institution_search/",
        views.institution_search,
        name="institution_search",
    ),
    path("chip_search", views.chip_search, name="chip_search"),
    path(
        "chipsample_tab_content",
        views.chipsample_tab_content,
        name="chipsample_tab_content",
    ),
    path(
        "chipsample_tab_button",
        views.chipsample_tab_button,
        name="chipsample_tab_button",
    ),
    path("chip_upload", views.ChipUpload.as_view(), name="chip_upload"),
]
