# Generated by Django 4.2 on 2023-12-19 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0162_alter_parcela_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urbanizacion',
            name='codigo',
            field=models.TextField(blank=True, help_text='Codigo de la Urbanizacion', null=True),
        ),
    ]