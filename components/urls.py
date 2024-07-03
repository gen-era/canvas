from django.urls import include, path

urlpatterns = [
    path("chip_search/", include("components.chip_search.urls")),
]
