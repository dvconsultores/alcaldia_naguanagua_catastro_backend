# Generated by Django 4.2 on 2023-07-20 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0084_tipoflujo_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='estadocuentadetalle',
            name='observaciones',
            field=models.TextField(blank=True, help_text='observaciones', null=True),
        ),
        migrations.AddField(
            model_name='inmueblepropietarios',
            name='multa_articulo_101',
            field=models.BooleanField(default=True, help_text='True si al momento de cargar este nuevo propietario, generó multa'),
        ),
        migrations.AddField(
            model_name='liquidaciondetalle',
            name='observaciones',
            field=models.TextField(blank=True, help_text='observaciones', null=True),
        ),
        migrations.AddField(
            model_name='tasamulta',
            name='codigo',
            field=models.TextField(blank=True, help_text='Codigo de la Tasa Multa', null=True),
        ),
        migrations.AlterField(
            model_name='inmueblevaloracionconstruccion',
            name='sub_utilizado',
            field=models.BooleanField(default=False, help_text='subutilizado si o no'),
        ),
        migrations.AlterField(
            model_name='tipoflujo',
            name='codigo',
            field=models.TextField(blank=True, help_text='Codigo del Tipo de Flujo', null=True),
        ),
    ]
