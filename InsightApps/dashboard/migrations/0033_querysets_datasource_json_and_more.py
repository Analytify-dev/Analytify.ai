# Generated by Django 4.1.13 on 2024-07-01 06:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0032_chartfilters_datasource_querysetid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='querysets',
            name='datasource_json',
            field=models.URLField(db_column='datasource_json_url', null=True),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 276501)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 3, 12, 10, 42, 276501)),
        ),
        migrations.AlterField(
            model_name='chartfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 280487)),
        ),
        migrations.AlterField(
            model_name='dashboard_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 283476)),
        ),
        migrations.AlterField(
            model_name='datasource_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 280487)),
        ),
        migrations.AlterField(
            model_name='datasourcefilter',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 281481)),
        ),
        migrations.AlterField(
            model_name='filedetails',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 278495)),
        ),
        migrations.AlterField(
            model_name='functions_tb',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 281481)),
        ),
        migrations.AlterField(
            model_name='license_key',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 282482)),
        ),
        migrations.AlterField(
            model_name='querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 279488)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 277494)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 279488)),
        ),
        migrations.AlterField(
            model_name='sheet_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 283476)),
        ),
        migrations.AlterField(
            model_name='sheetfilter_querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 284472)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 1, 12, 10, 42, 274696)),
        ),
    ]
