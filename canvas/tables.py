import django_tables2 as tables
from canvas.models import Institution, Chip, Sample


class InstitutionTable(tables.Table):
    class Meta:
        model = Institution
        template_name = "canvas/bootstrap_htmx.html"


class ChipTable(tables.Table):
    class Meta:
        model = Chip
        template_name = "canvas/bootstrap_htmx.html"


class SampleTable(tables.Table):
    class Meta:
        model = Sample
        template_name = "canvas/bootstrap_htmx.html"
