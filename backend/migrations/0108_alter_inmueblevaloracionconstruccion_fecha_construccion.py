# Generated by Django 4.2 on 2023-08-09 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0107_remove_tipologia_m2desde_remove_tipologia_m2hasta_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inmueblevaloracionconstruccion',
            name='fecha_construccion',
            field=models.DateField(blank=True, help_text='fecha construccion', null=True),
        ),
    ]