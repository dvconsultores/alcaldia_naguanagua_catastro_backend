# Generated by Django 4.2 on 2024-02-23 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0202_comunidad_inmueblecategorizacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='comunidad',
            name='clave',
            field=models.TextField(blank=True, help_text='numero_civico de expediente', null=True),
        ),
    ]