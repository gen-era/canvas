from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError

from django.db import models
from taggit.managers import TaggableManager
from django.contrib.auth.models import User, Group


# Create your models here.


class Lot(models.Model):
    lot_number = models.CharField(max_length=200)
    entry_date = models.DateTimeField(auto_now_add=True)
    arrival_date = models.DateTimeField("Entry date")

    def __str__(self):
        return self.lot_number


class ChipType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Chip(models.Model):
    lab_practitioner = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True
    )
    chip_id = models.CharField(max_length=200)
    chip_type = models.ForeignKey(ChipType, on_delete=models.PROTECT)
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now_add=True)
    protocol_start_date = models.DateTimeField("Start date")
    scan_date = models.DateTimeField("Scan date")

    def __str__(self):
        return self.chip_id


class SampleType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Institution(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="institutions"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Check if a group with the same name exists
        group, created = Group.objects.get_or_create(name=self.name)
        # Assign the group to the institution
        self.group = group
        super().save(*args, **kwargs)


class Sample(models.Model):
    entry_date = models.DateTimeField(
        auto_now_add=True
    )  # Change to DateTimeField with auto_now_add=True
    arrival_date = models.DateField()
    study_date = models.DateField(null=True)
    protocol_id = models.CharField(max_length=100)
    concentration = models.DecimalField(max_digits=5, decimal_places=1)
    institution = models.ForeignKey(
        Institution, on_delete=models.PROTECT, related_name="sample"
    )
    data_info = TaggableManager()
    description = models.CharField(max_length=255, null=True)
    sample_type = models.ForeignKey(SampleType, on_delete=models.PROTECT)
    repeat = models.ManyToManyField("self")

    def __str__(self):
        return f"{self.protocol_id} - {self.arrival_date}"

    @property
    def chipsample(self):
        return ChipSample.objects.get(sample=self)


class ChipSample(models.Model):
    sample = models.ForeignKey(
        Sample, on_delete=models.PROTECT, related_name="chipsample"
    )

    call_rate = models.DecimalField(max_digits=10, decimal_places=7)
    chip = models.ForeignKey(
        Chip, on_delete=models.PROTECT, null=True, blank=True, related_name="chipsample"
    )
    position = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^R\d{2}C\d{2}$",
                message="Position should follow this structure: R01C01",
                code="invalid_position",
            ),
        ],
    )

    def __str__(self):
        return f"{self.sample.protocol_id} - {self.chip.scan_date}"


class IDAT(models.Model):
    entry_date = models.DateTimeField(
        auto_now_add=True
    )  # Change to DateTimeField with auto_now_add=True
    idat = models.FileField(
        upload_to="idats/",
        validators=[FileExtensionValidator(allowed_extensions=["idat"])],
    )
    chipsample = models.ForeignKey(
        ChipSample, on_delete=models.PROTECT, null=True, blank=True
    )


class GTC(models.Model):
    entry_date = models.DateTimeField(
        auto_now_add=True
    )  # Change to DateTimeField with auto_now_add=True
    gtc = models.FileField(
        upload_to="gtcs/",
        validators=[FileExtensionValidator(allowed_extensions=["gtc"])],
    )
    chipsample = models.ForeignKey(ChipSample, on_delete=models.PROTECT)


class VCF(models.Model):
    chipsample = models.ForeignKey(
        ChipSample, on_delete=models.PROTECT, null=True, blank=True
    )
    entry_date = models.DateTimeField(
        auto_now_add=True
    )  # Change to DateTimeField with auto_now_add=True
    vcf = models.FileField(
        upload_to="vcfs/",
        validators=[FileExtensionValidator(allowed_extensions=["vcf.gz"])],
    )


class BedGraph(models.Model):
    bedgraph_types = [("LRR", "Log R Ratio"), ("BAF", "B Allele Frequency")]
    chipsample = models.ForeignKey(
        ChipSample,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bedgraph",
    )
    entry_date = models.DateTimeField(
        auto_now_add=True
    )  # Change to DateTimeField with auto_now_add=True
    bedgraph_type = models.CharField(max_length=50, choices=bedgraph_types)
    bedgraph = models.FileField(
        upload_to="bedGraphs/",
        validators=[FileExtensionValidator(allowed_extensions=["bedgraph.gz"])],
    )


class SampleSheet(models.Model):
    entry_date = models.DateTimeField(
        auto_now_add=True
    )  # Change to DateTimeField with auto_now_add=True
    chip = models.ForeignKey(
        Chip,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="samplesheet",
    )
    samplesheet = models.FileField(
        upload_to="samplesheets/",
        validators=[FileExtensionValidator(allowed_extensions=["tsv"])],
    )
