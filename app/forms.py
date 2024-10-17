from xml.dom.minidom import Document
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Alumno, CustomUser, Conductor, Apoderado, DocumentosPersonales, Ruta, SolicitudVinculacion, SubirDumentoImagen
from .models import Vehiculo  # Asegúrate de tener un modelo para los vehículos


class RegistroConductorForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nombre = forms.CharField(max_length=100, required=True)  # Campo para el nombre
    apellido = forms.CharField(max_length=100, required=True)  # Campo para el apellido
    
    class Meta:
        model = CustomUser
        fields = ('nombre', 'apellido','rut', 'email', 'password1', 'password2')  # Agregar nombre y apellido a los campos

    def save(self, commit=True):
        user = super(RegistroConductorForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Crear el objeto Conductor con nombre y apellido
            conductor = Conductor(user=user, nombre=self.cleaned_data['nombre'], apellido=self.cleaned_data['apellido'])
            conductor.save()
        return user


class RegistroApoderadoForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('rut', 'nombre', 'apellido','email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(RegistroApoderadoForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            apoderado = Apoderado(user=user)  # Eliminamos relacion_alumno
            apoderado.save()
        return user




class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'apellido', 'rut']


        ######



class SolicitudVinculacionForm(forms.ModelForm):
    class Meta:
        model = SolicitudVinculacion
        fields = ['conductor']



class RutaForm(forms.ModelForm):
    class Meta:
        model = Ruta
        fields = ['alumnos', 'origen_lat', 'origen_lon', 'destino_lat', 'destino_lon', 'fecha', 'hora_salida']


class ConductorDocumentosForm(forms.ModelForm):
    class Meta:
        model = DocumentosPersonales
        fields = ['licencia', 'certificado']  # Campos separados para 'licencia' y 'certificado'


class DatosVehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['marca', 'modelo', 'anio', 'patente', 'revision_tecnica', 'seguro_obligatorio']  # Datos del vehículo y sus documentos