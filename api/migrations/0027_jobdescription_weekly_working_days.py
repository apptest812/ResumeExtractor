# Generated by Django 4.2.15 on 2024-10-21 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "api",
            "0026_rename_experienceinmonths_jobdescription_max_experience_in_months_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="jobdescription",
            name="weekly_working_days",
            field=models.IntegerField(default=6),
        ),
    ]
