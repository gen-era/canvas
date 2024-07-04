import pandas as pd
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from canvas.models import Sample, Institution, SampleType
from django.core.exceptions import ValidationError
from datetime import datetime

class Command(BaseCommand):
    help = 'Import samples from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the Excel file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        data = pd.read_excel(file_path)

        for index, row in data.iterrows():
            institution_name = row['Kurum Adı']
            sample_type_name = row['Numune Tipi']
            protocol_id = row['Lab No']
            arrival_date_str = str(row['Geliş Tarihi']).strip()
            study_date_str = str(row['Çalışma Tarihi']).strip()
            description = row['Açıklama'] if pd.notna(row['Açıklama']) else ''
            concentration_str = str(row['Kons']).strip() if pd.notna(row['Kons']) else '0'

            # Parse dates
            try:
                arrival_date = parse_date(arrival_date_str)
            except ValueError:
                arrival_date = None

            try:
                study_date = parse_date(study_date_str)
            except ValueError:
                study_date = None

            # Handle invalid dates
            if not arrival_date:
                # Set default date 0001-01-01 if arrival_date is missing
                arrival_date = datetime(1, 1, 1).date()

            if not study_date:
                # If it's not a valid date, add it to the description
                if study_date_str and study_date_str != 'nan':
                    if description:
                        description += f" / {study_date_str}"
                    else:
                        description = study_date_str

            # Validate and convert concentration
            try:
                concentration = float(concentration_str)
            except ValueError:
                concentration = 0.0

            institution, _ = Institution.objects.get_or_create(name=institution_name)
            sample_type, _ = SampleType.objects.get_or_create(name=sample_type_name)
            
            sample, created = Sample.objects.get_or_create(
                protocol_id=protocol_id,
                defaults={
                    'arrival_date': arrival_date,
                    'study_date': study_date,
                    'description': description,
                    'institution': institution,
                    'sample_type': sample_type,
                    'concentration': concentration,
                }
            )

            if not created:
                sample.arrival_date = arrival_date
                sample.study_date = study_date
                sample.description = description
                sample.institution = institution
                sample.sample_type = sample_type
                sample.concentration = concentration
                try:
                    sample.save()
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f'Error saving sample {protocol_id}: {e}'))

        self.stdout.write(self.style.SUCCESS('Successfully imported samples from Excel'))

