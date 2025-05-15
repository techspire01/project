#from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from .models import ChatMessage
from .services.chatbot_service import chatbot
import logging

logger = logging.getLogger(__name__)

def chat_view(request):
    """Render the chat interface"""
    return render(request, 'chat_app/chat.html')

@csrf_exempt
def chat_message(request):
    """Process incoming chat messages"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            # Get base URL for knowledge fetching
            base_url = request.build_absolute_uri('/')
            
            # Process the message
            response_data = chatbot.process_query(message, base_url)
            
            # Save the message and response
            chat_message = ChatMessage.objects.create(
                user_message=message,
                bot_response=response_data['response'],
                source=response_data.get('source')
            )
            
            return JsonResponse({
                'response': response_data['response'],
                'source': response_data.get('source'),
                'timestamp': chat_message.created_at.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return JsonResponse({'error': 'An error occurred'}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def index_page(request):
    """Add a page to the chatbot's knowledge base"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url', '').strip()
            
            if not url:
                return JsonResponse({'error': 'URL is required'}, status=400)
            
            # Fetch and index the page
            success = chatbot.fetch_content_from_url(url)
            
            if success:
                return JsonResponse({'status': 'success', 'message': 'Page indexed successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Failed to index page'}, status=400)
                
        except Exception as e:
            logger.error(f"Error indexing page: {str(e)}")
            return JsonResponse({'error': 'An error occurred'}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)