# Generated by Django 4.1.13 on 2024-09-30 17:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0096_userrole_created_at_userrole_created_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 840141)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 2, 23, 1, 39, 840141)),
        ),
        migrations.AlterField(
            model_name='chartfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 842129)),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 844127)),
        ),
        migrations.AlterField(
            model_name='dashboardfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 845132)),
        ),
        migrations.AlterField(
            model_name='datasource_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 842129)),
        ),
        migrations.AlterField(
            model_name='datasourcefilter',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 843130)),
        ),
        migrations.AlterField(
            model_name='filedetails',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 841142)),
        ),
        migrations.AlterField(
            model_name='functions_tb',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 843130)),
        ),
        migrations.AlterField(
            model_name='license_key',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 843130)),
        ),
        migrations.AlterField(
            model_name='querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 842129)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 841142)),
        ),
        migrations.AlterField(
            model_name='role',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 841142)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 842129)),
        ),
        migrations.AlterField(
            model_name='sheet_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 844127)),
        ),
        migrations.AlterField(
            model_name='sheetfilter_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 844127)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 839133)),
        ),
        migrations.AlterField(
            model_name='userrole',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 30, 23, 1, 39, 841142)),
        ),
    ]