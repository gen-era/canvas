from django.shortcuts import render
from django.conf import settings
from django.views import View
from django.http import HttpResponse

from canvas.models import Sample, Chip, ChipSample, Institution, IDAT

from datetime import timedelta
import json

import minio


def index(request):

    return render(
        request,
        "canvas/index.html",
        {
            "title": "Index",
            "description": "Chip search of a Django model",
        },
    )


class InstitutionSearch(View):
    tbody_temp = "canvas/components/institution_search_tbody.html"

    def post(self, request, *args, **kwargs):
        search = request.POST.get("search")
        if not search:
            return render(request, self.tbody_temp, context)
        institutions = Institution.objects.filter(name__icontains=search)
        context = {"institutions": institutions.order_by("id")[:10]}

        return render(request, self.tbody_temp, context)


class ChipSearch(View):
    tbody_temp = "canvas/components/chip_search_tbody.html"

    def post(self, request, *args, **kwargs):
        search = request.POST.get("search")
        print(request.POST)
        if not search:
            return render(request, self.tbody_temp, context)
        chips = Chip.objects.filter(chip_id__icontains=search) | Chip.objects.filter(
            chip_type__name__icontains=search
        )
        context = {"chips": chips.order_by("id")[:10]}

        return render(request, self.tbody_temp, context)


class SampleSearch(View):
    tbody_temp = "canvas/components/sample_search_tbody.html"

    def post(self, request, *args, **kwargs):
        search = request.POST.get("search")
        if not search:
            return render(request, self.tbody_temp, context)
        samples = Sample.objects.filter(
            protocol_id__icontains=search
        ) | Sample.objects.filter(sample_type__name__icontains=search)
        context = {"samples": samples.order_by("id")[:10]}

        return render(request, self.tbody_temp, context)


class OmniSearch(View):
    tbody_temp = "canvas/components/search_results.html"

    def post(self, request, *args, **kwargs):
        print(request.POST)
        institution_search = request.POST.get("institution_search", None)
        chip_search = request.POST.get("chip_search", None)
        sample_search = request.POST.get("sample_search", None)

        institutions = Institution.objects.filter(name__icontains=institution_search)

        context = {"institutions": institutions.order_by("id")[:10]}

        chips = Chip.objects.filter(
            chip_id__icontains=chip_search
        ) | Chip.objects.filter(chip_type__name__icontains=chip_search)
        context = {"chips": chips.order_by("id")[:10]}

        samples = Sample.objects.filter(
            protocol_id__icontains=sample_search
        ) | Sample.objects.filter(sample_type__name__icontains=sample_search)
        context = {"samples": samples.order_by("id")[:10]}

        return render(request, self.tbody_temp, context)


def get_presigned_url(bucket_name, file_name, expiration=600):

    client = minio.Minio(
        settings.MINIO_STORAGE_ENDPOINT,
        settings.MINIO_STORAGE_ACCESS_KEY,
        settings.MINIO_STORAGE_SECRET_KEY,
        secure=False,
    )

    return client.presigned_put_object(
        bucket_name, file_name, expires=timedelta(hours=2)
    )


class ChipUpload(View):
    template_name = "canvas/components/uploader.html"

    def post(self, request, *args, **kwargs):
        bucket_name = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME

        idats = request.FILES.getlist("file")

        presigned_urls = {}
        for idat in idats:
            presigned_urls[idat.name] = get_presigned_url(bucket_name, idat.name)
            idat_obj = IDAT(idat=f"{bucket_name}/{idat.name}")
            idat_obj.save()

        context = {
            "presigned_urls": json.dumps(presigned_urls),
            "path": f"to {bucket_name}",
        }

        return render(request, self.template_name, context)
