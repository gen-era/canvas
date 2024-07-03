from django.urls import path

from components.chip_search.tbody import TBodyChipSearchComponent

urlpatterns = [
    path(
        "search/",
        TBodyChipSearchComponent.as_view(),
        name="tbody_chip_search",
    ),
]
