import django_tables2 as tables
from canvas.models import Institution, Chip, Sample


class InstitutionTable(tables.Table):
    class Meta:
        model = Institution
        template_name = "canvas/bootstrap_htmx.html"
        fields = ("name", )



class ChipTable(tables.Table):
    class Meta:
        model = Chip
        template_name = "canvas/bootstrap_htmx.html"
        fields = ("chip_id", "chip_type",)


class SampleTable(tables.Table):
    chip = tables.Column(accessor = 'chipsample.first.chip.chip_id')
    position = tables.Column(accessor = 'chipsample.first.position')

    class Meta:
        model = Sample
        template_name = "canvas/bootstrap_htmx.html"
        fields = ("protocol_id", "chip", "position", "sample_type", "institution")
