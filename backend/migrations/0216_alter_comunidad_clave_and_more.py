# Generated by Django 4.2 on 2024-04-08 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0215_alter_correlativo_logo1_alter_correlativo_logo2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comunidad',
            name='clave',
            field=models.TextField(blank=True, help_text='numero_civico de expediente.', null=True),
        ),
        migrations.AlterField(
            model_name='historicalcomunidad',
            name='clave',
            field=models.TextField(blank=True, help_text='numero_civico de expediente.', null=True),
        ),
    ]
