# Generated by Django 4.2 on 2023-08-16 16:47

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0111_ae_actividadeconomica_ae_actividadeconomicadetalle_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ae_actividadeconomicadetalle',
            name='porcentaje_maximo_ingresos',
            field=models.DecimalField(decimal_places=8, default=Decimal('0'), help_text='este  impuesto no puede ser superior a este % de los ingresos brutos obtenidos en el mes', max_digits=22),
        ),
        migrations.AlterField(
            model_name='ae_actividadeconomicadetalle',
            name='minimo_tributable_anual',
            field=models.DecimalField(decimal_places=8, default=Decimal('0'), max_digits=22),
        ),
        migrations.AlterField(
            model_name='ae_actividadeconomicadetalle',
            name='minimo_tributable_mensual',
            field=models.DecimalField(decimal_places=8, default=Decimal('0'), max_digits=22),
        ),
    ]
