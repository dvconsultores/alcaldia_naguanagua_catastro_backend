# Generated by Django 4.2 on 2023-05-30 23:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0015_alter_modulo_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modulo',
            options={'ordering': ['menu', '-es_menu', 'orden']},
        ),
        migrations.AlterField(
            model_name='inmueblepropietarios',
            name='propietario',
            field=models.ForeignKey(help_text='Id Propietario', on_delete=django.db.models.deletion.PROTECT, to='backend.propietario'),
        ),
        migrations.AlterField(
            model_name='modulo',
            name='es_menu',
            field=models.BooleanField(default=False, help_text='Es TRUE si pertenece a un titulo de menu. En valor que contenga su campo NOMBRE lo debe contener cada campo MENU de sus opciones'),
        ),
        migrations.AlterField(
            model_name='modulo',
            name='menu',
            field=models.TextField(blank=True, help_text='Se coloca el valor del campo NOMBRE correpondiente al menu.', null=True),
        ),
        migrations.AlterField(
            model_name='modulo',
            name='nombre',
            field=models.CharField(help_text='Nombre exacto del archivo .VUE (a excepcion de los menues)', max_length=255, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='modulo',
            name='titulo',
            field=models.TextField(blank=True, help_text='Nombre que muestra en el Menu', null=True),
        ),
    ]
