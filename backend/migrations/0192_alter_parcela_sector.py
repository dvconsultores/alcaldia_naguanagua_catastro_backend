# Generated by Django 4.2 on 2024-02-19 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0191_alter_parcela_codigo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parcela',
            name='sector',
            field=models.ForeignKey(help_text='Sector asociado', on_delete=django.db.models.deletion.PROTECT, to='backend.sector'),
        ),
    ]
