# Generated by Django 4.2 on 2023-10-02 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0143_exceldocument'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcelDocumentLOG',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pestana', models.CharField(help_text='Pestaña del archivo de excel', max_length=255)),
                ('codigo', models.CharField(help_text='id del registro con error', max_length=255)),
                ('error', models.CharField(help_text='codigo del error', max_length=255)),
                ('fecha', models.DateTimeField(help_text='Fecha registro error')),
            ],
        ),
    ]