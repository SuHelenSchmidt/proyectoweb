# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Mensaje, Apoderado, Conductor
from django.contrib.auth import get_user_model

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f"chat_{self.chat_id}"
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        remitente_id = data['remitente_id']
        destinatario_id = data['destinatario_id']

        remitente = get_user_model().objects.get(id=remitente_id)
        destinatario = get_user_model().objects.get(id=destinatario_id)
        
        # Guarda el mensaje en la base de datos
        mensaje = Mensaje.objects.create(
            remitente=remitente,
            destinatario=destinatario,
            contenido=message,
        )

        # Enviar el mensaje a todos en el grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'remitente': remitente.nombre,
                'fecha': str(mensaje.fecha_enviado)
            }
        )

    async def chat_message(self, event):
        message = event['message']
        remitente = event['remitente']
        fecha = event['fecha']

        await self.send(text_data=json.dumps({
            'message': message,
            'remitente': remitente,
            'fecha': fecha
        }))
