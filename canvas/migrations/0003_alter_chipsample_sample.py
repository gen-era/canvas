# Generated by Django 5.0.7 on 2024-10-11 15:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canvas', '0002_chiptype_cols_chiptype_rows'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chipsample',
            name='sample',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='chipsample', to='canvas.sample'),
        ),
    ]
