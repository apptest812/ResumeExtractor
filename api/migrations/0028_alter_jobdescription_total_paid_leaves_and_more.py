# Generated by Django 4.2.15 on 2024-10-21 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0027_jobdescription_weekly_working_days"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobdescription",
            name="total_paid_leaves",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name="jobdescription",
            name="weekly_working_days",
            field=models.IntegerField(blank=True, default=6, null=True),
        ),
    ]
