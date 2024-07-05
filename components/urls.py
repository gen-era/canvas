from django.urls import include, path

urlpatterns = [
    path("chip_search/", include("components.chip_search.urls")),
    path("sample_search/", include("components.sample_search.urls")),
    path("institution_search/", include("components.institution_search.urls")),
]
