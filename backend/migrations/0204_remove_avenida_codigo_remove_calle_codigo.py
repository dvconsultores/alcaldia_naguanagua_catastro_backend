# Generated by Django 4.2 on 2024-02-28 23:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0203_comunidad_clave'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='avenida',
            name='codigo',
        ),
        migrations.RemoveField(
            model_name='calle',
            name='codigo',
        ),
    ]