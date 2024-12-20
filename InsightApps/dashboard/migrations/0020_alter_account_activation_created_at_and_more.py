# Generated by Django 4.1.13 on 2024-06-10 14:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0019_alter_account_activation_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_activation',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 20, 11, 19, 359379)),
        ),
        migrations.AlterField(
            model_name='account_activation',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 12, 20, 11, 19, 359379)),
        ),
        migrations.AlterField(
            model_name='chartfilters',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 20, 11, 19, 360374)),
        ),
        migrations.AlterField(
            model_name='datasourcefilter',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 20, 11, 19, 361377)),
        ),
        migrations.AlterField(
            model_name='filedetails',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 20, 11, 19, 359379)),
        ),
        migrations.AlterField(
            model_name='functions_tb',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 20, 11, 19, 360374)),
        ),
        migrations.AlterField(
            model_name='license_key',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 20, 11, 19, 361377)),
        ),
        migrations.AlterField(
            model_name='querysets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 20, 11, 19, 360374)),
        ),
        migrations.AlterField(
            model_name='reset_password',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 20, 11, 19, 359379)),
        ),
        migrations.AlterField(
            model_name='serverdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 20, 11, 19, 360374)),
        ),
        migrations.AlterField(
            model_name='sheet_data',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 20, 11, 19, 361377)),
        ),
        migrations.AlterField(
            model_name='sheet_data',
            name='datapath',
            field=models.FileField(blank=True, db_column='sheet_data_path', max_length=1000, null=True, upload_to='insightapps/sheetdata/'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 10, 20, 11, 19, 358378)),
        ),
    ]
