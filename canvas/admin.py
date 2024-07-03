from django.contrib import admin

# Register your models here.
from .models import Lot, Chip, ChipType, SampleType, Institution, Sample, SampleChip


class ChipAdmin(admin.ModelAdmin):
    list_display = ["chip_id", "lot", "protocol_start_date", "scan_date"]
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


class SampleChipAdmin(admin.ModelAdmin):
    list_display = (
        "get_protocol_id",
        "chip",
        "position",
        "call_rate",
    )
    search_fields = ("protocol_id", "chip__name", "institution__name")

    def get_protocol_id(self, obj):
        return obj.sample.protocol_id


admin.site.register(Lot)
admin.site.register(Chip, ChipAdmin)
admin.site.register(ChipType, ChipTypeAdmin)
admin.site.register(SampleType, SampleTypeAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Sample, SampleAdmin)
admin.site.register(SampleChip, SampleChipAdmin)
