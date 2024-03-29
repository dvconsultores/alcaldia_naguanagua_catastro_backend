# Generated by Django 4.2 on 2024-02-20 03:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0198_alter_parcela_sector'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='edificio',
            options={'ordering': ['urbanizacion', 'nombre']},
        ),
        migrations.AlterUniqueTogether(
            name='edificio',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='edificio',
            name='urbanizacion',
            field=models.ForeignKey(blank=True, help_text='Urbanizacion/barrio asociada', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.urbanizacion'),
        ),
        migrations.AlterField(
            model_name='edificio',
            name='conjuntoresidencial',
            field=models.ForeignKey(blank=True, help_text='conjunto residencial asociado', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.conjuntoresidencial'),
        ),
        migrations.AlterUniqueTogether(
            name='edificio',
            unique_together={('urbanizacion', 'nombre')},
        ),
    ]
