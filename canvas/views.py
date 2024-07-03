from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return render(request, "canvas/index.html")


def chip_search(request):
    print("Canvas view chip_search!")

    return render(
        request,
        "canvas/chip_search.html",
        {
            "title": "Chip Search",
            "description": "Chip search of a Django model",
        },
    )
