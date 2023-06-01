# Generated by Django 4.2 on 2023-05-24 14:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend', '0006_alter_estadocuenta_propietario_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Modulo',
            fields=[
                ('nombre', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activo', models.BooleanField(default=True, help_text='esta el usuario activo?')),
                ('tipo', models.CharField(choices=[('S', 'Super'), ('A', 'Admin'), ('U', 'Usuario'), ('C', 'Catastro'), ('T', 'Tributario')], default='U', help_text='Tipo de usuario', max_length=1, null=True)),
                ('usuario', models.OneToOneField(help_text='usuario asociado', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Permiso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leer', models.BooleanField(default=False, help_text='Tiene opcion de leer?')),
                ('escribir', models.BooleanField(default=False, help_text='Tiene opcion de escribir?')),
                ('borrar', models.BooleanField(default=False, help_text='Tiene opcion de borrar?')),
                ('actualizar', models.BooleanField(default=False, help_text='Tiene opcion de actualizar?')),
                ('modulo', models.ForeignKey(help_text='Opcion de menu asociada', on_delete=django.db.models.deletion.CASCADE, to='backend.modulo')),
                ('perfil', models.ForeignKey(help_text='Usuario asociado', on_delete=django.db.models.deletion.CASCADE, to='backend.perfil')),
            ],
        ),
    ]