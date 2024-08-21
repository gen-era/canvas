from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator

from django.views.generic.base import TemplateView

from canvas.models import Sample, Chip, ChipSample, Institution, IDAT, BedGraph
from django.contrib.auth.decorators import login_required

from datetime import timedelta
import json

import minio


def index(request):

    samples = Sample.objects.order_by("-entry_date")
    paginator = Paginator(samples, 12)
    samples = paginator.get_page(1)

    return render(
        request,
        "canvas/index.html",
        {
            "title": "Index",
            "samples": samples,
        },
    )


@login_required
def institution_search(request):
    query = request.POST.get("search", "")
    if query:
        institutions = Institution.objects.filter(name__icontains=query)
    else:
        institutions = Institution.objects.none()

    return render(
        request,
        "canvas/partials/search_results.html",
        {"items": institutions},
    )


@login_required
def chip_search(request):
    query = request.POST.get("search", "")
    if query:
        chips = Chip.objects.filter(chip_id__icontains=query)
    else:
        chips = Chip.objects.none()

    return render(
        request,
        "canvas/partials/search_results.html",
        {"items": chips},
    )


@login_required
def sample_search(request):
    query = request.GET.get("search", "")
    page = request.GET.get("page")
    institutions = request.GET.getlist("institutions")
    chips = request.GET.getlist("chips")

    # Start with filtering by protocol ID
    samples = Sample.objects.filter(protocol_id__icontains=query)

    # Filter by institutions if any are selected
    if institutions:
        samples = samples.filter(institution__name__in=institutions)

    # Assuming a relationship exists, filter by chips
    if chips:
        samples = samples.filter(chipsample__chip__chip_id__in=chips)

    # Order by entry date
    samples = samples.order_by("-entry_date")

    paginator = Paginator(samples, 12)
    samples = paginator.get_page(page)
    return render(
        request,
        "canvas/partials/sample_results.html",
        {"samples": samples, "query": query},
    )


@login_required
def chipsample_tab_button(request):
    chipsample_pk = request.GET.get("chipsample_pk")
    chipsample = ChipSample.objects.get(id=chipsample_pk)
    return render(
        request,
        "canvas/partials/chipsample_tab_button.html",
        {"chipsample": chipsample},
    )


@login_required
def chipsample_tab_content(request):
    chipsample_pk = request.GET.get("chipsample_pk")
    chipsample = ChipSample.objects.get(id=chipsample_pk)
    bedgraphs = chipsample.bedgraph.all()

    return render(
        request,
        "canvas/partials/chipsample_tab_content.html",
        {"chipsample": chipsample, "bedgraphs": bedgraphs},
    )


@login_required
def put_presigned_url(bucket_name, file_name, expiration=600):

    client = minio.Minio(
        settings.MINIO_STORAGE_ENDPOINT,
        settings.MINIO_STORAGE_ACCESS_KEY,
        settings.MINIO_STORAGE_SECRET_KEY,
        secure=False,
    )

    return client.presigned_put_object(
        bucket_name, file_name, expires=timedelta(hours=2)
    )


@login_required
def get_presigned_url(bucket_name, file_path, expiration=600):

    client = minio.Minio(
        settings.MINIO_STORAGE_ENDPOINT,
        settings.MINIO_STORAGE_ACCESS_KEY,
        settings.MINIO_STORAGE_SECRET_KEY,
        secure=False,
    )

    return client.presigned_get_object(
        bucket_name, file_path, expires=timedelta(seconds=expiration)
    )


class ChipUpload(View):
    template_name = "canvas/components/uploader.html"

    def post(self, request, *args, **kwargs):
        bucket_name = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME

        idats = request.FILES.getlist("file")

        presigned_urls = {}
        for idat in idats:
            presigned_urls[idat.name] = put_presigned_url(bucket_name, idat.name)
            idat_obj = IDAT(idat=f"{bucket_name}/{idat.name}")
            idat_obj.save()

        context = {
            "presigned_urls": json.dumps(presigned_urls),
            "path": f"to {bucket_name}",
        }

        return render(request, self.template_name, context)
