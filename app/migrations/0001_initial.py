# Generated by Django 5.1.2 on 2024-10-17 02:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('rut', models.CharField(max_length=12, unique=True)),
                ('nombre', models.CharField(default='Desconocido', max_length=30)),
                ('apellido', models.CharField(default='Desconocido', max_length=30)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Apoderado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relacion_alumno', models.CharField(max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Alumno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rut', models.CharField(max_length=12, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(max_length=100)),
                ('apoderado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alumnos', to='app.apoderado')),
            ],
        ),
        migrations.CreateModel(
            name='Conductor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=100, null=True)),
                ('apellido', models.CharField(max_length=100, null=True)),
                ('disponible', models.BooleanField(default=True)),
                ('licencia_conduccion', models.CharField(max_length=20)),
                ('licencia', models.FileField(blank=True, null=True, upload_to='licencias/')),
                ('certificado', models.FileField(blank=True, null=True, upload_to='certificados/')),
                ('apoderados', models.ManyToManyField(related_name='conductor_apoderados', to='app.apoderado')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='apoderado',
            name='conductores',
            field=models.ManyToManyField(related_name='apoderado_conductores', to='app.conductor'),
        ),
        migrations.CreateModel(
            name='Conversacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('participante_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversaciones_participante_1', to=settings.AUTH_USER_MODEL)),
                ('participante_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversaciones_participante_2', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentosPersonales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('licencia', models.FileField(blank=True, null=True, upload_to='documentos_personales/licencia/')),
                ('certificado', models.FileField(blank=True, null=True, upload_to='documentos_personales/certificado/')),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('conductor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos_personales', to='app.conductor')),
            ],
        ),
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('fecha_enviado', models.DateTimeField(auto_now_add=True)),
                ('leido', models.BooleanField(default=False)),
                ('conversacion', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='mensajes', to='app.conversacion')),
                ('destinatario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes_recibidos', to=settings.AUTH_USER_MODEL)),
                ('remitente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes_enviados', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ruta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origen_lat', models.FloatField()),
                ('origen_lon', models.FloatField()),
                ('destino_lat', models.FloatField()),
                ('destino_lon', models.FloatField()),
                ('fecha', models.DateField()),
                ('hora_salida', models.TimeField()),
                ('alumnos', models.ManyToManyField(to='app.alumno')),
                ('conductor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.conductor')),
            ],
        ),
        migrations.CreateModel(
            name='Solicitud',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')], max_length=20)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('apoderado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.apoderado')),
                ('conductor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.conductor')),
            ],
        ),
        migrations.CreateModel(
            name='SolicitudVinculacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')], default='pendiente', max_length=20)),
                ('alumnos', models.ManyToManyField(to='app.alumno')),
                ('apoderado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.apoderado')),
                ('conductor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.conductor')),
            ],
            options={
                'verbose_name': 'Solicitud de Vinculación',
                'verbose_name_plural': 'Solicitudes de Vinculación',
            },
        ),
        migrations.CreateModel(
            name='SubirDumentoImagen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('documento', models.FileField(upload_to='documents/')),
                ('imagen', models.ImageField(upload_to='images/')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('conductor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='app.conductor')),
            ],
            options={
                'db_table': '¨files',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Vehiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marca', models.CharField(max_length=50)),
                ('modelo', models.CharField(max_length=50)),
                ('anio', models.IntegerField()),
                ('patente', models.CharField(max_length=10)),
                ('revision_tecnica', models.FileField(upload_to='documentos_vehiculo/')),
                ('seguro_obligatorio', models.FileField(upload_to='documentos_vehiculo/')),
                ('conductor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehiculos', to='app.conductor')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentosVehiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_documento', models.CharField(choices=[('revision', 'Revisión Técnica'), ('seguro', 'Seguro')], max_length=20)),
                ('archivo', models.FileField(upload_to='documentos_vehiculo/')),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('vehiculo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos_vehiculo', to='app.vehiculo')),
            ],
        ),
        migrations.CreateModel(
            name='Viaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('en_viaje', models.BooleanField(default=False)),
                ('ubicacion', models.JSONField(blank=True, null=True)),
                ('conductor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.conductor')),
            ],
        ),
    ]
