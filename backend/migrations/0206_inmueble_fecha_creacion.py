# Generated by Django 4.2 on 2024-03-01 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0205_tipoflujo_crea_expediente'),
    ]

    operations = [
        migrations.AddField(
            model_name='inmueble',
            name='fecha_creacion',
            field=models.DateField(blank=True, help_text='fecha de creacion en el modelo', null=True),
        ),
    ]