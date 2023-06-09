# Generated by Django 4.2 on 2023-05-25 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_alter_tasabcv_fecha_alter_tasabcv_fecha_vigente_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inmueble',
            name='fecha_inscripcion',
            field=models.DateField(blank=True, help_text='fecha de inscripcion'),
        ),
        migrations.AlterField(
            model_name='inmueblepropiedad',
            name='fecha_construccion',
            field=models.DateField(blank=True, help_text='fecha de inscripcion'),
        ),
        migrations.AlterField(
            model_name='inmueblepropiedad',
            name='fecha_documento',
            field=models.DateField(blank=True, help_text='fecha de inscripcion'),
        ),
        migrations.AlterField(
            model_name='inmueblepropiedad',
            name='fecha_habitabilidad',
            field=models.DateField(blank=True, help_text='fecha_habitabilidad'),
        ),
        migrations.AlterField(
            model_name='inmueblepropiedad',
            name='fecha_terreno',
            field=models.DateField(blank=True, help_text='fecha de inscripcion'),
        ),
        migrations.AlterField(
            model_name='inmueblepropiedad',
            name='fecha_vigencia',
            field=models.DateField(blank=True, help_text='fecha de inscripcion'),
        ),
        migrations.AlterField(
            model_name='inmueblevaloracionconstruccion',
            name='fecha_compra',
            field=models.DateField(blank=True, help_text='fecha_compra'),
        ),
    ]
