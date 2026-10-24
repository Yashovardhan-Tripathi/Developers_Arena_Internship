from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated or not user.is_active:
            await self.close(code=4401)
            return
        self.group = f'notifications_{user.pk}'
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        await self.send_json({'type': 'connected'})

    async def disconnect(self, code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    @database_sync_to_async
    def payload(self, pk):
        from .services import visible_notifications
        obj = visible_notifications(self.scope['user']).filter(pk=pk).first()
        if obj:
            return {'type': 'notification', 'id': obj.pk, 'message': f'{obj.actor.username} {obj.verb}'}

    async def notification_message(self, event):
        payload = await self.payload(event['id'])
        if payload:
            await self.send_json(payload)
