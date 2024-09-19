from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from django.apps import apps
from django_htmx.http import retarget
from django.db import transaction


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
    len_samples = len(samples)
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
            "len_samples": len_samples,
        },
    )


@login_required
def generic_search(request, model_name, field_name):
    query = request.GET.get("search", "").strip()
    page = request.GET.get("page")

    # Dynamically get the model class
    model = apps.get_model(app_label="canvas", model_name=model_name)

    if query:
        # Use the field_name dynamically
        filter_kwargs = {f"{field_name}__icontains": query}
        items = model.objects.filter(**filter_kwargs)
    else:
        items = model.objects.none()

    items = items.order_by(field_name)
    len_items = len(items)

    paginator = Paginator(items, 12)
    items = paginator.get_page(page)

    return render(
        request,
        "canvas/partials/search_results.html",
        {
            "items": items,
            "len_items": len_items,
            "query": query,
            "model_name": model_name,
            "field_name": field_name,
        },
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
    len_samples = len(samples)

    paginator = Paginator(samples, 12)
    samples = paginator.get_page(page)
    return render(
        request,
        "canvas/partials/sample_results.html",
        {"samples": samples, "query": query, "len_samples": len_samples},
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

    cnvs = []
    for cnv in chipsample.cnv.all():
        cnv_json = cnv.cnv_json
        cnv_json["addToReport"] = False
        cnvs.append(cnv_json)

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
            "cnvs": json.dumps(cnvs),
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


@login_required
def get_sample_input_row(request):
    label = secrets.token_urlsafe(6)
    return render(request, "canvas/partials/sample_input_row.html", {"label": label})


@login_required
def save_samples(request):
    form_data = dict(request.POST)
    print(form_data)  # For debugging

    form_invalid = False
    errors = []

    len_samples = len(form_data["protocol_id"])
    # Process each row of form data
    try:
        with transaction.atomic():
            for i in range(len(form_data["protocol_id"])):
                try:
                    institution = Institution.objects.get(
                        id=form_data["Institution"][i]
                    )
                    sample_type = SampleType.objects.get(id=form_data["SampleType"][i])

                    # Create new Sample object
                    sample = Sample.objects.create(
                        arrival_date=form_data["arrival_date"][i],
                        study_date=form_data["study_date"][i] or None,
                        protocol_id=form_data["protocol_id"][i],
                        concentration=form_data["concentration"][i],
                        institution=institution,
                        sex=form_data["sex"][i],
                        description=form_data["description"][i],
                        sample_type=sample_type,
                    )

                    # Handle ManyToManyField 'repeat'
                    repeat_sample_id = form_data["Sample"][i]
                    if repeat_sample_id:
                        try:
                            repeat_sample = Sample.objects.get(id=repeat_sample_id)
                            sample.repeat.add(repeat_sample)
                        except Sample.DoesNotExist:
                            errors.append(
                                f"Sample with ID {repeat_sample_id} not found."
                            )
                            form_invalid = True

                except Institution.DoesNotExist:
                    errors.append(
                        f"Institution with ID {form_data['Institution'][i]} not found."
                    )
                    form_invalid = True
                except SampleType.DoesNotExist:
                    errors.append(
                        f"SampleType with ID {form_data['SampleType'][i]} not found."
                    )
                    form_invalid = True

        # Check if the form is invalid after the loop
        if form_invalid:
            return render(
                request,
                "canvas/partials/sample_input_form_errors.html",
                {"errors": errors},
            )
        else:
            # If everything is successful, return success response
            response = render(
                request,
                "canvas/partials/sample_input_success.html",
                {"len_samples": len_samples},
            )
            return retarget(response, "#sample-input-form")

    except Exception as e:
        errors.append(str(e))
        return render(
            request,
            "canvas/partials/sample_input_form_errors.html",
            {"errors": errors},
        )


def create_report(request):
    form_data = dict(request.POST)
    print(form_data)
    return render(
        request,
        "canvas/partials/sample_input_form_errors.html",
    )


def get_reports(request):
    chipsample_pk = request.POST.get("chipsample_pk")
    button = request.POST.get("button")
    chipsample = ChipSample.objects.get(id=chipsample_pk)

    context = {
        "reports": [f"{chipsample}a", f"{chipsample}b", f"{chipsample}c"],
        "button": button,
        "chipsample": chipsample,
    }
    return render(request, "canvas/partials/report_list.html", context=context)


def get_chip_type_size(request):
    query = request.GET.get("chipType", "").strip()
    chip_type = ChipType.objects.get(name=query)

    # Generate the card positions based on the chip size
    num_rows=[f"{i:02d}" for i in range(1, chip_type.rows +1)]
    num_cols=[f"{i:02d}" for i in range(1, chip_type.cols + 1)]

    return render(
            request,
            "canvas/partials/chip_cards_template.html",
            {'num_rows': num_rows,
                'num_cols': num_cols,
                'chip_type':chip_type
             },
        )

from django.shortcuts import HttpResponse
def save_chip_input(request):

    print(request.POST)
    return HttpResponse("hi")
#     form_data = dict(request.POST)
#     print(form_data)
    
#     try:
#         with transaction.atomic():
#             for i in range(len(form_data["Sample"])):
#                 try:
#                     sample = Sample.objects.get(
#                         id=form_data["Sample"][i]
#                     )

#                     position = 

#                     # Create new Sample object
#                     sample = Sample.objects.create(
#                         arrival_date=form_data["arrival_date"][i],
#                         study_date=form_data["study_date"][i] or None,
#                         protocol_id=form_data["protocol_id"][i],
#                         concentration=form_data["concentration"][i],
#                         institution=institution,
#                         sex=form_data["sex"][i],
#                         description=form_data["description"][i],
#                         sample_type=sample_type,
#                     )

#                     # Handle ManyToManyField 'repeat'
#                     repeat_sample_id = form_data["Sample"][i]
#                     if repeat_sample_id:
#                         try:
#                             repeat_sample = Sample.objects.get(id=repeat_sample_id)
#                             sample.repeat.add(repeat_sample)
#                         except Sample.DoesNotExist:
#                             errors.append(
#                                 f"Sample with ID {repeat_sample_id} not found."
#                             )
#                             form_invalid = True

#                 except Institution.DoesNotExist:
#                     errors.append(
#                         f"Institution with ID {form_data['Institution'][i]} not found."
#                     )
#                     form_invalid = True
#                 except SampleType.DoesNotExist:
#                     errors.append(
#                         f"SampleType with ID {form_data['SampleType'][i]} not found."
#                     )
#                     form_invalid = True

#         # Check if the form is invalid after the loop
#         if form_invalid:
#             return render(
#                 request,
#                 "canvas/partials/sample_input_form_errors.html",
#                 {"errors": errors},
#             )
#         else:
#             # If everything is successful, return success response
#             response = render(
#                 request,
#                 "canvas/partials/sample_input_success.html",
#                 {"len_samples": len_samples},
#             )
#             return retarget(response, "#sample-input-form")

#     except Exception as e:
#         errors.append(str(e))
#         return render(
#             request,
#             "canvas/partials/sample_input_form_errors.html",
#             {"errors": errors},
#         )

from django.shortcuts import get_object_or_404

def idat_upload(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        uploaded_files = []
        errors = []

        for file in files:
            if file.name.endswith('.idat'):
                # Extract chip_id logic (from file or directory name)
                chip_id, position = file.name.split("_")[:2]

                # Get or create ChipSample instance using chip_id
                chipsample = ChipSample.objects.get(chip__chip_id=chip_id, position=position)

                try:
                    # Save the file in the IDAT model and link it to ChipSample
                    idat_file = IDAT.objects.create(
                        idat=file,
                        chipsample=chipsample
                    )
                    uploaded_files.append(idat_file)
                except Exception as e:
                    errors.append(f"Error uploading {file.name}: {str(e)}")
            else:
                errors.append(f"Invalid file type: {file.name}")

        # Render the uploaded files and error messages into HTML
        context = {
            'uploaded_files': uploaded_files,
            'errors': errors
        }
        return HttpResponse("hi")
        # return render(request, 'partials/upload_result.html', context)
