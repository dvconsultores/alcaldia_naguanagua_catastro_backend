# Generated by Django 4.2 on 2023-08-29 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0116_pagoestadocuentadetalle_nro_aprobacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='correlativo',
            name='NumeroNotaCredito',
            field=models.PositiveIntegerField(blank=True, help_text='Numero de nota de credito', null=True),
        ),
        migrations.AddField(
            model_name='tipopago',
            name='codigo',
            field=models.TextField(blank=True, help_text='codigo Tipo de pago', null=True),
        ),
    ]
