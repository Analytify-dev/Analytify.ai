# Generated by Django 4.1.13 on 2024-08-19 08:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0067_alter_account_activation_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 833142)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 21, 13, 49, 57, 833142)),
        ),
        migrations.AlterField(
            model_name='chartfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 835141)),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 837141)),
        ),
        migrations.AlterField(
            model_name='dashboardfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 838140)),
        ),
        migrations.AlterField(
            model_name='datasource_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 835141)),
        ),
        migrations.AlterField(
            model_name='datasourcefilter',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 836140)),
        ),
        migrations.AlterField(
            model_name='filedetails',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 834142)),
        ),
        migrations.AlterField(
            model_name='functions_tb',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 836140)),
        ),
        migrations.AlterField(
            model_name='license_key',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 836140)),
        ),
        migrations.AlterField(
            model_name='querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 835141)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 833142)),
        ),
        migrations.AlterField(
            model_name='role',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 833142)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 835141)),
        ),
        migrations.AlterField(
            model_name='sheet_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 837141)),
        ),
        migrations.AlterField(
            model_name='sheetfilter_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 837141)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 831146)),
        ),
    ]
