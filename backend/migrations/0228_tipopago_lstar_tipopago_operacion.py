# Generated by Django 4.2 on 2024-05-23 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0227_alter_tasamulta_aplica_alter_tasamulta_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipopago',
            name='lstar',
            field=models.BooleanField(default=True, help_text='se lista en los formularios?'),
        ),
        migrations.AddField(
            model_name='tipopago',
            name='operacion',
            field=models.CharField(choices=[('3', 'TRANSFERENCIA'), ('5', 'DEPOSITO'), ('11', 'DEBITO'), ('14', 'SITUADO'), ('4', 'INTERESES'), ('12', 'FCI'), ('X', 'Todos')], default='X', help_text='A que tipo de OPERACION aplica', max_length=2),
        ),
    ]
