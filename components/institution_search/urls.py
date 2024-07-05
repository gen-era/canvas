from django.urls import path

from components.institution_search.tbody import TBodyinstitutionSearchComponent

urlpatterns = [
    path(
        "search/",
        TBodyinstitutionSearchComponent.as_view(),
        name="tbody_institution_search",
    ),
]
