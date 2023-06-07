# Generated by Django 4.2 on 2023-06-07 10:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0039_tipoflujo_estadocuenta_tipoflujo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liquidacion',
            name='tipoflujo',
            field=models.ForeignKey(blank=True, help_text='Tipo de flujo solo catasrro: inscripcion, actualizacion o modificar propietario', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.tipoflujo'),
        ),
    ]