# Generated by Django 4.2 on 2023-08-09 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0106_remove_ic_periodo_diafin_remove_ic_periodo_diainicio_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tipologia',
            name='m2desde',
        ),
        migrations.RemoveField(
            model_name='tipologia',
            name='m2hasta',
        ),
        migrations.RemoveField(
            model_name='tipologia',
            name='se_lista',
        ),
        migrations.RemoveField(
            model_name='tipologia',
            name='valor',
        ),
        migrations.AlterField(
            model_name='tipologia',
            name='descripcion',
            field=models.TextField(help_text='descripcion de tipologia'),
        ),
    ]
