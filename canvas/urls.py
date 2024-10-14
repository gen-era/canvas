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
    path("idat_upload", views.idat_upload, name="idat_upload"),
    path(
        "get_sample_input_row/", views.get_sample_input_row, name="get_sample_input_row"
    ),
    path("save_samples/", views.save_samples, name="save_samples"),
    path("create_report/", views.create_report, name="create_report"),
    path("get_reports/", views.get_reports, name="get_reports"),
    path("chip_edit/", views.chip_edit, name="chip_edit"),
    path("chip_search", views.chip_search, name="chip_search"),
]
