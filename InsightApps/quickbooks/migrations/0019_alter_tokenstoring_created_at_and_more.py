# Generated by Django 4.1.13 on 2024-08-08 12:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickbooks', '0018_alter_tokenstoring_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokenstoring',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 899153)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 18, 45, 19, 899153)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 8, 17, 45, 19, 899153)),
        ),
    ]