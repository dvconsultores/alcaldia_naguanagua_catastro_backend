# Generated by Django 4.2 on 2023-12-15 10:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0156_estatusinmueble_inmueble_activo'),
    ]

    operations = [
        migrations.CreateModel(
            name='MotivoDesincorporacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(help_text='Descripcion del motivo Desincorporación', unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='inmueble',
            name='motivodesincorporacion',
            field=models.ForeignKey(blank=True, help_text='Motivo Desincorporacion', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.motivodesincorporacion'),
        ),
    ]
