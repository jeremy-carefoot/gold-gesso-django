import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class AssignmentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        # Only allow authenticated users
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
            
        # Create a unique group for this user
        self.group_name = f"user_{self.user.id}_assignments"
        
        # Join user's assignment group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to assignment updates'
        }))

    async def disconnect(self, close_code):
        # Leave the group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        # Handle messages from WebSocket (if needed)
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        # You can handle different message types here if needed
        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong'
            }))

    # Handler for assignment updates from the channel layer
    async def assignment_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': event['update_type'],
            'data': event.get('data', {}),
            'message': event.get('message', '')
        }))