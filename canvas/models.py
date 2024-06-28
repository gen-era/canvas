from django.core.validators import RegexValidator
from django.db import models
from taggit.managers import TaggableManager



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
    chip_id = models.CharField(max_length=200)
    chip_type = models.ForeignKey(ChipType, on_delete=models.PROTECT)
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now_add=True)
    protocol_start_date = models.DateTimeField("Entry date")
    scan_date = models.DateTimeField("Entry date")


class SampleType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Institution(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

def validate_position(value):
    pattern = r'^R\d{2}C\d{2}$'  # Regex pattern for R01C01, R02C01, R03C01, etc.
    if not bool(re.match(pattern, value)):
        raise ValidationError('Position must follow the format R01C01, R02C01, R03C01, etc.')

class Sample(models.Model):
    entry_date = models.DateTimeField(auto_now_add=True)  # Change to DateTimeField with auto_now_add=True
    arrival_date = models.DateField()
    study_date = models.DateField()
    chip = models.ForeignKey(Chip, on_delete=models.PROTECT, null=True, blank=True)
    position = models.CharField(max_length=10, validators=[validate_position])
    protocol_id = models.CharField(max_length=100)
    concentration = models.DecimalField(max_digits=5, decimal_places=1)
    institution = models.ForeignKey(Institution, on_delete=models.PROTECT)
    call_rate = models.DecimalField(max_digits=10, decimal_places=7)
    data_info = TaggableManager()
    description = models.CharField(max_length=255)
    sample_type = models.ForeignKey(SampleType, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.protocol_id} - {self.date}"
