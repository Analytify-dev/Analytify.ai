# Generated by Django 4.1.13 on 2024-08-19 08:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickbooks', '0022_alter_tokenstoring_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokenstoring',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 839142)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 14, 49, 57, 839142)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 19, 13, 49, 57, 839142)),
        ),
    ]
