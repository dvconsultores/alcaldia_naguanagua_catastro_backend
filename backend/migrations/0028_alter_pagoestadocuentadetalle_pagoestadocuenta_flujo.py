# Generated by Django 4.2 on 2023-06-05 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0027_delete_flujo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagoestadocuentadetalle',
            name='pagoestadocuenta',
            field=models.ForeignKey(help_text='ID Cabecera PAGO', on_delete=django.db.models.deletion.PROTECT, to='backend.pagoestadocuenta'),
        ),
        migrations.CreateModel(
            name='Flujo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inmueble', models.ForeignKey(help_text='Inmueble', on_delete=django.db.models.deletion.PROTECT, to='backend.inmueble')),
                ('pagoestadocuenta', models.ForeignKey(help_text='ID Cabecera PAGO', on_delete=django.db.models.deletion.PROTECT, to='backend.pagoestadocuenta')),
            ],
        ),
    ]
