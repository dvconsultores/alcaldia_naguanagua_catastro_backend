# Generated by Django 4.2 on 2024-03-18 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0210_inmueble_comunidad'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='flujo',
            index=models.Index(fields=['numero'], name='backend_flu_numero_77c665_idx'),
        ),
        migrations.AddIndex(
            model_name='flujodetalle',
            index=models.Index(fields=['flujo'], name='backend_flu_flujo_i_59cec8_idx'),
        ),
    ]
