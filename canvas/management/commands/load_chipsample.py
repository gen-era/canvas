import pandas as pd
from django.core.management.base import BaseCommand
from canvas.models import (
    Chip,
    ChipType,
    Sample,
    SampleType,
    Institution,
    ChipSample,
    Lot,
)
from django.utils.dateparse import parse_date
from django.core.exceptions import ValidationError
import re
from datetime import datetime


class Command(BaseCommand):
    help = "Import data from an Excel file into the database"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="The path to the Excel file")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        sheet_name = "Aktif Örnekler"

        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error reading the Excel file: {e}"))
            return

        default_date = datetime.strptime("1.1.2000", "%d.%m.%Y").date()

        for index, row in df.iterrows():
            try:
                # Convert the decimal values from strings with commas to proper decimal format
                concentration = row["Kons."]
                if isinstance(concentration, str):
                    concentration = concentration.replace(",", ".")
                if pd.isna(concentration):
                    self.stderr.write(
                        self.style.ERROR(
                            f"NaN value for concentration at row {index + 1}. Skipping row."
                        )
                    )
                    continue
                concentration = float(concentration)

                call_rate = row["Call_Rate"]
                if isinstance(call_rate, str):
                    call_rate = call_rate.replace(",", ".")
                if pd.isna(call_rate):
                    self.stderr.write(
                        self.style.ERROR(
                            f"NaN value for call rate at row {index + 1}. Skipping row."
                        )
                    )
                    continue
                call_rate = float(call_rate)

                # Ensure arrival_date is not null
                try:
                    arrival_date = datetime.strptime(row["Tarih"], "%d.%m.%Y").date()
                except ValueError:
                    arrival_date = default_date
                    self.stderr.write(
                        self.style.WARNING(
                            f"Invalid arrival date at row {index + 1}. Replacing with default date."
                        )
                    )

                chip_type, _ = ChipType.objects.get_or_create(name=row["Çip"])
                institution, _ = Institution.objects.get_or_create(name=row["Kurum"])
                sample_type, _ = SampleType.objects.get_or_create(
                    name="Default"
                )  # Adjust as needed

                # Create or get a Lot with a valid arrival_date
                lot, _ = Lot.objects.get_or_create(
                    lot_number=row["Barkod"],
                    defaults={
                        "arrival_date": arrival_date,
                    },
                )

                chip, _ = Chip.objects.get_or_create(
                    chip_id=row["Barkod"],
                    defaults={
                        "chip_type": chip_type,
                        "lab_practitioner": None,  # Adjust if you have lab practitioners data
                        "lot": lot,  # Use the created or retrieved lot
                        "protocol_start_date": arrival_date,
                        "scan_date": arrival_date,
                    },
                )

                sample, created = Sample.objects.get_or_create(
                    protocol_id=row["Örnek"],
                    defaults={
                        "arrival_date": arrival_date,
                        "study_date": arrival_date,
                        "concentration": concentration,
                        "institution": institution,
                        "description": row["Açıklama"],
                        "sample_type": sample_type,
                    },
                )

                sample_chip, _ = ChipSample.objects.get_or_create(
                    sample=sample,
                    chip=chip,
                    position=row["Pozisyon"],
                    defaults={
                        "call_rate": call_rate,
                    },
                )

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully processed row {index + 1}")
                )

            except ValidationError as ve:
                self.stderr.write(
                    self.style.ERROR(f"Validation error: {ve} at row {index + 1}")
                )
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Error processing row {index + 1}: {e}")
                )

        self.stdout.write(self.style.SUCCESS("Data import complete"))
