# Generated by Django 4.2 on 2023-12-19 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0160_inmueble_reportepdfcedulacatastral_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inmueblepropiedad',
            name='valor_construccion',
            field=models.TextField(blank=True, help_text='valor construccion', null=True),
        ),
    ]
