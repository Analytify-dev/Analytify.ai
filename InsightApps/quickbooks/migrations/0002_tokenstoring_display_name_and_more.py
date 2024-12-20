# Generated by Django 4.1.13 on 2024-07-24 18:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickbooks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokenstoring',
            name='display_name',
            field=models.CharField(blank=True, db_column='display_name', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 25, 0, 11, 55, 103718)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 25, 1, 11, 55, 102707)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 25, 0, 11, 55, 103718)),
        ),
    ]
