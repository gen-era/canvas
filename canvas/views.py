import json
import os
import secrets
import socket
import struct
import subprocess
import tempfile
from datetime import timedelta
from http.client import HTTPResponse

import minio
from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import HttpResponse, render
from django.utils import timezone
from django_htmx.http import retarget

from canvas.models import (
    IDAT,
    Chip,
    ChipSample,
    ChipType,
    Institution,
    Lot,
    Sample,
    SampleType,
)


def get_default_gateway_linux():
    """Read the default gateway directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != "00000000" or not int(fields[3], 16) & 2:
                # If not default route or not RTF_GATEWAY, skip it
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


def get_version():
    with open(settings.BASE_DIR.joinpath(".git/ORIG_HEAD")) as f:
        return f.read().splitlines()[0][:6]


def start_run(chip_id):
    if not settings.DEBUG:
        HOST_IP = get_default_gateway_linux()
        MINIO_IP = socket.gethostbyname("minio")
        label = secrets.token_urlsafe(6)

        with tempfile.NamedTemporaryFile(delete_on_close=False, mode="w") as fp:
            fp.write(
                f"""
                aws {{
                access_key = "{settings.MINIO_STORAGE_ACCESS_KEY}"
                secret_key = "{settings.MINIO_STORAGE_SECRET_KEY}"
                client {{
                    endpoint = "http://{MINIO_IP}:9000"
                }}
                }}
                profiles {{
                docker {{
                    docker.enabled = true
                }}
                }}
                """
            )
            fp.close()
            subprocess.run(
                f"scp {fp.name} canvas@{HOST_IP}:/tmp/",
                shell=True,
            )

        subprocess.run(
            f"ssh canvas@{HOST_IP} tsp -L {label} nextflow /home/canvas/canvas-pipeline/main.nf \
                                                --chip_id {chip_id} \
                                                --bpm analysis_files/manifest-cluster/GSACyto_20044998_A1.bpm \
                                                --csv analysis_files/manifest-cluster/GSACyto_20044998_A1.csv \
                                                --egt analysis_files/manifest-cluster/2003.egt \
                                                --fasta analysis_files/GRCh37_genome.fa \
                                                --pfb analysis_files/PennCNV/test/out.pfb \
                                                --band canvas-pipeline/hg19_chrom_band.txt \
                                                --tex_template canvas-pipeline/template/base_template.tex \
                                                --output_dir canvas-pipeline-demo-results/ \
                                                -c {fp.name} \
                                                -profile docker",
            shell=True,
        )


def index(request):

    samples = Sample.objects.order_by("-entry_date")
    len_samples = len(samples)
    sample_paginator = Paginator(samples, 12)
    samples = sample_paginator.get_page(1)

    chips = Chip.objects.order_by("-entry_date")
    len_chips = len(chips)
    chip_paginator = Paginator(chips, 12)
    chips = chip_paginator.get_page(1)

    label = secrets.token_urlsafe(6)
    return render(
        request,
        "canvas/index.html",
        {
            "title": "Index",
            "label": label,
            "samples": samples,
            "len_samples": len_samples,
            "chips": chips,
            "len_chips": len_chips,
            "canvas_version": get_version(),
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
def chip_search(request):
    query = request.GET.get("search", "").strip()
    page = request.GET.get("page")

    chips = Chip.objects.filter(chip_id__contains=query)

    chips = chips.order_by("-entry_date")
    len_chips = len(chips)

    paginator = Paginator(chips, 12)
    chips = paginator.get_page(page)

    return render(
        request,
        "canvas/partials/chips.html",
        {"chips": chips, "query": query, "len_chips": len_chips},
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
def chip_edit(request):
    if request.method == "GET":
        chip_pk = request.GET.get("chip_pk")
        chip = Chip.objects.get(id=chip_pk)
        return render(
            request, "canvas/partials/chip_edit.html", {"chip": chip}
        )  # For debugging

    if request.method == "POST":
        chip_pk = request.POST.get("chip_pk")
        chip = Chip.objects.filter(id=chip_pk).first()

        edit = request.POST.get("edit", None)
        if edit == "false":
            return render(
                request, "canvas/partials/chip.html", {"chip": chip}
            )  # For debugging

        positions = request.POST.getlist("position")
        samples = request.POST.getlist("Sample")

        for position, sample_pk in zip(positions, samples):
            if sample_pk.strip():
                sample = Sample.objects.get(pk=int(sample_pk))

                chipsample = ChipSample.objects.filter(
                    chip=chip, position=position
                ).first()
                if chipsample:
                    chipsample.sample = sample
                    chipsample.save()
                else:
                    ChipSample.objects.create(
                        chip=chip, position=position, sample=sample
                    )

        if not chipsample.call_rate:
            start_run(chip.chip_id)
        return render(request, "canvas/partials/chip.html", {"chip": chip})


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
                "canvas/partials/sample_results.html",
                {"errors": errors},
            )
        else:
            # If everything is successful, return success response
            response = render(
                request,
                "canvas/partials/sample_input_results.html",
                {"len_samples": len_samples},
            )
            return retarget(response, "#sample-input-form")

    except Exception as e:
        errors.append(str(e))
        return render(
            request,
            "canvas/partials/sample_input_results.html",
            {"errors": errors},
        )


def create_report(request):
    form_data = dict(request.POST)
    print(form_data)
    return HTTPResponse("hi")


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


def idat_upload(request):
    if request.method == "POST":
        files = request.FILES.getlist("files")
        uploaded_files = []
        errors = []

        chip_type_pk = request.POST.get("ChipType")
        chip_type = ChipType.objects.get(pk=int(chip_type_pk[0]))

        for file in files:
            if file.name.endswith(".idat"):
                try:
                    chip_id, position = file.name.split("_")[:2]
                    chip, created = Chip.objects.get_or_create(
                        chip_id=chip_id,
                        defaults={
                            "chip_type": chip_type,
                            "lab_practitioner": request.user,
                            "protocol_start_date": timezone.now(),
                            "scan_date": timezone.now(),
                        },
                    )
                    chipsample, created = ChipSample.objects.get_or_create(
                        chip=chip, position=position
                    )
                    idat_file = IDAT.objects.create(idat=file, chipsample=chipsample)
                    uploaded_files.append(idat_file)
                except Exception as e:
                    errors.append(f"Error uploading {file.name}: {str(e)}")
            else:
                errors.append(f"Invalid file type: {file.name}")

        # Render the uploaded files and error messages into HTML
        context = {"uploaded_files": uploaded_files, "errors": errors}
        return render(request, "canvas/partials/idat_upload_results.html", context)
    
from .read_sample_from_excel import generate_data_list
def upload_excel(request):
    excel_file = request.FILES.get('excel_file')
    sample_list = generate_data_list(excel_file)
    context = {"sample_list":sample_list}
    print(context)
    return render(request, 'canvas/partials/samples_from_excel.html', context)