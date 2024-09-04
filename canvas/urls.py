from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sample_search", views.sample_search, name="sample_search"),
    path(
        "search/<str:model_name>/<str:field_name>/",
        views.generic_search,
        name="generic_search",
    ),
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
    path("save_samples/", views.save_samples, name="save_samples"),
]
