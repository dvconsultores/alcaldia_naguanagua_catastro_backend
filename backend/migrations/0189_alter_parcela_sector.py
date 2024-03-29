# Generated by Django 4.2 on 2024-02-19 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0188_alter_parcela_options_alter_parcela_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parcela',
            name='sector',
            field=models.ForeignKey(blank=True, help_text='Sector asociado', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.sector'),
        ),
    ]
