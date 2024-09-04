from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

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
    num_samples = len(samples)
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
            "num_samples": num_samples,
        },
    )


@login_required
def institution_search(request):
    query = request.POST.get("search", "").strip()
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
    query = request.POST.get("search", "").strip()
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
    num_samples = len(samples)

    paginator = Paginator(samples, 12)
    samples = paginator.get_page(page)
    return render(
        request,
        "canvas/partials/sample_results.html",
        {"samples": samples, "query": query, "num_samples": num_samples},
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
    cnvs = json.dumps([cnv.cnv_json for cnv in chipsample.cnv.all()])

    bedgraphs = chipsample.bedgraph.all()
    lrr_bedgraph = None
    baf_bedgraph = None
    for bedgraph in bedgraphs:
        if bedgraph.bedgraph_type == "LRR":
            lrr_bedgraph = bedgraph
        elif bedgraph.bedgraph_type == "BAF":
            baf_bedgraph = bedgraph

    return render(
        request,
        "canvas/partials/chipsample_tab_content.html",
        {
            "chipsample": chipsample,
            "lrr_bedgraph": lrr_bedgraph,
            "baf_bedgraph": baf_bedgraph,
            "cnvs": cnvs,
        },
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


@require_POST
@login_required
def save_samples(request):
    print(request.POST)
    samples_data = json.loads(request.POST.get('samples', '[]'))
    print(samples_data)

    return JsonResponse({'status': 'success', 'data': samples_data})

    # saved_samples = []
    # for sample_data in samples_data:
    #     institution, _ = Institution.objects.get_or_create(name=sample_data['institution'])
    #     sample_type, _ = SampleType.objects.get_or_create(name=sample_data['sample_type'])

    #     sample = Sample.objects.create(
    #         protocol_id=sample_data['protocol_id'],
    #         institution=institution,
    #         sample_type=sample_type,
    #         arrival_date=sample_data['arrival_date'],
    #         study_date=sample_data['study_date'] or None,
    #         description=sample_data['description'],
    #         concentration=sample_data['concentration']
    #     )

    #     if sample_data['repeat']:
    #         repeat_sample = Sample.objects.filter(protocol_id=sample_data['repeat']).first()
    #         if repeat_sample:
    #             sample.repeat.add(repeat_sample)

    #     saved_samples.append(sample)

    # return HttpResponse(f"Successfully saved {len(saved_samples)} samples.")

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
    query = request.POST.get("search", "")
    print(query)
    if query:
        chip_types = ChipType.objects.filter(name__icontains=query)
    else:
        chip_types = ChipType.objects.none()
    print(chip_types)
    return render(
        request,
        "canvas/partials/search_results.html",
        {"items": chip_types},
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

