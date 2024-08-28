from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator

from django.http import JsonResponse

from canvas.models import (
    Sample,
    Chip,
    ChipSample,
    Institution,
    IDAT,
    BedGraph,
    SampleType,
    ChipType,
)
from django.contrib.auth.decorators import login_required

from datetime import timedelta
import json

import secrets
import minio


def index(request):

    samples = Sample.objects.order_by("-entry_date")
    paginator = Paginator(samples, 12)
    samples = paginator.get_page(1)

    label = secrets.token_urlsafe(6)
    return render(
        request,
        "canvas/index.html",
        {
            "title": "Index",
            "samples": samples,
            "label": label,
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


def get_sample_input_row(request):
    label = secrets.token_urlsafe(6)
    return render(request, "canvas/partials/sample_input_row.html", {"label": label})


def save_samples(request):
    if request.method == "POST":
        protocol_id = request.POST.getlist("protocol_id")
        name = request.POST.getlist("name")
        institution = request.POST.getlist("institution")
        sample_type = request.POST.getlist("sample_type")
        arrival_date = request.POST.getlist("arrival_date")
        chip_type = request.POST.getlist("chip_type")
        study_date = request.POST.getlist("study_date")
        description = request.POST.getlist("description")
        concentration = request.POST.getlist("concentration")

        for i in range(len(protocol_id)):
            Sample.objects.create(
                protocol_id=protocol_id[i],
                institution=Institution.objects.get(name=institution[i]),
                sample_type=SampleType.objects.get(name=sample_type[i]),
                chip_type=ChipType.objects.get(name=chip_type[i]),
                arrival_date=arrival_date[i],
                study_date=study_date[i],
                description=description[i],
                concentration=concentration[i],
            )

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "failed"})


@login_required
def sample_type_search(request):
    query = request.POST.get("search", "")
    if query:
        types = SampleType.objects.filter(name__icontains=query)
    else:
        types = SampleType.objects.none()

    return render(
        request,
        "canvas/partials/search_results.html",
        {"items": types},
    )


@login_required
def chip_type_search(request):
    query = request.POST.get("chip-type-search", "")
    if query:
        chips = ChipType.objects.filter(name__icontains=query)
    else:
        chips = ChipType.objects.none()

    return render(
        request,
        "canvas/partials/search_results.html",
        {"items": chips},
    )

@login_required
def sample_input_sample_search(request):
    query = request.POST.get("search", "")
    if query:
        samples = Sample.objects.filter(protocol_id__icontains=query)
    else:
        samples = Sample.objects.none()

    return render(
        request,
        "canvas/partials/search_results.html",
        {"items": samples},
    )
