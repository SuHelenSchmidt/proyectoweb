from pyexpat.errors import messages
from django.db import models
from django.contrib.auth import get_user_model

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.shortcuts import get_object_or_404, redirect

from proyectoweb import settings
# Gestor de usuario personalizado
class CustomUserManager(BaseUserManager):
    def create_user(self, rut, email, nombre, apellido, password=None, **extra_fields):
        if not rut:
            raise ValueError('El usuario debe tener un RUT')
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        if not nombre:
            raise ValueError('El usuario debe tener un nombre')
        if not apellido:
            raise ValueError('El usuario debe tener un apellido')

        email = self.normalize_email(email)
        user = self.model(rut=rut, email=email, nombre=nombre, apellido=apellido, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, email, nombre, apellido, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(rut, email, nombre, apellido, password, **extra_fields)

# Modelo de usuario personalizado
class CustomUser(AbstractBaseUser):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=30, null=False, default='Desconocido')  # Añade un valor por defecto
    apellido = models.CharField(max_length=30, null=False, default='Desconocido')  # Añade un valor por defecto
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['email', 'nombre', 'apellido']
    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.rut})'

# Modelo Apoderado
class Apoderado(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    relacion_alumno = models.CharField(max_length=50)
    conductores = models.ManyToManyField('Conductor', related_name='apoderado_conductores')  # Cambiado el related_name

    def __str__(self):
        return f"{self.user.rut} - Apoderado"

# Modelo Conductor
class Conductor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, blank=True, null=True)  
    apellido = models.CharField(max_length=100, null=True)
    disponible = models.BooleanField(default=True)  # Eliminar esta línea

    licencia_conduccion = models.CharField(max_length=20)
    licencia = models.FileField(upload_to='licencias/', blank=True, null=True)
    certificado = models.FileField(upload_to='certificados/', blank=True, null=True)
    apoderados = models.ManyToManyField('Apoderado', related_name='conductor_apoderados')  # Cambiado el related_name
    documentos_personales_subidos = models.BooleanField(default=False)
    datos_vehiculo_subidos = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.rut} - Conductor"

# Modelo Alumno
class Alumno(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    apoderado = models.ForeignKey(Apoderado, on_delete=models.CASCADE, related_name='alumnos')

    def __str__(self):
        return self.nombre





###########

class SolicitudVinculacion(models.Model):
    apoderado = models.ForeignKey('Apoderado', on_delete=models.CASCADE)
    conductor = models.ForeignKey('Conductor', on_delete=models.CASCADE)
    alumnos = models.ManyToManyField('Alumno')  # Relación con los alumnos
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Solicitud de {self.apoderado} para {self.conductor} - Estado: {self.estado}"

    class Meta:
        verbose_name = "Solicitud de Vinculación"
        verbose_name_plural = "Solicitudes de Vinculación"
    
# models.py
class Viaje(models.Model):
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE)
    en_viaje = models.BooleanField(default=False)
    ubicacion = models.JSONField(null=True, blank=True)  # o dos campos para latitud y longitud



class Ruta(models.Model):
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE)
    alumnos = models.ManyToManyField(Alumno)
    origen_lat = models.FloatField()  # Latitud del origen
    origen_lon = models.FloatField()  # Longitud del origen
    destino_lat = models.FloatField()  # Latitud del destino
    destino_lon = models.FloatField()  # Longitud del destino
    fecha = models.DateField()
    hora_salida = models.TimeField()

    def __str__(self):
        return f"Ruta de {self.conductor} - {self.fecha} {self.hora_salida}"
    


class SubirDumentoImagen(models.Model):
    documento = models.FileField(upload_to='documents/')
    imagen = models.ImageField(upload_to='images/')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    conductor = models.ForeignKey('Conductor', on_delete=models.CASCADE, related_name='documentos', null=True, blank=True)

    class Meta:
        db_table = "¨files"
        ordering = ['-created_at']


class Vehiculo(models.Model):
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, related_name='vehiculos')
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.IntegerField()
    patente = models.CharField(max_length=10)
    revision_tecnica = models.FileField(upload_to='documentos_vehiculo/')
    seguro_obligatorio = models.FileField(upload_to='documentos_vehiculo/')

    def __str__(self):
        return f"{self.marca} {self.modelo} - Patente: {self.patente}"

class DocumentosPersonales(models.Model):
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, related_name='documentos_personales')
    licencia = models.FileField(upload_to='documentos_personales/licencia/', blank=True, null=True)
    certificado = models.FileField(upload_to='documentos_personales/certificado/', blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Documentos de {self.conductor.nombre}"
class DocumentosVehiculo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='documentos_vehiculo')
    tipo_documento = models.CharField(max_length=20, choices=[('revision', 'Revisión Técnica'), ('seguro', 'Seguro')])
    archivo = models.FileField(upload_to='documentos_vehiculo/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_documento} del vehículo {self.vehiculo.marca} {self.vehiculo.modelo}"


# models.py
class Solicitud(models.Model):
    apoderado = models.ForeignKey(Apoderado, on_delete=models.CASCADE)
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')])
    fecha_creacion = models.DateTimeField(auto_now_add=True)



class Conversacion(models.Model):
    participante_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='conversaciones_participante_1', on_delete=models.CASCADE)
    participante_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='conversaciones_participante_2', on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participante_1} - {self.participante_2}"
# Modelo Mensaje para la comunicación entre conductor y apoderado
class Mensaje(models.Model):
    conversacion = models.ForeignKey(Conversacion, related_name='mensajes', on_delete=models.CASCADE, default=1)  # Cambia '1' por el ID de una conversación válida

    remitente = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='mensajes_recibidos')
    contenido = models.TextField()
    fecha_enviado = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Mensaje de {self.remitente} a {self.destinatario} - {self.contenido[:30]}"
    


class Notificacion(models.Model):
    destinatario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.destinatario}: {self.mensaje} - {'Leída' if self.leida else 'No leída'}"