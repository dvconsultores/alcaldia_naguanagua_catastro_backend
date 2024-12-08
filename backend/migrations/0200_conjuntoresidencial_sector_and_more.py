# Generated by Django 4.2 on 2024-02-20 03:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0199_alter_edificio_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='conjuntoresidencial',
            name='sector',
            field=models.ForeignKey(blank=True, help_text='Sector asociado.', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.sector'),
        ),
        migrations.AlterField(
            model_name='conjuntoresidencial',
            name='urbanizacion',
            field=models.ForeignKey(blank=True, help_text='Urbanizacion/barrio asociada', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.urbanizacion'),
        ),
    ]