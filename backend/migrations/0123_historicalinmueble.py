# Generated by Django 4.2 on 2023-08-31 12:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend', '0122_historicalinmueblevaloracionconstruccion'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalInmueble',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('numero_expediente', models.TextField(db_index=True, help_text='Numero de expediente.Correlativo.ExpedienteCatastro')),
                ('fecha_inscripcion', models.DateField(blank=True, help_text='fecha de inscripcion', null=True)),
                ('numero_civico', models.TextField(blank=True, help_text='Numero de expediente', null=True)),
                ('numero_casa', models.TextField(blank=True, help_text='Numero de expediente', null=True)),
                ('numero_piso', models.TextField(blank=True, help_text='Numero de expediente', null=True)),
                ('telefono', models.TextField(blank=True, help_text='Numero de expediente', null=True)),
                ('direccion', models.TextField(blank=True, help_text='direccion', null=True)),
                ('referencia', models.TextField(blank=True, help_text='referencia', null=True)),
                ('observaciones', models.TextField(blank=True, help_text='observaciones', null=True)),
                ('inscripcion_paga', models.BooleanField(default=False, help_text='True desde use_case de crear pago cuando se cancele el flujo de Inscripcion de Inmueble')),
                ('habilitado', models.BooleanField(default=True, help_text='Esta activo?')),
                ('anio', models.PositiveIntegerField(blank=True, help_text='Año que adeuda', null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('ambito', models.ForeignKey(blank=True, db_constraint=False, help_text='ambito asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.ambito')),
                ('avenida', models.ForeignKey(blank=True, db_constraint=False, help_text='avenida asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.avenida')),
                ('calle', models.ForeignKey(blank=True, db_constraint=False, help_text='calle asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.calle')),
                ('conjunto_residencial', models.ForeignKey(blank=True, db_constraint=False, help_text='Sector asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.conjuntoresidencial')),
                ('edificio', models.ForeignKey(blank=True, db_constraint=False, help_text='edificio asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.edificio')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('manzana', models.ForeignKey(blank=True, db_constraint=False, help_text='manzana asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.manzana')),
                ('nivel', models.ForeignKey(blank=True, db_constraint=False, help_text='nivel asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.nivelinmueble')),
                ('parcela', models.ForeignKey(blank=True, db_constraint=False, help_text='parcela asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.parcela')),
                ('periodo', models.ForeignKey(blank=True, db_constraint=False, help_text='Periodo que adeuda', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.ic_periodo')),
                ('sector', models.ForeignKey(blank=True, db_constraint=False, help_text='Sector asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.sector')),
                ('status', models.ForeignKey(blank=True, db_constraint=False, help_text='status asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.estatusinmueble')),
                ('subparcela', models.ForeignKey(blank=True, db_constraint=False, help_text='subparcela asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.subparcela')),
                ('tipo', models.ForeignKey(blank=True, db_constraint=False, help_text='TipoInmueble asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.tipoinmueble')),
                ('torre', models.ForeignKey(blank=True, db_constraint=False, help_text='Sector asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.torre')),
                ('unidad', models.ForeignKey(blank=True, db_constraint=False, help_text='unidad asociado', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.unidadinmueble')),
                ('urbanizacion', models.ForeignKey(blank=True, db_constraint=False, help_text='urbanizacion', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.urbanizacion')),
                ('zona', models.ForeignKey(blank=True, db_constraint=False, help_text='Zona !! Base para calculo', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='backend.zona')),
            ],
            options={
                'verbose_name': 'historical inmueble',
                'verbose_name_plural': 'historical inmuebles',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]