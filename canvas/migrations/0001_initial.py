# Generated by Django 5.0.7 on 2024-09-18 13:52

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChipType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('rows', models.IntegerField(default=12)),
                ('cols', models.IntegerField(default=2)),
            ],
        ),
        migrations.CreateModel(
            name='Lot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lot_number', models.CharField(max_length=200)),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('arrival_date', models.DateTimeField(verbose_name='Entry date')),
            ],
        ),
        migrations.CreateModel(
            name='SampleType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Chip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chip_id', models.CharField(max_length=200)),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('protocol_start_date', models.DateTimeField(verbose_name='Start date')),
                ('scan_date', models.DateTimeField(verbose_name='Scan date')),
                ('lab_practitioner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('chip_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='canvas.chiptype')),
                ('lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='canvas.lot')),
            ],
        ),
        migrations.CreateModel(
            name='ChipSample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('call_rate', models.DecimalField(decimal_places=8, default=0, max_digits=10)),
                ('autosomal_call_rate', models.DecimalField(decimal_places=8, default=0, max_digits=10)),
                ('lrr_std_dev', models.DecimalField(decimal_places=8, default=0, max_digits=10)),
                ('sex_estimate', models.CharField(choices=[('F', 'Female'), ('M', 'Male'), ('U', 'Unknown')], max_length=100, null=True)),
                ('position', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(code='invalid_position', message='Position should follow this structure: R01C01', regex='^R\\d{2}C\\d{2}$')])),
                ('chip', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='chipsample', to='canvas.chip')),
            ],
        ),
        migrations.CreateModel(
            name='BedGraph',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('bedgraph_type', models.CharField(choices=[('LRR', 'Log R Ratio'), ('BAF', 'B Allele Frequency')], max_length=50)),
                ('bedgraph', models.FileField(upload_to='bedGraphs/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['gz'])])),
                ('chipsample', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bedgraph', to='canvas.chipsample')),
            ],
        ),
        migrations.CreateModel(
            name='CNV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('variant_id', models.CharField(max_length=255)),
                ('cnv_json', models.JSONField()),
                ('chipsample', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cnv', to='canvas.chipsample')),
            ],
        ),
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('classification_json', models.JSONField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('cnv', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='classification', to='canvas.cnv')),
            ],
        ),
        migrations.CreateModel(
            name='GTC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('gtc', models.FileField(upload_to='gtcs/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['gtc'])])),
                ('chipsample', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='canvas.chipsample')),
            ],
        ),
        migrations.CreateModel(
            name='IDAT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('idat', models.FileField(upload_to='idats/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['idat'])])),
                ('chipsample', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='canvas.chipsample')),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='institutions', to='auth.group')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('report', models.FileField(upload_to='reports/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
                ('classifications', models.ManyToManyField(to='canvas.classification')),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('arrival_date', models.DateField()),
                ('study_date', models.DateField(null=True)),
                ('protocol_id', models.CharField(max_length=100)),
                ('concentration', models.DecimalField(decimal_places=1, max_digits=5)),
                ('sex', models.CharField(choices=[('F', 'Female'), ('M', 'Male'), ('U', 'Unknown')], max_length=100, null=True)),
                ('description', models.CharField(max_length=255, null=True)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sample', to='canvas.institution')),
                ('repeat', models.ManyToManyField(blank=True, to='canvas.sample')),
                ('sample_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='canvas.sampletype')),
            ],
        ),
        migrations.AddField(
            model_name='chipsample',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chipsample', to='canvas.sample'),
        ),
        migrations.CreateModel(
            name='SampleSheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('samplesheet', models.FileField(upload_to='samplesheets/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['tsv'])])),
                ('chip', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='samplesheet', to='canvas.chip')),
            ],
        ),
        migrations.CreateModel(
            name='VCF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_date', models.DateTimeField(auto_now_add=True)),
                ('vcf', models.FileField(upload_to='vcfs/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['vcf.gz'])])),
                ('chipsample', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='canvas.chipsample')),
            ],
        ),
    ]
