import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.tokens import AccessToken
from .models import Notification

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.token = self.scope['url_route']['kwargs']['token']
        
        logger.info(f"Connecting WebSocket - User ID: {self.user_id}")
        
        # Validate token
        if not self.token:
            logger.error("No token provided")
            await self.close()
            return
        
        try:
            access_token = AccessToken(self.token)
            token_user_id = access_token['user_id']
            logger.info(f"Token validated. Token user_id: {token_user_id}")
            if str(token_user_id) != self.user_id:
                logger.error(f"User ID mismatch: {token_user_id} != {self.user_id}")
                await self.close()
                return
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            await self.close()
            return
        
        self.room_group_name = f'notifications_{self.user_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Joined group {self.room_group_name}")

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notification_message',
                'message': message
            }
        )

    # Receive message from room group
    async def notification_message(self, event):
        message = event['message']
        print(f"Sending to WebSocket: {message}")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))