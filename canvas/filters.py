# products/filters.py
from decimal import Decimal
from django.db.models import Q
import django_filters
from .models import Institution, Chip, Sample, ChipSample


class InstitutionFilter(django_filters.FilterSet):

    class Meta:
        model = Institution
        fields = ['name']


class ChipFilter(django_filters.FilterSet):

    class Meta:
        model = Chip
        fields = ['chip_id']


class SampleFilter(django_filters.FilterSet):

    class Meta:
        model = Sample
        fields = ['protocol_id'] #, 'chipsample.first.position']
