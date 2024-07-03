from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("chip_search", views.chip_search, name="chip_search"),
]
