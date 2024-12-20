# Generated by Django 5.0.4 on 2024-05-07 12:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_serverdetails_is_connected_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 7, 17, 45, 10, 475204)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 9, 17, 45, 10, 475204)),
        ),
        migrations.AlterField(
            model_name='filedetails',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 7, 17, 45, 10, 476201)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 7, 17, 45, 10, 475204)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 7, 17, 45, 10, 477198)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='display_name',
            field=models.CharField(db_column='display_name', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 7, 17, 45, 10, 471202)),
        ),
    ]
