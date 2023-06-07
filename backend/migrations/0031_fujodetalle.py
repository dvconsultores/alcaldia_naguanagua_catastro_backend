# Generated by Django 4.2 on 2023-06-06 09:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend', '0030_delete_fujodetalle'),
    ]

    operations = [
        migrations.CreateModel(
            name='FujoDetalle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('1', 'Pendiente por Recibir'), ('2', 'Recibido'), ('3', 'Pendiente por Procesar'), ('4', 'Procesado'), ('5', 'Pendiente por Enviar'), ('6', 'Enviado'), ('7', 'Finalizado'), ('8', 'Fin del Proceso')], default='1', help_text='Estado del proceso', max_length=1)),
                ('tarea', models.CharField(choices=[('1', 'Pendiente por Realizar'), ('2', 'Realizado')], default='1', help_text='Estado del proceso', max_length=1)),
                ('envia_fecha', models.DateTimeField(blank=True, help_text='Fecha Estado Cuenta')),
                ('recibe_fecha', models.DateTimeField(blank=True, help_text='Fecha Estado Cuenta')),
                ('observaciones', models.TextField(help_text='observaciones')),
                ('envia_usuario', models.ForeignKey(help_text='usuario asociado', on_delete=django.db.models.deletion.CASCADE, related_name='FujoDetalle_envia_usuario', to=settings.AUTH_USER_MODEL)),
                ('flujo', models.ForeignKey(help_text='ID Cabecera PAGO', on_delete=django.db.models.deletion.PROTECT, to='backend.flujo')),
                ('recibe_usuario', models.ForeignKey(help_text='usuario asociado', on_delete=django.db.models.deletion.CASCADE, related_name='FujoDetalle_recibe_usuario', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]