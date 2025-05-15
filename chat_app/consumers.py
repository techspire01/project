import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage
from .services.chatbot_service import chatbot
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '').strip()
            
            if not message:
                await self.send(text_data=json.dumps({
                    'error': 'Message is required'
                }))
                return
            
            # Process the message (in a synchronous function)
            response_data = await self.process_message(message)
            
            # Save the chat message
            await self.save_chat_message(message, response_data['response'], response_data.get('source'))
            
            # Send response back to WebSocket
            await self.send(text_data=json.dumps({
                'response': response_data['response'],
                'source': response_data.get('source'),
                'timestamp': response_data.get('timestamp', '')
            }))
            
        except Exception as e:
            logger.error(f"Error in WebSocket consumer: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'An error occurred'
            }))
    
    @database_sync_to_async
    def process_message(self, message):
        """Process message using the chatbot service"""
        response_data = chatbot.process_query(message)
        return response_data
    
    @database_sync_to_async
    def save_chat_message(self, user_message, bot_response, source=None):
        """Save chat message to database"""
        chat_message = ChatMessage.objects.create(
            user_message=user_message,
            bot_response=bot_response,
            source=source
        )
        return chat_message