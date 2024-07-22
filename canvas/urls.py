from django.urls import path

from . import views
from .views import load_igv_browser

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.Search.as_view(), name="search"),
    path("sample/", views.SampleView.as_view(), name="sample"),
    path("chip_upload", views.ChipUpload.as_view(), name="chip_upload"),
    path('load-igv-browser/', load_igv_browser, name='load_igv_browser'),
]
