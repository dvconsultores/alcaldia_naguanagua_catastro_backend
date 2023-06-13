# Generated by Django 4.2 on 2023-06-13 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0056_remove_pagoestadocuentadetalle_banco_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banco',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(help_text='Nombre del banco', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='BancoCuenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.TextField(help_text='Numero de Cuenta', unique=True)),
                ('tipo', models.CharField(choices=[('1', 'Corriente'), ('2', 'Ahorro')], default='1', help_text='Tipo de Cuenta', max_length=1)),
                ('banco', models.ForeignKey(help_text='ID Banco', on_delete=django.db.models.deletion.PROTECT, to='backend.banco')),
            ],
        ),
    ]