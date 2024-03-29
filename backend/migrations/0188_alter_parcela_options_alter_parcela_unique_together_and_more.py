# Generated by Django 4.2 on 2024-02-19 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0187_remove_manzana_area_remove_manzana_perimetro_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parcela',
            options={'ordering': ['sector', 'codigo']},
        ),
        migrations.AlterUniqueTogether(
            name='parcela',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='subparcela',
            name='area',
        ),
        migrations.RemoveField(
            model_name='subparcela',
            name='perimetro',
        ),
        migrations.AddField(
            model_name='parcela',
            name='sector',
            field=models.ForeignKey(default=1, help_text='Sector asociado', on_delete=django.db.models.deletion.PROTECT, to='backend.sector'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='parcela',
            unique_together={('sector', 'codigo')},
        ),
        migrations.RemoveField(
            model_name='parcela',
            name='area',
        ),
        migrations.RemoveField(
            model_name='parcela',
            name='manzana',
        ),
        migrations.RemoveField(
            model_name='parcela',
            name='perimetro',
        ),
    ]
