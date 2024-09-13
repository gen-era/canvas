from pathlib import Path
from collections import defaultdict
from django.core.management.base import BaseCommand
from canvas.models import ChipSample, BedGraph, IDAT, GTC, VCF, CNV
import csv


class Command(BaseCommand):
    help = "Associate files with ChipSample models"

    def add_arguments(self, parser):
        parser.add_argument("chip_id", type=str, help="The Chip ID to process")
        parser.add_argument(
            "base_dir", type=str, help="Base directory for the media files"
        )

    def handle(self, *args, **options):
        chip_id = options["chip_id"]
        base_dir = Path(options["base_dir"])
        results = base_dir.joinpath(chip_id)

        def gather_scoresheets():
            """
            returns:
            {
            "R03C02": "path to the scoresheet",
            }

            """
            return {
                i.stem.split("_")[1]: i.joinpath("Scoresheet.txt")
                for i in results.joinpath("ClassifyCNV").iterdir()
            }

        def gather_cnvs():
            """
            returns:
            {
            "R03C02": "path to the cnvs",
            }

            """

            iscns = []
            for i in results.joinpath("cnvs").iterdir():
                if "iscn" in i.as_posix():
                    iscns.append(i)
            return {i.stem.split("_")[1]: i for i in iscns}

        def gather_bedgraphs():
            """
            returns:
            {
            "R03C02": "path to the cnvs",
            }

            """

            bedgraphs = []
            for i in results.joinpath("bedgraphs").iterdir():
                bedgraphs.append(i)
            return {i.stem.split("_")[1].split(".")[0]: i for i in bedgraphs}

        # Function to process CNV file
        def process_cnv_file(file_path):
            cnv_data = {}
            with open(file_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    (
                        chr_info,
                        numsnp_info,
                        length_info,
                        state_info,
                        file_info,
                        startsnp_info,
                        endsnp_info,
                        conf,
                        iscn,
                    ) = parts
                    region = chr_info.split(":")
                    chr_start_end = f"{region[0]}_{region[1].split('-')[0]}_{region[1].split('-')[1]}"
                    cnv = {
                        "iscn": iscn,
                        "chr_info": chr_info,
                        "numsnp_info": numsnp_info,
                        "length_info": length_info,
                        "state_info": state_info,
                        "file_info": file_info,
                        "startsnp_info": startsnp_info,
                        "endsnp_info": endsnp_info,
                        "conf": conf,
                    }
                    cnv_data[chr_start_end] = cnv
            return cnv_data

        # Function to process Scoresheet file
        def process_scoresheet_file(file_path):
            scoresheet_data = {}
            with open(file_path, "r") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    variant_id = row["VariantID"]
                    # Remove _DEL and _DUP from VariantID
                    clean_variant_id = variant_id.replace("_DEL", "").replace(
                        "_DUP", ""
                    )
                    scoresheet_data[clean_variant_id] = dict(row)
            return scoresheet_data

        scoresheet_files = gather_scoresheets()
        cnv_files = gather_cnvs()

        for position, scoresheet_file in scoresheet_files.items():

            cnv_data = process_cnv_file(cnv_files[position])
            scoresheet_data = process_scoresheet_file(scoresheet_file)

            cnvs = {}
            for variant_id, cnv_dict in cnv_data.items():
                score_dict = scoresheet_data.get(variant_id, {})
                merged_dict = {**cnv_dict, **score_dict}
                cnvs[variant_id] = merged_dict

            try:
                chipsample = ChipSample.objects.get(
                    chip__chip_id=chip_id, position=position
                )
            except ChipSample.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"ChipSample not found for {chip_id} position {position}"
                    )
                )
                continue

            for variant_id, cnv in cnvs.items():
                cnv, created = CNV.objects.get_or_create(
                    variant_id=variant_id, cnv_json=cnv, chipsample=chipsample
                )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Saved CNV {variant_id} to {chipsample}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"CNV {variant_id} for {chipsample} already exists."
                    )
                )

        bedgraphs = gather_bedgraphs()
        for position, bedgraph in bedgraphs.items():

            try:
                chipsample = ChipSample.objects.get(
                    chip__chip_id=chip_id, position=position
                )
            except ChipSample.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"ChipSample not found for position {position}")
                )
                continue

            bedgraph_type = bedgraph.stem.split(".")[1].upper()
            bg, created = BedGraph.objects.get_or_create(
                chipsample=chipsample,
                bedgraph_type=bedgraph_type,
                bedgraph=bedgraph.relative_to("media").as_posix(),
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Saved BedGraph {bedgraph.stem} to {chipsample}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"BedGraph {bedgraph.stem} for {chipsample} already exists."
                    )
                )

        # Gather quality metrics for chip sample
        gt_sample_summary = results.joinpath("gtcs/gt_sample_summary.csv")
        with open(gt_sample_summary, "r") as f:
            samples = [i.split(",") for i in f.read().splitlines()[1:]]
            for sample in samples:
                print(sample)
                position = sample[0].split("_")[1]
                try:
                    chipsample = ChipSample.objects.get(
                        chip__chip_id=chip_id, position=position
                    )
                    chipsample.autosomal_call_rate = sample[3]
                    chipsample.call_rate = sample[4]
                    chipsample.lrr_std_dev = sample[5]
                    chipsample.sex_estimate = sample[6]
                    chipsample.save()

                except ChipSample.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"ChipSample not found for position {position}"
                        )
                    )
                    continue
                self.stdout.write(
                    self.style.SUCCESS(f"Updated quality metrics for {chipsample}")
                )


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
