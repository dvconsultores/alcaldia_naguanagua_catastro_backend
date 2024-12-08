# Generated by Django 4.2 on 2024-02-20 03:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0197_alter_parcela_sector'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parcela',
            name='sector',
            field=models.ForeignKey(blank=True, help_text='Sector asociado.', null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.sector'),
        ),
    ]