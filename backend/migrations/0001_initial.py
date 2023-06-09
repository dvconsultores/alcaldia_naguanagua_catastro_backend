# Generated by Django 4.2 on 2023-05-08 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ambito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.TextField(help_text='Codigo del ambito', unique=True)),
                ('descripcion', models.TextField(help_text='Descripcion del ambito', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.TextField(help_text='Codigo del Sector', unique=True)),
                ('descripcion', models.TextField(help_text='Descripcion del Sector', unique=True)),
                ('area', models.TextField(help_text='area del Sector', unique=True)),
                ('perimetro', models.TextField(help_text='Descripcion del Sector', unique=True)),
                ('clasificacion', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], default='A', help_text='clasificacion del Sector', max_length=1)),
                ('ambito', models.ForeignKey(help_text='ambito asociado', on_delete=django.db.models.deletion.PROTECT, to='backend.ambito')),
            ],
        ),
    ]
