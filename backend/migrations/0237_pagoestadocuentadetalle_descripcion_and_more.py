# Generated by Django 4.2 on 2024-10-31 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0236_corridasbancarias_observaciones_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagoestadocuentadetalle',
            name='descripcion',
            field=models.TextField(blank=True, help_text='descripcion - - SOLO PARA TRANSFERENCIAS DE CORRIDASBANCARIAS', null=True),
        ),
        migrations.AddField(
            model_name='pagoestadocuentadetalle',
            name='fecha',
            field=models.DateField(blank=True, help_text='Fecha- SOLO PARA TRANSFERENCIAS DE CORRIDASBANCARIAS', null=True),
        ),
    ]
