# Generated by Django 4.2 on 2023-06-13 10:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0061_pagoestadocuentadetalle_fecha'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagoestadocuentadetalle',
            name='fechapago',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, help_text='Fecha pago'),
            preserve_default=False,
        ),
    ]