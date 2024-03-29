# Generated by Django 4.2 on 2024-02-19 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0184_departamento_finaliza_flujo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='conjuntoresidencial',
            options={'ordering': ['urbanizacion', 'nombre']},
        ),
        migrations.AlterModelOptions(
            name='edificio',
            options={'ordering': ['conjuntoresidencial', 'nombre']},
        ),
        migrations.AlterModelOptions(
            name='torre',
            options={'ordering': ['conjuntoresidencial', 'nombre']},
        ),
        migrations.AlterUniqueTogether(
            name='conjuntoresidencial',
            unique_together={('urbanizacion', 'nombre')},
        ),
        migrations.AlterUniqueTogether(
            name='edificio',
            unique_together={('conjuntoresidencial', 'nombre')},
        ),
        migrations.AlterUniqueTogether(
            name='torre',
            unique_together={('conjuntoresidencial', 'nombre')},
        ),
        migrations.RemoveField(
            model_name='conjuntoresidencial',
            name='codigo',
        ),
        migrations.RemoveField(
            model_name='edificio',
            name='codigo',
        ),
        migrations.RemoveField(
            model_name='torre',
            name='codigo',
        ),
    ]
