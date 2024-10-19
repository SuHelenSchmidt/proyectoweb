# views.py
from pyexpat.errors import messages
from django.contrib import messages

from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core import serializers
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    AlumnoForm,
    ConductorDocumentosForm,
    DatosVehiculoForm,
    RegistroConductorForm,
    RegistroApoderadoForm,
  
)
from .models import (
    Alumno,
    Conversacion,
    CustomUser,
    DocumentosPersonales,
    DocumentosVehiculo,
    Mensaje,
    Solicitud,
    SolicitudVinculacion,
    Conductor,
    Apoderado,
    Vehiculo,
)

def home(request):
    # Redirigir según el tipo de usuario
    if request.user.is_authenticated:
        if hasattr(request.user, 'conductor'):
            return redirect('home_conductor')
        elif hasattr(request.user, 'apoderado'):
            return redirect('home_apoderado')
    return render(request, 'app/home.html') 


# Nueva vista para elegir entre conductor o apoderado
def elegir_tipo_registro(request):
    return render(request, 'registration/elegir_tipo_registro.html')
# Vista de registro para conductores
def registro_conductor(request):
    if request.method == 'POST':
        form = RegistroConductorForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('subir_documentos')
    else:
        form = RegistroConductorForm()
    return render(request, 'registration/registro_conductor.html', {'form': form})

# Vista de registro para apoderados
def registro_apoderado(request):
    if request.method == 'POST':
        form = RegistroApoderadoForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('crear_alumno')  # Redirigir a home_apoderado después del registro
    else:
        form = RegistroApoderadoForm()
    return render(request, 'registration/registro_apoderado.html', {'form': form})



class CustomLoginView(LoginView):
    template_name = 'registration/login.html' 
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        if hasattr(self.request.user, 'conductor'):
            return HttpResponseRedirect(reverse('home_conductor'))
        elif hasattr(self.request.user, 'apoderado'):
            # Verificar si el apoderado tiene una solicitud aceptada
            apoderado = self.request.user.apoderado
            solicitud_aceptada = SolicitudVinculacion.objects.filter(apoderado=apoderado, estado='aceptada').exists()
            if solicitud_aceptada:
                return HttpResponseRedirect(reverse('home_apoderado'))
            else:
                return HttpResponseRedirect(reverse('estado_solicitudes'))
        return response

@login_required
@login_required
@login_required
def home_apoderado(request):
    try:
        apoderado = Apoderado.objects.get(user=request.user)
    except Apoderado.DoesNotExist:
        return redirect('registro_apoderado')

    conductores_vinculados = apoderado.conductores.all()
    alumnos = apoderado.alumnos.all()
    alumno_seleccionado = None
    solicitud = None

    if request.method == 'POST':
        alumno_id = request.POST.get('alumno_id')
        alumno_seleccionado = get_object_or_404(Alumno, id=alumno_id)
        solicitud = SolicitudVinculacion.objects.filter(alumnos=alumno_seleccionado, estado='Aceptada').first()

    context = {
        'conductores_vinculados': conductores_vinculados,
        'alumnos': alumnos,
        'alumno_seleccionado': alumno_seleccionado,
        'solicitud': solicitud,
    }
    return render(request, 'apoderado/home_apoderado.html', context)

@login_required
def home_conductor(request):
    conductor = Conductor.objects.get(user=request.user)
    apoderados = conductor.apoderados.all()
    return render(request, 'conductor/home_conductor.html', {
        'conductor': conductor,
        'apoderados': apoderados,
    })

@login_required
def crear_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            alumno.apoderado = request.user.apoderado 
            alumno.save()
            if 'agregar_otro' in request.POST:
                return redirect('crear_alumno')
            else:
                return redirect('buscar_conductor')
    else:
        form = AlumnoForm()
    return render(request, 'apoderado/crear_alumno.html', {'form': form})

@login_required
def buscar_conductor(request):
    conductores = Conductor.objects.filter(disponible=True)
    if request.method == 'POST':
        conductor_id = request.POST.get('conductor_id')
        return redirect('crear_solicitud_vinculacion', conductor_id=conductor_id)
    return render(request, 'apoderado/buscar_conductor.html', {'conductores': conductores})

@login_required
def crear_solicitud_vinculacion(request, conductor_id):
    conductor = get_object_or_404(Conductor, id=conductor_id)
    alumnos = request.user.apoderado.alumnos.all()

    if request.method == 'POST':
        solicitud = SolicitudVinculacion(
            apoderado=request.user.apoderado,
            conductor=conductor,
            estado='Pendiente'
        )
        solicitud.save()  

        alumnos_ids = request.POST.getlist('alumnos_ids')
        for alumno_id in alumnos_ids:
            solicitud.alumnos.add(alumno_id)

        solicitud.save()  
        return redirect('SolicitudesApoderados')

    return render(request, 'apoderado/crear_solicitud_vinculacion.html', {'conductor': conductor, 'alumnos': alumnos})

class Vinculaciones(View):
    def get(self, request):
        conductor = request.user.conductor  
        solicitudes_pendientes = SolicitudVinculacion.objects.filter(conductor=conductor, estado='Pendiente')
        apoderados_aceptados = SolicitudVinculacion.objects.filter(conductor=conductor, estado='Aceptada')
        
        return render(request, 'conductor/vinculaciones.html', {
            'solicitudes_pendientes': solicitudes_pendientes,
            'apoderados_aceptados': apoderados_aceptados
        })
    
    def post(self, request):
        conductor = request.user.conductor
        solicitud_id = request.POST.get('solicitud_id')
        accion = request.POST.get('accion')  # 'aceptar' o 'rechazar'

        solicitud = get_object_or_404(SolicitudVinculacion, id=solicitud_id, conductor=conductor)

        if accion == 'aceptar':
            solicitud.estado = 'Aceptada'
            solicitud.save()
        elif accion == 'rechazar':
            solicitud.estado = 'Rechazada'
            solicitud.save()

        # Mantén la redirección a la misma página de vinculaciones
        return redirect('vinculaciones')

class SolicitudesApoderados(LoginRequiredMixin, View):
    def get(self, request):
        apoderado = request.user.apoderado
        solicitudes = SolicitudVinculacion.objects.filter(apoderado=apoderado)

        # Verificar si el apoderado tiene al menos un alumno aceptado
        tiene_alumno_aceptado = SolicitudVinculacion.objects.filter(
            apoderado=apoderado, 
            estado='Aceptada'  # Asegúrate de que el estado sea coherente aquí
        ).exists()

        # Redirigir al home_apoderado si hay solicitudes pendientes y no hay alumnos aceptados
        if solicitudes.filter(estado='Pendiente').exists() and not tiene_alumno_aceptado:
            return redirect('home_apoderado')

        return render(request, 'apoderado/solicitudes_apoderados.html', {'solicitudes': solicitudes})



@login_required
def ver_conductor_alumno(request):
    if request.method == 'POST':
        alumno_id = request.POST.get('alumno_id')
        alumno = get_object_or_404(Alumno, id=alumno_id)
        solicitud = SolicitudVinculacion.objects.filter(alumnos=alumno, estado='Aceptada').first()

        context = {
            'alumno': alumno,
            'solicitud': solicitud,
        }
        return render(request, 'apoderado/ver_conductor_alumno.html', context)
    return redirect('home_apoderado')  # Redirigir si no es POST
@login_required


def listar_conductores(request):
    conductores = Conductor.objects.all()  # Obtén todos los conductores

    if request.method == 'POST':
        destinatario_id = request.POST.get('destinatario_id')
        contenido = request.POST.get('contenido')

        try:
            destinatario = Conductor.objects.get(id=destinatario_id)
            # Crea el mensaje
            Mensaje.objects.create(remitente=request.user, destinatario=destinatario.user, contenido=contenido)
            messages.success(request, 'Mensaje enviado con éxito.')
        except Conductor.DoesNotExist:
            messages.error(request, 'El conductor no existe.')

    return render(request, 'apoderado/listar_conductores.html', {'conductores': conductores})


@login_required
def gestion_alumnos(request):
    # Lógica para gestionar alumnos
    alumnos = request.user.apoderado.alumnos.all()  # Por ejemplo, obtener los alumnos del apoderado
    return render(request, 'apoderado/gestion_alumnos.html', {'alumnos': alumnos})

def subir_documentos(request):
    if request.method == 'POST':
        form = ConductorDocumentosForm(request.POST, request.FILES)
        if form.is_valid():
            conductor = request.user.conductor  # Asigna el conductor autenticado
            documentos = form.save(commit=False)
            documentos.conductor = conductor  # Asocia los documentos con el conductor
            documentos.save()
            return redirect('subir_datos_vehiculo')  # Redirige a la página para subir datos del vehículo
    else:
        form = ConductorDocumentosForm()
    return render(request, 'conductor/subir_documentos.html', {'form': form})


def subir_datos_vehiculo(request):
    if request.method == 'POST':
        form = DatosVehiculoForm(request.POST, request.FILES)  # Usa DatosVehiculoForm aquí
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.conductor = request.user.conductor
            vehiculo.save()
            return redirect('home_conductor')
    else:
        form = DatosVehiculoForm()  # Usa DatosVehiculoForm aquí también
    return render(request, 'conductor/subir_datos_vehiculo.html', {'form': form})



def gestionar_documentos(request):
    documentos_personales, created = DocumentosPersonales.objects.get_or_create(conductor=request.user.conductor)
    vehiculo = Vehiculo.objects.filter(conductor=request.user.conductor).first()  # Asumiendo que un conductor puede tener un vehículo

    # Manejo de eliminación de documentos
    if request.method == 'POST':
        documento_id = request.POST.get('documento_id')
        if 'eliminar_documento_licencia' in request.POST:
            documentos_personales.licencia.delete()  # Eliminar archivo de licencia
            documentos_personales.licencia = None  # Limpiar campo
            documentos_personales.save()
        elif 'eliminar_documento_certificado' in request.POST:
            documentos_personales.certificado.delete()  # Eliminar archivo de certificado
            documentos_personales.certificado = None  # Limpiar campo
            documentos_personales.save()
        elif 'eliminar_documento_vehiculo' in request.POST:
            # Lógica para eliminar documentos de vehículo, si aplica
            pass

    return render(request, 'conductor/gestionar_documentos.html', {
        'documentos_personales': documentos_personales,
        'vehiculo': vehiculo,
        'documentos_vehiculo': DocumentosVehiculo.objects.filter(vehiculo=vehiculo)
    })




## para q el apoderado pueda ver los datos del conductor
@login_required
def aceptar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudVinculacion, id=solicitud_id, conductor=request.user.conductor)
    
    if request.method == 'POST':
        # Cambia el estado de la solicitud a aceptada
        solicitud.estado = 'Aceptada'
        solicitud.save()
        
        # Aquí podrías implementar la lógica para otorgar permisos al apoderado
        # Por ejemplo, almacenar en la solicitud a qué documentos puede acceder
        # (esto depende de cómo gestiones la visibilidad de documentos)

        return redirect('vinculaciones')  # Redirige a la vista de vinculaciones

    return render(request, 'conductor/aceptar_solicitud.html', {'solicitud': solicitud})


@login_required
def ver_documentos_conductor(request, conductor_id):
    # Obtiene el apoderado y el conductor correspondiente
    apoderado = get_object_or_404(Apoderado, user=request.user)
    conductor = get_object_or_404(Conductor, id=conductor_id)
    
    # Verificar si el apoderado tiene una solicitud aceptada con este conductor
    solicitud_aceptada = SolicitudVinculacion.objects.filter(
        apoderado=apoderado,
        conductor=conductor,
        estado='Aceptada'
    ).exists()
    
    if not solicitud_aceptada:
        # Si no hay solicitud aceptada, redirige o muestra un mensaje
        return redirect('home_apoderado')  # O muestra un mensaje de error

    # Obtener los documentos del conductor
    documentos = DocumentosPersonales.objects.filter(conductor=conductor)

    return render(request, 'apoderado/ver_documentos_conductores.html', {
        'conductor': conductor,
        'documentos': documentos
    })


def chat_view(request, chat_id):
    return render(request, 'mensaje/chat.html', {'chat_id': chat_id, 'user_id': request.user.id})



@login_required
def ver_mensajes(request):
    # Recupera conversaciones donde el usuario actual es parte
    conversaciones = Conversacion.objects.filter(participante_1=request.user) | Conversacion.objects.filter(participante_2=request.user)

    return render(request, 'mensaje/ver_mensajes.html', {
        'conversaciones': conversaciones,
    })

@login_required
def ver_conversacion(request, conversacion_id):
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    
    # Asegúrate de que el usuario es parte de la conversación
    if request.user not in [conversacion.participante_1, conversacion.participante_2]:
        return redirect('ver_mensajes')

    mensajes = Mensaje.objects.filter(conversacion=conversacion).order_by('fecha_enviado')

    # Debug: imprime los mensajes recuperados
    for mensaje in mensajes:
        print(f'Mensaje: {mensaje.contenido}, Remitente: {mensaje.remitente.nombre}, Fecha: {mensaje.fecha_enviado}')

    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        
        # Envía el mensaje
        Mensaje.objects.create(
            remitente=request.user,
            destinatario=conversacion.participante_2 if conversacion.participante_1 == request.user else conversacion.participante_1,
            contenido=contenido,
            conversacion=conversacion
        )
        
        messages.success(request, 'Mensaje enviado con éxito.')
        return redirect('ver_conversacion', conversacion_id=conversacion.id)

    return render(request, 'mensaje/ver_conversacion.html', {
        'conversacion': conversacion,
        'mensajes': mensajes
    })

@login_required
def enviar_mensaje(request):
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        destinatario_id = request.POST.get('destinatario_id')

        # Verifica si el destinatario existe
        try:
            destinatario = CustomUser.objects.get(id=destinatario_id)
        except CustomUser.DoesNotExist:
            messages.error(request, 'El destinatario no existe.')
            return redirect('ver_mensajes')

        # Verifica si ya existe una conversación
        conversacion, created = Conversacion.objects.get_or_create(
            participante_1=request.user,
            participante_2=destinatario
        )

        # Envía el mensaje
        Mensaje.objects.create(
            remitente=request.user,
            destinatario=destinatario,
            contenido=contenido,
            conversacion=conversacion
        )
        messages.success(request, 'Mensaje enviado con éxito.')
        return redirect('ver_conversacion', conversacion_id=conversacion.id)
    
    # Usuarios a los que se puede enviar el mensaje
    if hasattr(request.user, 'apoderado'):
        conductores = Conductor.objects.all()
        context = {'usuarios': conductores}
    elif hasattr(request.user, 'conductor'):
        apoderados_vinculados = request.user.conductor.apoderado_conductores.all()
        context = {'usuarios': apoderados_vinculados}
    
    return render(request, 'mensaje/enviar_mensaje.html', context)


@login_required
def cargar_conversacion(request, conversacion_id):
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    mensajes = Mensaje.objects.filter(conversacion=conversacion).order_by('fecha_enviado')
    
    # Convertir los mensajes a JSON
    data = serializers.serialize('json', mensajes, fields=('remitente', 'contenido', 'fecha_enviado'))
    return JsonResponse({'mensajes': data})