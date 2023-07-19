# Generated by Django 4.2 on 2023-07-19 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0078_rename_inmueble_terreno_inmueblevaloracionconstruccion_inmueblevaloracionterreno'),
    ]

    operations = [
        migrations.AddField(
            model_name='inmuebleterreno',
            name='regimen',
            field=models.ForeignKey(blank=True, help_text='regimen asociado', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.regimen'),
        ),
        migrations.DeleteModel(
            name='InmuebleTerrenoRegimen',
        ),
    ]