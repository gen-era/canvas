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


from django_tables2 import MultiTableMixin
from .tables import InstitutionTable, ChipTable, SampleTable


class Search(MultiTableMixin, View):
    table_pagination = {
        "per_page": 5
    }

    # def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        print(f"{context=}")
        print(f"{request.GET=}")
        institution_query = request.GET.get("instituion_search", None)
        chip_query = request.GET.get("chip_search", None)
        sample_query = request.GET.get("sample_search", None)


        tables = [
            InstitutionTable(
                institution_filter(
                Institution.objects.all()
                )
            ),
            ChipTable(
                chip_filter(
                Chip.objects.all())
                )
            ,
            SampleTable(
                sample_filter(
                Sample.objects.all()
                )
            ),
        ]

        context = {
            'tables': self.tables,
        }
        return render(request, self.get_template_names(), context)


    def get_template_names(self):
        if self.request.htmx:
            template_name = "canvas/components/search_results.html"
        else:
            template_name = "canvas/components/search.html"

        return template_name




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
