# Generated by Django 5.1.2 on 2024-10-19 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conductor',
            name='datos_vehiculo_subidos',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='conductor',
            name='documentos_personales_subidos',
            field=models.BooleanField(default=False),
        ),
    ]
