import os
from django.core.management.base import BaseCommand
from canvas.models import ChipSample, BedGraph, IDAT, GTC, VCF

class Command(BaseCommand):
    help = "Associate files with ChipSample models"

    def add_arguments(self, parser):
        parser.add_argument('chip_id', type=str, help='The Chip ID to process')
        parser.add_argument('base_dir', type=str, help='Base directory for the media files')

    def handle(self, *args, **options):
        chip_id = options['chip_id']
        base_dir = options['base_dir']
        print(chip_id)

        # Example of how to handle BedGraph files
        bedgraph_dir = os.path.join(base_dir, chip_id, "bedgraphs")
        for filename in os.listdir(bedgraph_dir):
            # Parse the filename to get the chip position and bedgraph type
            parts = filename.split(".")
            print(filename)
            print(parts)
            if len(parts) == 4:  # Ensure it's a correctly formatted filename
                chip_position = parts[0].split("_")[1]
                bedgraph_type = parts[1].upper()
                print(chip_position)

                try:
                    chipsample = ChipSample.objects.get(
                        chip__chip_id=chip_id, position=chip_position
                    )
                    print(chipsample)
                except ChipSample.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"ChipSample not found for {filename}"))
                    continue

                BedGraph.objects.create(
                    chipsample=chipsample,
                    bedgraph_type=bedgraph_type,
                    bedgraph=os.path.join(f"{chip_id}/bedgraphs", filename),
                )
                self.stdout.write(self.style.SUCCESS(f"Saved {filename} to {chipsample}"))

        # # Repeat for IDAT, GTC, VCF, etc.
        # # Example for IDAT
        # idat_dir = os.path.join(base_dir, chip_id, "idats")
        # for filename in os.listdir(idat_dir):
        #     # Implement similar logic to associate IDAT files
        #
        # # Example for GTC
        # gtc_dir = os.path.join(base_dir, chip_id, "gtcs")
        # for filename in os.listdir(gtc_dir):
        #     # Implement similar logic to associate GTC files
        #
        # # Example for VCF
        # vcf_dir = os.path.join(base_dir, chip_id, "vcfs")
        # for filename in os.listdir(vcf_dir):
        #     # Implement similar logic to associate VCF files
