from django.urls import path

from components.sample_search.tbody import TBodysampleSearchComponent

urlpatterns = [
    path(
        "search/",
        TBodysampleSearchComponent.as_view(),
        name="tbody_sample_search",
    ),
]
