from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

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


class Search(View):
    tbody_temp = "canvas/components/search_results.html"

    def post(self, request, *args, **kwargs):
        institution_search = request.POST.get("institution_search", None)
        chip_search = request.POST.get("chip_search", None)
        sample_search = request.POST.get("sample_search", None)
        print(f"""
        {institution_search=}
        {sample_search=}
        {chip_search=}
        """)

        if institution_search and chip_search and sample_search:
            print(f"""
            {institution_search=}
            {sample_search=}
            {chip_search=}
            """)
            institutions = Institution.objects.filter(name__icontains=institution_search)
            samples = Sample.objects.filter(protocol_id__icontains=sample_search, institution__in=institutions)
            chips = Chip.objects.filter(chip_id__icontains=chip_search)

            chip_ids = ChipSample.objects.filter(sample__in=samples, chip__in=chips).values_list("chip", flat=True)
            sample_ids = ChipSample.objects.filter(sample__in=samples, chip__in=chips).values_list("sample", flat=True)

            chips = Chip.objects.filter(id__in=chip_ids)
            samples = Sample.objects.filter(id__in=sample_ids)

        elif institution_search and chip_search:
            print(f"""
            {institution_search=}
            {chip_search=}
            """)
            pass

        elif institution_search and sample_search:
            print(f"""
            {institution_search=}
            {sample_search=}
            """)
            institutions = Institution.objects.filter(name__icontains=institution_search)
            
            samples = Sample.objects.filter(
                protocol_id__icontains=sample_search,
                institution__in = institutions
            )
            chip_ids = ChipSample.objects.filter(sample__in=samples).values_list("chip")
            chips = Chip.objects.filter(id__in=chip_ids)

        elif chip_search and sample_search:
            print(f"""
            {sample_search=}
            {chip_search=}
            """)
            pass

        elif institution_search:
            print(f"""
            {institution_search=}
            """)
            institutions = Institution.objects.filter(name__icontains=institution_search)
            samples = Sample.objects.filter(institution__in = institutions)
            chip_ids = ChipSample.objects.filter(sample__in=samples).values_list("chip")
            chips = Chip.objects.filter(id__in=chip_ids)

        elif chip_search:
            print(f"""
            {chip_search=}
            """)
            chips = Chip.objects.filter(chip_id__icontains=chip_search)
            chip_samples = ChipSample.objects.filter(chip__in=chips)
            sample_ids = chip_samples.values_list("sample", flat=True)
            samples = Sample.objects.filter(id__in=sample_ids)
            institution_ids = samples.values_list("institution", flat=True)
            institutions = Institution.objects.filter(id__in=institution_ids)

        elif sample_search:
            print(f"""
            {sample_search=}
            """)
            pass
        else:
            print(f"""
            Arama yok.
            """)
            # En son eklenenleri getir.
            pass


        context = {
            "samples": samples.order_by("id"),
            "chips": chips.order_by("id"),
            "institutions": institutions.order_by("id"),
        }
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

