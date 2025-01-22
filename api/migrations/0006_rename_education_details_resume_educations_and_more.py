# Generated by Django 4.2.15 on 2024-08-25 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_uploadedfile_in_progress_alter_education_degree_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resume',
            old_name='education_details',
            new_name='educations',
        ),
        migrations.AlterField(
            model_name='resume',
            name='id',
            field=models.BigIntegerField(default=1724610370664, editable=False, primary_key=True, serialize=False),
        ),
        migrations.RemoveField(
            model_name='resume',
            name='skills',
        ),
        migrations.AlterField(
            model_name='uploadedfile',
            name='id',
            field=models.BigIntegerField(default=1724610370665, editable=False, primary_key=True, serialize=False),
        ),
        migrations.DeleteModel(
            name='Skill',
        ),
        migrations.AddField(
            model_name='resume',
            name='skills',
            field=models.TextField(blank=True, null=True),
        ),
    ]
