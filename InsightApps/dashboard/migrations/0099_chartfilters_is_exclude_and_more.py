# Generated by Django 4.1.13 on 2024-10-10 06:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0098_merge_20240930_2334'),
    ]

    operations = [
        migrations.AddField(
            model_name='chartfilters',
            name='is_exclude',
            field=models.BooleanField(default=False),
        )
    ]