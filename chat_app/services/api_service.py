import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.base_url = "https://api.openai.com/v1"
    
    def is_configured(self):
        """Check if the API key is configured"""
        return bool(self.api_key)
    
    def get_completion(self, prompt, system_message=None, model="gpt-3.5-turbo"):
        """Get a completion from OpenAI API"""
        if not self.is_configured():
            logger.warning("OpenAI API key not configured")
            return None
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": model,
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            return response_data["choices"][0]["message"]["content"]
        
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return None

# Create a singleton instance
openai_service = OpenAIService()