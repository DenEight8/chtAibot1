import json
from channels.generic.websocket import AsyncWebsocketConsumer

"""Handles WebSocket chat messages and currently echoes user input."""

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg = data.get("message", "")
        # Тут додай логіку: інтеграція з OpenAI або БД
        answer = f"Ви написали: {msg}"  # simple echo for now
        await self.send(text_data=json.dumps({"answer": answer}))
