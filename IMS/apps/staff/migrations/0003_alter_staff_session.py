# Generated by Django 5.2.4 on 2025-08-01 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_staff_session'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='session',
            field=models.PositiveIntegerField(blank=True, default=None, help_text='Session or academic year information (leave blank if not specified)', null=True),
        ),
    ]
