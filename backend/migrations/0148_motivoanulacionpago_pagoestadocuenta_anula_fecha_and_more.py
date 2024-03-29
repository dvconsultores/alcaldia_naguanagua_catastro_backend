# Generated by Django 4.2 on 2023-10-23 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0147_alter_tipoflujo_aplica'),
    ]

    operations = [
        migrations.CreateModel(
            name='MotivoAnulacionPago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(help_text='Descripcion del motivo', unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='pagoestadocuenta',
            name='anula_fecha',
            field=models.DateTimeField(blank=True, help_text='Fecha Anulacion', null=True),
        ),
        migrations.AddField(
            model_name='pagoestadocuenta',
            name='anula_observaciones',
            field=models.TextField(blank=True, help_text='observaciones por la anulacion', null=True),
        ),
        migrations.AddField(
            model_name='pagoestadocuenta',
            name='anula_usuario',
            field=models.TextField(blank=True, help_text='usuario que anula', null=True),
        ),
        migrations.AddField(
            model_name='pagoestadocuenta',
            name='habilitado',
            field=models.BooleanField(default=True, help_text='Esta activo?'),
        ),
        migrations.AddField(
            model_name='pagoestadocuenta',
            name='motivoanulacionpago',
            field=models.ForeignKey(blank=True, help_text='ID MotivoAnulacionPago', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.motivoanulacionpago'),
        ),
    ]
