# Generated by Django 4.2 on 2023-12-14 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0155_correlativo_logo1_correlativo_logo2'),
    ]

    operations = [
        migrations.AddField(
            model_name='estatusinmueble',
            name='inmueble_activo',
            field=models.BooleanField(default=True, help_text='si es tru, este estatus permite procesar el inmueble para calculo de impuestos'),
        ),
    ]
