# Generated by Django 4.2 on 2023-08-29 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0118_perfil_caja'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagoestadocuenta',
            name='caja',
            field=models.PositiveIntegerField(blank=True, help_text='Numero de Caja . Viene del modelo Perfil', null=True),
        ),
    ]