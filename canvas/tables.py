import django_tables2 as tables
from canvas.models import Institution, Chip, Sample

class InstitutionHTMxTable(tables.Table):
    class Meta:
        model = Institution
        template_name = "canvas/bootstrap_htmx.html"

class ChipHTMxTable(tables.Table):
    class Meta:
        model = Chip
        template_name = "canvas/bootstrap_htmx.html"

class SampleHTMxTable(tables.Table):
    class Meta:
        model = Sample
        template_name = "canvas/bootstrap_htmx.html"