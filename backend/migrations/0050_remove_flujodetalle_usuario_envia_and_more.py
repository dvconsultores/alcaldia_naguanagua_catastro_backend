# Generated by Django 4.2 on 2023-06-10 00:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend', '0049_alter_flujodetalle_recibe_usuario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flujodetalle',
            name='usuario_envia',
        ),
        migrations.RemoveField(
            model_name='flujodetalle',
            name='usuario_recibe',
        ),
        migrations.AddField(
            model_name='flujodetalle',
            name='fin_usuario',
            field=models.ForeignKey(blank=True, help_text='usuario asociado', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='FujoDetalle_fin_usuario', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='flujodetalle',
            name='inicio_proceso_usuario',
            field=models.ForeignKey(blank=True, help_text='usuario asociado', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='FujoDetalle_inicio_proceso_usuario', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='flujodetalle',
            name='procesa_usuario',
            field=models.ForeignKey(blank=True, help_text='usuario asociado', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='FujoDetalle_procesa_usuario', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='flujodetalle',
            name='estado',
            field=models.CharField(choices=[('1', 'Pendiente por Recibir'), ('2', 'Recibido'), ('3', 'Pendiente por Procesar'), ('4', 'En proceso'), ('5', 'Proceso Culminado'), ('6', 'Pendiente por Enviar'), ('7', 'Enviado'), ('8', 'Finalizado'), ('9', 'Fin de la Solcitud')], default='1', help_text='Estado del proceso', max_length=1),
        ),
        migrations.AlterField(
            model_name='flujodetalle',
            name='fin_fecha',
            field=models.DateTimeField(blank=True, help_text='Fecha FIN DE LA SOLICITUD', null=True),
        ),
        migrations.AlterField(
            model_name='flujodetalle',
            name='tarea',
            field=models.CharField(choices=[('1', 'Pendiente por Recibir'), ('3', 'Pendiente por Procesar'), ('6', 'Pendiente por Enviar'), ('8', 'Finalizado')], default='1', help_text='Estado del proceso', max_length=1),
        ),
    ]
