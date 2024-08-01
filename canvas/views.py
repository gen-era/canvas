from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


from django_tables2 import MultiTableMixin
from .tables import InstitutionTable, ChipTable, SampleTable
from django.views.generic.base import TemplateView

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


class Search(MultiTableMixin, TemplateView):
    table_pagination = {"per_page": 5}
    template_name = "canvas/components/search_results.html"

    def get_tables(self):
        institution_search = self.request.GET.get("institution_search", None)
        chip_search = self.request.GET.get("chip_search", None)
        sample_search = self.request.GET.get("sample_search", None)

        if institution_search and chip_search and sample_search:
            print(
                f"""
            {institution_search=}
            {sample_search=}
            {chip_search=}
            """
            )
            institutions = Institution.objects.filter(
                name__icontains=institution_search
            )
            samples = Sample.objects.filter(
                protocol_id__icontains=sample_search, institution__in=institutions
            )
            chips = Chip.objects.filter(chip_id__icontains=chip_search)

            chip_ids = ChipSample.objects.filter(
                sample__in=samples, chip__in=chips
            ).values_list("chip", flat=True)
            sample_ids = ChipSample.objects.filter(
                sample__in=samples, chip__in=chips
            ).values_list("sample", flat=True)

            chips = Chip.objects.filter(id__in=chip_ids)
            samples = Sample.objects.filter(id__in=sample_ids)

        elif institution_search and chip_search:
            print(
                f"""
            {institution_search=}
            {chip_search=}
            """
            )
            institutions = Institution.objects.filter(
                name__icontains=institution_search
            )
            chips = Chip.objects.filter(chip_id__icontains=chip_search)
            sample_ids = ChipSample.objects.filter(
                sample__in=samples, chip__in=chips
            ).values_list("sample", flat=True)
            samples = Sample.objects.filter(id__in=sample_ids)

        elif institution_search and sample_search:
            print(
                f"""
            {institution_search=}
            {sample_search=}
            """
            )
            institutions = Institution.objects.filter(
                name__icontains=institution_search
            )

            samples = Sample.objects.filter(
                protocol_id__icontains=sample_search, institution__in=institutions
            )
            chip_ids = ChipSample.objects.filter(sample__in=samples).values_list("chip")
            chips = Chip.objects.filter(id__in=chip_ids)

        elif chip_search and sample_search:
            print(
                f"""
            {sample_search=}
            {chip_search=}
            """
            )
            pass

        elif institution_search:
            print(
                f"""
            {institution_search=}
            """
            )
            institutions = Institution.objects.filter(
                name__icontains=institution_search
            )
            samples = Sample.objects.filter(institution__in=institutions)
            chip_ids = ChipSample.objects.filter(sample__in=samples).values_list("chip")
            chips = Chip.objects.filter(id__in=chip_ids)

        elif chip_search:
            print(
                f"""
            {chip_search=}
            """
            )
            chips = Chip.objects.filter(chip_id__icontains=chip_search)
            chip_samples = ChipSample.objects.filter(chip__in=chips)
            sample_ids = chip_samples.values_list("sample", flat=True)
            samples = Sample.objects.filter(id__in=sample_ids)
            institution_ids = samples.values_list("institution", flat=True)
            institutions = Institution.objects.filter(id__in=institution_ids)

        elif sample_search:
            print(
                f"""
            {sample_search=}
            """
            )
            pass
        else:
            print(
                f"""
            Arama yok.
            """
            )
            # En son eklenenleri getir.
            pass

        tables = [
            InstitutionTable(institutions),
            ChipTable(chips),
            SampleTable(samples),
        ]
        return tables


class SampleView(TemplateView):
    template_name = "canvas/components/sample.html"

    def get(self, request, *args, **kwargs):
        sample_pk = request.GET.get("sample_pk")
        sample = Sample.objects.get(id=sample_pk)
        bedgraph_url= "http://192.168.1.102:9000/canvas/bedgraphs/{sample.p.bedgraph.gz" 
        context = {"sample": sample,
        "bedgraph_url": bedgraph_url}


        return render(request, self.template_name, context=context)


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

