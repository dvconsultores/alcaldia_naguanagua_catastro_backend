# Generated by Django 4.2 on 2023-06-13 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0059_pagoestadocuentadetalle_tipopago'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagoestadocuentadetalle',
            name='fecha',
        ),
    ]
