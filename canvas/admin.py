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
    BedGraph
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
    search_fields = ("protocol_id", "institution__name")


class ChipSampleAdmin(admin.ModelAdmin):
    list_display = (
        "protocol_id",
        "chip",
        "position",
        "call_rate",
    )
    search_fields = ("protocol_id", "chip__name", "institution__name")

    def protocol_id(self, obj):
        return obj.sample.protocol_id


class IDATAdmin(admin.ModelAdmin):
    list_display = ["idat", "protocol_id"]
    search_fields = ["idat", "protocol_id"]

    def protocol_id(self, obj):
        if obj.chip_sample:
            return obj.chip_sample.sample.protocol_id
        else:
            return "none"


class GTCAdmin(admin.ModelAdmin):
    list_display = ["gtc", "protocol_id"]
    search_fields = ["gtc", "protocol_id"]

    def protocol_id(self, obj):
        return obj.chip_sample.sample.protocol_id

class VCFAdmin(admin.ModelAdmin):
    list_display = ["vcf", "protocol_id"]
    search_fields = ["vcf", "protocol_id"]

    def protocol_id(self, obj):
        return obj.chip_sample.sample.protocol_id
    
class BedGraphAdmin(admin.ModelAdmin):
    list_display = ["chip_sample", "bedgraph", "bedgraph_type", "protocol_id"]
    search_fields = ["bedgraph", "protocol_id"]

    def protocol_id(self, obj):
        try:
            return obj.chip_sample.sample.protocol_id
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
admin.site.register(BedGraph,BedGraphAdmin)
