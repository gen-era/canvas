import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor

from canvas.models import Institution, Chip, Sample


class InstitutionTable(tables.Table):
    class Meta:
        model = Institution
        template_name = "canvas/table_base.html"
        fields = ("name",)


class ChipTable(tables.Table):
    class Meta:
        model = Chip
        template_name = "canvas/table_base.html"
        fields = (
            "chip_id",
            "chip_type",
        )


class SampleTable(tables.Table):

    protocol_id = tables.TemplateColumn(
        template_name="canvas/sample_protocol_id_column.html"
    )

    chipsample = tables.TemplateColumn(template_name="canvas/chipsample_column.html")
    chip = tables.Column(accessor="chipsample.first.chip.chip_id")
    position = tables.Column(accessor="chipsample.first.position")

    class Meta:
        model = Sample
        template_name = "canvas/table_base.html"
        fields = ("protocol_id", "chipsample", "sample_type", "institution")
