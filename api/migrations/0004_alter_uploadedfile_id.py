# Generated by Django 4.2.15 on 2024-08-24 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_uploadedfile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='id',
            field=models.BigIntegerField(default=1724528196347, editable=False, primary_key=True, serialize=False),
        ),
    ]
