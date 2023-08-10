# Generated by Django 4.2 on 2023-08-09 15:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0108_alter_inmueblevaloracionconstruccion_fecha_construccion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inmueblevaloracionconstruccion',
            name='tipologia',
            field=models.ForeignKey(blank=True, help_text='tipologia asociado', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.tipologia'),
        ),
    ]
