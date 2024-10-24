# Generated by Django 5.0.7 on 2024-10-22 13:11

import canvas.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canvas', '0007_chiptype_band_path_chiptype_bpm_path_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chiptype',
            name='band_path',
        ),
        migrations.RemoveField(
            model_name='chiptype',
            name='bpm_path',
        ),
        migrations.RemoveField(
            model_name='chiptype',
            name='csv_path',
        ),
        migrations.RemoveField(
            model_name='chiptype',
            name='egt_path',
        ),
        migrations.RemoveField(
            model_name='chiptype',
            name='fasta_path',
        ),
        migrations.RemoveField(
            model_name='chiptype',
            name='pfb_path',
        ),
        migrations.AddField(
            model_name='chiptype',
            name='band',
            field=models.FileField(blank=True, upload_to=canvas.models.analysis_files_directory_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['txt'])]),
        ),
        migrations.AddField(
            model_name='chiptype',
            name='bpm',
            field=models.FileField(blank=True, upload_to=canvas.models.analysis_files_directory_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['bpm'])]),
        ),
        migrations.AddField(
            model_name='chiptype',
            name='csv',
            field=models.FileField(blank=True, upload_to=canvas.models.analysis_files_directory_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['csv'])]),
        ),
        migrations.AddField(
            model_name='chiptype',
            name='egt',
            field=models.FileField(blank=True, upload_to=canvas.models.analysis_files_directory_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['egt'])]),
        ),
        migrations.AddField(
            model_name='chiptype',
            name='fasta',
            field=models.FileField(blank=True, upload_to=canvas.models.analysis_files_directory_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['fa'])]),
        ),
        migrations.AddField(
            model_name='chiptype',
            name='pfb',
            field=models.FileField(blank=True, upload_to=canvas.models.analysis_files_directory_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pfb'])]),
        ),
    ]
