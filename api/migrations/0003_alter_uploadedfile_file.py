# Generated by Django 4.2.15 on 2024-08-24 05:26

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_uploadedfile_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='file',
            field=models.FileField(upload_to=api.models.upload_to),
        ),
    ]
