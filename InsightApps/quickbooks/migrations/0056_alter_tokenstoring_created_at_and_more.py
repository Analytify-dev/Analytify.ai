# Generated by Django 4.1.13 on 2024-10-15 09:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickbooks', '0055_alter_tokenstoring_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokenstoring',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 15, 12, 53, 677336)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 16, 12, 53, 676820)),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 15, 12, 53, 677336)),
        ),
    ]
