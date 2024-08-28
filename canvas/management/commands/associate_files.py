from pathlib import Path
from collections import defaultdict
from django.core.management.base import BaseCommand
from canvas.models import ChipSample, BedGraph, IDAT, GTC, VCF

class Command(BaseCommand):
    help = "Associate files with ChipSample models"

    def add_arguments(self, parser):
        parser.add_argument('chip_id', type=str, help='The Chip ID to process')
        parser.add_argument('base_dir', type=str, help='Base directory for the media files')

    def handle(self, *args, **options):
        chip_id = options['chip_id']
        base_dir = Path(options['base_dir'])
        results = base_dir.joinpath(chip_id)

        def gather_scoresheets():
            '''
            returns:
            {
            "R03C02": "path to the scoresheet",
            }

            '''
            return {
                i.stem.split("_")[1]: i.joinpath("Scoresheet.txt")
                for i in results.joinpath("ClassifyCNV").iterdir()
            }

        def gather_cnvs():
            '''
            returns:
            {
            "R03C02": "path to the cnvs",
            }

            '''

            iscns = []
            for i in results.joinpath("cnvs").iterdir():
                if "iscn" in i.as_posix():
                    iscns.append(i)
            return {
                i.stem.split("_")[1]: i for i in iscns
            }
                    
        print(gather_scoresheets())
        print(gather_cnvs())


            # try:
            #     chipsample = ChipSample.objects.get(
            #         chip__chip_id=chip_id, position=position
            #     )
            # except ChipSample.DoesNotExist:
            #     self.stdout.write(self.style.ERROR(f"ChipSample not found for position {position}"))
            #     continue
            #
            # # Save BedGraph files
            # for filename in files['bedgraphs']:
            #     bedgraph_type = filename.split(".")[1].upper()
            #     BedGraph.objects.create(
            #         chipsample=chipsample,
            #         bedgraph_type=bedgraph_type,
            #         bedgraph=os.path.join("bedGraphs", filename),
            #     )
            #     self.stdout.write(self.style.SUCCESS(f"Saved BedGraph {filename} to {chipsample}"))

            # Save IDAT files
            # for filename in files['idats']:
            #     IDAT.objects.create(
            #         chipsample=chipsample,
            #         idat=os.path.join("idats", filename),
            #     )
            #     self.stdout.write(self.style.SUCCESS(f"Saved IDAT {filename} to {chipsample}"))

            # Save GTC files
            # for filename in files['gtcs']:
            #     GTC.objects.create(
            #         chipsample=chipsample,
            #         gtc=os.path.join("gtcs", filename),
            #     )
            #     self.stdout.write(self.style.SUCCESS(f"Saved GTC {filename} to {chipsample}"))
            #
            # # Save VCF files
            # for filename in files['vcfs']:
            #     VCF.objects.create(
            #         chipsample=chipsample,
            #         vcf=os.path.join("vcfs", filename),
            #     )
            #     self.stdout.write(self.style.SUCCESS(f"Saved VCF {filename} to {chipsample}"))
