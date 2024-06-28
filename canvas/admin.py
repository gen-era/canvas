from django.contrib import admin

# Register your models here.
from .models import Lot, Chip, SampleType, Institution, Sample

class ChipAdmin(admin.ModelAdmin):
    list_display = ["chip_id", "lot", "protocol_start_date", "scan_date"]
    search_fields = ["chip_id", "lot__lot_number"]


class SampleTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class SampleAdmin(admin.ModelAdmin):
    list_display = ('protocol_id', 'entry_date', 'arrival_date', 'study_date', 'chip', 'position', 'concentration', 'institution', 'call_rate')
    search_fields = ('protocol_id', 'chip__name', 'institution__name')

admin.site.register(Lot)
admin.site.register(Chip, ChipAdmin)
admin.site.register(SampleType, SampleTypeAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Sample, SampleAdmin)
