# Generated by Django 4.2 on 2023-06-12 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0053_estadocuenta_habilitado'),
    ]

    operations = [
        migrations.AddField(
            model_name='liquidacion',
            name='habilitado',
            field=models.BooleanField(default=True, help_text='Esta activo?'),
        ),
        migrations.AddField(
            model_name='pagoestadocuentadetalle',
            name='nro_referencia',
            field=models.TextField(blank=True, help_text='numero de referencia', null=True),
        ),
        migrations.AlterField(
            model_name='pagoestadocuentadetalle',
            name='banco',
            field=models.TextField(blank=True, help_text='banco', null=True),
        ),
        migrations.AlterField(
            model_name='pagoestadocuentadetalle',
            name='cedula',
            field=models.TextField(blank=True, help_text='cedula', null=True),
        ),
        migrations.AlterField(
            model_name='pagoestadocuentadetalle',
            name='fecha',
            field=models.TextField(blank=True, help_text='fecha', null=True),
        ),
        migrations.AlterField(
            model_name='pagoestadocuentadetalle',
            name='nro_cuenta',
            field=models.TextField(blank=True, help_text='nro_cuenta', null=True),
        ),
        migrations.AlterField(
            model_name='pagoestadocuentadetalle',
            name='telefono',
            field=models.TextField(blank=True, help_text='telefono', null=True),
        ),
    ]
