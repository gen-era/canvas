#!/usr/bin/env python3

# your_app/management/commands/load_chip_excel.py

import pandas as pd
from django.core.management.base import BaseCommand
from canvas.models import Lot, Chip, ChipType
from datetime import datetime

class Command(BaseCommand):
    help = 'Load chip data from Excel file into the database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')

    def handle(self, *args, **options):
        excel_file = options['file_path']
        try:
            df = pd.read_excel(excel_file)

            lot, _ = Lot.objects.get_or_create(lot_number=0, arrival_date=datetime.now())
            # Load ChipType data
            for index, row in df.iterrows():
                chip_type, _ = ChipType.objects.get_or_create(name=row['Çip Tipi'])

                entry_date = datetime.strptime(row['Tarih'], '%d.%m.%Y')

                Chip.objects.get_or_create(
                    chip_id=row['Çip Barkodu'],
                    chip_type=chip_type,
                    protocol_start_date=datetime.now(),
                    scan_date= datetime.now(),
                    lot=lot,
                    entry_date=entry_date
                )

            self.stdout.write(self.style.SUCCESS('Chip data loaded successfully!'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('File not found. Please provide the correct file path.'))
