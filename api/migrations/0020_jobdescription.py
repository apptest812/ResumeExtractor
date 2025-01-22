# Generated by Django 4.2.15 on 2024-10-08 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0019_remove_resume_educations_remove_resume_experiences_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="JobDescription",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(blank=True, max_length=200, null=True)),
                ("position", models.CharField(blank=True, max_length=200, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("main_technologies", models.TextField(blank=True, null=True)),
                ("required_skills", models.TextField(blank=True, null=True)),
                ("responsibilities", models.TextField(blank=True, null=True)),
                ("required_qualification", models.TextField(blank=True, null=True)),
                ("preferred_qualification", models.TextField(blank=True, null=True)),
                ("experienceInMonths", models.IntegerField(blank=True, null=True)),
                ("salary", models.CharField(blank=True, max_length=200, null=True)),
                ("location", models.CharField(blank=True, max_length=200, null=True)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
