# Generated by Django 4.2 on 2023-09-30 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0142_alter_inmueblepropiedad_tipo_documento_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcelDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('excel_file', models.FileField(upload_to='excel_files/')),
            ],
        ),
    ]
