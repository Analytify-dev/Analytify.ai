# Generated by Django 4.1.13 on 2024-12-02 17:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0125_dashboard_drill_through_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='calculation_field',
            name='functionName',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='calculation_field',
            name='nestedFunctionName',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]