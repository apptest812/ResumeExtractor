# Generated by Django 4.2.15 on 2024-10-08 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0020_jobdescription"),
    ]

    operations = [
        migrations.AddField(
            model_name="uploadedfile",
            name="is_job_description",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="uploadedfile",
            name="is_resume",
            field=models.BooleanField(default=True),
        ),
    ]
