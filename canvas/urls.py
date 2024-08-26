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
    path(
        "get_sample_input_row/", views.get_sample_input_row, name="get_sample_input_row"
    ),
    path("save_form/", views.save_form, name="save_form"),
    path("input-samples/", views.sample_input_page, name="sample_input_page"),
    path(
        "sample_type_search/",
        views.sample_type_search,
        name="sample_type_search",
    ),
    path(
        "chip_type_search/",
        views.chip_type_search,
        name="chip_type_search",
    ),
]
