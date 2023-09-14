# Generated by Django 4.2 on 2023-09-08 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0125_banco_codigo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sector',
            name='codigo',
            field=models.TextField(help_text='Codigo del Sector'),
        ),
        migrations.AlterUniqueTogether(
            name='sector',
            unique_together={('ambito', 'codigo')},
        ),
    ]
