from django.contrib import admin

# Register your models here.
from .models import (
    Lot,
    Chip,
    ChipType,
    SampleType,
    Institution,
    Sample,
    ChipSample,
    IDAT,
    GTC,
    VCF,
    BedGraph,
    CNV,
)


class ChipAdmin(admin.ModelAdmin):
    list_display = ["chip_id", "lot", "entry_date", "protocol_start_date", "scan_date"]
    search_fields = ["chip_id", "lot__lot_number"]


class ChipTypeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


class SampleTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class SampleAdmin(admin.ModelAdmin):
    list_display = (
        "protocol_id",
        "entry_date",
        "arrival_date",
        "study_date",
        "concentration",
        "institution",
        "sample_type",
        "description",
    )
    autocomplete_fields = ["repeat"]
    search_fields = ("protocol_id", "institution__name")


class ChipSampleAdmin(admin.ModelAdmin):
    list_display = (
        "protocol_id",
        "chip",
        "position",
        "call_rate",
    )
    search_fields = (
        "sample__protocol_id",
        "chip__chip_id",
        "sample__institution__name",
    )

    def protocol_id(self, obj):
        return obj.sample.protocol_id


class IDATAdmin(admin.ModelAdmin):
    list_display = ["idat", "protocol_id"]
    search_fields = ["idat", "protocol_id"]

    def protocol_id(self, obj):
        if obj.chipsample:
            return obj.chipsample.sample.protocol_id
        else:
            return "none"


class GTCAdmin(admin.ModelAdmin):
    list_display = ["gtc", "protocol_id"]
    search_fields = ["gtc", "protocol_id"]

    def protocol_id(self, obj):
        return obj.chipsample.sample.protocol_id


class VCFAdmin(admin.ModelAdmin):
    list_display = ["vcf", "protocol_id"]
    search_fields = ["vcf", "protocol_id"]

    def protocol_id(self, obj):
        return obj.chipsample.sample.protocol_id


class BedGraphAdmin(admin.ModelAdmin):
    list_display = ["chipsample", "bedgraph", "bedgraph_type", "protocol_id"]
    search_fields = ["bedgraph", "protocol_id"]

    autocomplete_fields = ["chipsample"]

    def protocol_id(self, obj):
        try:
            return obj.chipsample.sample.protocol_id
        except:
            return "abc"


class CNVAdmin(admin.ModelAdmin):
    list_display = ["variant_id", "entry_date"]
    search_fields = ["variant_id", "cnv_json"]

    autocomplete_fields = ["chipsample"]

    def protocol_id(self, obj):
        try:
            return obj.chipsample.sample.protocol_id
        except:
            return "abc"


admin.site.register(Lot)
admin.site.register(Chip, ChipAdmin)
admin.site.register(ChipType, ChipTypeAdmin)
admin.site.register(SampleType, SampleTypeAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Sample, SampleAdmin)
admin.site.register(ChipSample, ChipSampleAdmin)
admin.site.register(IDAT, IDATAdmin)
admin.site.register(GTC, GTCAdmin)
admin.site.register(VCF, VCFAdmin)
admin.site.register(BedGraph, BedGraphAdmin)
admin.site.register(CNV, CNVAdmin)
