# Generated by Django 4.2.15 on 2024-08-27 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0017_alter_experience_responsibilities"),
    ]

    operations = [
        migrations.AddField(
            model_name="resume",
            name="json",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
