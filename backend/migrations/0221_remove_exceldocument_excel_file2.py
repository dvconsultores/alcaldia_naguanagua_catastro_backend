# Generated by Django 4.2 on 2024-04-22 12:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0220_exceldocument_excel_file2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exceldocument',
            name='excel_file2',
        ),
    ]