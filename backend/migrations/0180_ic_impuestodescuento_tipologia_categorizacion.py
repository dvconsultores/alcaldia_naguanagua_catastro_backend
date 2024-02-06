# Generated by Django 4.2 on 2024-01-25 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0179_inmueble_categorizacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic_impuestodescuento',
            name='tipologia_categorizacion',
            field=models.ForeignKey(blank=True, help_text='tipologia asociado. Solo para Inmuebles. Si no tiene aplica a cualquier uso', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.tipologia_categorizacion'),
        ),
    ]