# Generated by Django 4.2 on 2024-10-14 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0232_corridasbancarias_habilitado_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='correlativo',
            name='Numero_Referencia_Bancaria',
            field=models.PositiveIntegerField(blank=True, help_text='Correltivo para referencias repetidas', null=True),
        ),
    ]