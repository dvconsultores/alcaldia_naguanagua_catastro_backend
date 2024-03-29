# Generated by Django 4.2 on 2023-09-09 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0127_alter_manzana_options_alter_sector_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parcela',
            options={'ordering': ['manzana', 'codigo']},
        ),
        migrations.AlterField(
            model_name='parcela',
            name='codigo',
            field=models.TextField(help_text='Codigo de la Parcela'),
        ),
        migrations.AlterUniqueTogether(
            name='parcela',
            unique_together={('manzana', 'codigo')},
        ),
    ]
