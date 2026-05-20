import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("CONNECT HIT")

        user = self.scope["user"]
        print("USER:", user)

        if user.is_anonymous:
            print("ANONYMOUS")
            await self.close()
            return

        self.group_name = f"user_{user.id}"
        print("GROUP:", self.group_name)

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        print("GROUP JOINED")

        await self.accept()


    async def send_notification(self, event):
        print("NOTIFICATION RECEIVED:", event)

        await self.send(text_data=json.dumps({
            'message': event['message'],
            'msg' : "you are connected to notification channel"
        }))