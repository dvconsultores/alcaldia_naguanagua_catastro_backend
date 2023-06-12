# Generated by Django 4.2 on 2023-06-09 23:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend', '0048_alter_flujodetalle_recibe_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flujodetalle',
            name='recibe_usuario',
            field=models.ForeignKey(default=1, help_text='usuario asociado', on_delete=django.db.models.deletion.CASCADE, related_name='FujoDetalle_recibe_usuario', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]