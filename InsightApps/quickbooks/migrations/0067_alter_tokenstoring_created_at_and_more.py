# Generated by Django 4.1.13 on 2024-10-22 05:47

from django.db import migrations, models
import django.utils.timezone
import quickbooks.models


class Migration(migrations.Migration):

    dependencies = [
        ('quickbooks', '0066_alter_tokenstoring_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokenstoring',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='expiry_date',
            field=models.DateTimeField(default=quickbooks.models.get_expiry_date),
        ),
        migrations.AlterField(
            model_name='tokenstoring',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]